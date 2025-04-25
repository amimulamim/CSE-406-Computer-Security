import socket
import pickle
import threading
import os
from typing import Union
from aes_cbc import AESCBC
from ecdh_key_exchange import ECDHKeyExchange
from e_curve import EllipticCurve
from ec_point import ECPoint

class SecureSocketWrapper:
    def __init__(self, role: str, host: str = '127.0.0.1', port: int = 9999,aes_byte_length: int = 16):
        self.role = role.lower()  # 'client' or 'server'
        self.host = host
        self.port = port
        self.conn = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.shared_key = None
        self.aes: Union[AESCBC, None] = None
        self.curve: Union[EllipticCurve, None] = None
        self.G: Union[ECPoint, None] = None
        self.ecdh: Union[ECDHKeyExchange, None] = None
        self.running = True  # For controlling background receiver thread
        self.receiver_thread = None
        self.aes_byte_length = aes_byte_length
        if self.aes_byte_length not in (16, 24, 32):
         raise ValueError("AES key must be 128, 192, or 256 bits (16, 24, or 32 bytes).")

        self.folder = "server_files" if self.role == 'server' else "client_files"
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def start_connection(self):
        if self.role == 'server':
            self.sock.bind((self.host, self.port))
            self.sock.listen(1)
            print(f"[SERVER] Listening on {self.host}:{self.port}...")
            self.conn, _ = self.sock.accept()
            print(f"[SERVER] Connection accepted.")
        else:
            self.sock.connect((self.host, self.port))
            self.conn = self.sock
            print(f"[CLIENT] Connected to {self.host}:{self.port}")

    def start_receiver(self):
        self.receiver_thread = threading.Thread(target=self.receive_loop, daemon=True)
        self.receiver_thread.start()

    def close(self):
        self.running = False
        if self.conn:
            self.conn.close()
        self.sock.close()
        print(f"[{self.role.upper()}] Connection closed.")

    # ------------- Data Transfer ----------------
    def send_data(self, data):
        serialized = pickle.dumps(data)
        self.conn.sendall(len(serialized).to_bytes(4, 'big') + serialized)

    def receive_data(self):
        length = int.from_bytes(self._recv_exact(4), 'big')
        return pickle.loads(self._recv_exact(length))

    def _recv_exact(self, n: int) -> bytes:
        data = b''
        while len(data) < n:
            packet = self.conn.recv(n - len(data))
            if not packet:
                raise ConnectionError("Connection lost")
            data += packet
        return data

    # ------------- ECDH Exchange ----------------
    def exchange_curve_and_generator(self, curve: EllipticCurve = None, G: ECPoint = None):
        if self.role == 'server':
            a, b, p, gx, gy = self.receive_data()
            self.curve = EllipticCurve(a, b, p)
            self.G = ECPoint(self.curve, gx, gy)
            self.send_data("[ACK]")
        else:
            self.send_data((curve.a, curve.b, curve.p, G.x, G.y))
            ack = self.receive_data()
            assert ack == "[ACK]"
            self.curve = curve
            self.G = G

    def establish_shared_key(self):
        self.ecdh = ECDHKeyExchange(self.curve, self.G)
        priv, pub = self.ecdh.generate_keypair()
        self.send_data((pub.x, pub.y))
        peer_x, peer_y = self.receive_data()
        peer_pub = ECPoint(self.curve, peer_x, peer_y)
        shared = self.ecdh.compute_shared_secret(priv, peer_pub)
        self.shared_key = shared.x.to_bytes(32, 'big')[:self.aes_byte_length]
        self.aes = AESCBC(self.shared_key)

    # ------------- Sending Text/File (Encrypted) ----------------
    def send_encrypted_text(self, plaintext: bytes):
        ciphertext = self.aes.encrypt_text(plaintext)
        self.send_data({"type": "text", "data": ciphertext})


    
    def send_encrypted_file(self, filename: str):
        print(f"[{self.role.upper()}] Sending file '{filename}'...")
        path = os.path.join(self.folder, filename)
        if not os.path.isfile(path):
            print(f"[{self.role.upper()}] File '{filename}' not found in {self.folder}/")
            return
        print(f"[{self.role.upper()}] File '{filename}' found. Reading...")
        with open(path, 'rb') as f:
            file_data = f.read()
        print(f"[{self.role.upper()}] File '{filename}' read successfully. Encrypting...")
        print(f"[{self.role.upper()}] File size: {len(file_data)} bytes")
        print("data: ", file_data[:10], "...")
        payload = {"type": "file", "filename": filename, "data": self.aes.encrypt_text(file_data)}
        print(f"[{self.role.upper()}] File '{filename}' encrypted successfully. Sending...")    
        self.send_data(payload)
        print(f"[{self.role.upper()}] File '{filename}' sent successfully.")

    def receive_text(self, ciphertext: bytes):
        plaintext = self.aes.decrypt_text(ciphertext)
        print(f"\n[{self.role.upper()} RECEIVED TEXT]: {plaintext.decode()}")

    def receive_file(self, filename: str, ciphertext: bytes):
        raw = self.aes.decrypt_text(ciphertext)

        save_path = os.path.join(self.folder, filename)
        if  os.path.exists(save_path):
            print(f"[{self.role.upper()}] File '{filename}' already exists. Overwriting.")
        else:
            print(f"[{self.role.upper()}] File '{filename}' received.")
            with open(save_path, 'wb') as f:
                f.write(raw)
            print(f"\n[{self.role.upper()} RECEIVED FILE]: Saved as {save_path}")    


    # ------------- Background Receiver Loop ----------------
    def receive_loop(self):
        while self.running:
            try:
                incoming = self.receive_data()
                if not incoming:
                    continue

                if isinstance(incoming, dict):
                    data_type = incoming.get("type")

                    if data_type == "text":
                        self.receive_text(incoming["data"])

                    elif data_type == "file":
                        filename = incoming.get("filename")
                        ciphertext = incoming.get("data")
                        self.receive_file(filename, ciphertext)

                    else:
                        print(f"[{self.role.upper()} WARNING]: Unknown data type received.")

                else:
                    print(f"[{self.role.upper()} WARNING]: Received unexpected data format.")

            except (ConnectionError, OSError):
                print(f"[{self.role.upper()} WARNING]: Connection closed.")
                self.running = False
                break
            except Exception as e:
                print(f"[{self.role.upper()} ERROR]: {e}")
                self.running = False
                break
