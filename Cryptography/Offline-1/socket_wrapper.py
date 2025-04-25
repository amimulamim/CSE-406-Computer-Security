import socket
import pickle
from typing import Union
from aes_cbc import AESCBC
from ecdh_key_exchange import ECDHKeyExchange
from e_curve import EllipticCurve
from ec_point import ECPoint


class SecureSocketWrapper:
    def __init__(self, role: str, host: str = '127.0.0.1', port: int = 9999):
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

    def close(self):
        if self.conn:
            self.conn.close()
        self.sock.close()

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
        self.shared_key = shared.x.to_bytes(16, 'big')[:16]
        self.aes = AESCBC(self.shared_key)

    # ------------- Encrypted Text/File Transfer ----------------
    def send_encrypted_text(self, plaintext: bytes):
        ciphertext = self.aes.encrypt_text(plaintext)
        self.send_data(ciphertext)

    def receive_encrypted_text(self) -> bytes:
        return self.aes.decrypt_text(self.receive_data())

    def send_encrypted_file(self, file_path: str):
        with open(file_path, 'rb') as f:
            raw = f.read()
        self.send_data(self.aes.encrypt_text(raw))

    def receive_encrypted_file(self, save_path: str):
        decrypted = self.aes.decrypt_text(self.receive_data())
        with open(save_path, 'wb') as f:
            f.write(decrypted)
