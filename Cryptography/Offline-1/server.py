# server.py
import time
from socket_wrapper import SecureSocketWrapper
from prime_utils import PrimeUtils
from e_curve import EllipticCurve
from ec_point import ECPoint
from config import aes_key_len

def main():
    server = SecureSocketWrapper(role='server', host='127.0.0.1', port=9999,aes_bit=aes_key_len)

    server.start_connection()

    # Step 1: Exchange curve and generator
    print("[SERVER] Waiting for curve and generator...")
    server.exchange_curve_and_generator()

    # Step 2: ECDH shared key
    print("[SERVER] Establishing shared key...")
    server.establish_shared_key()
    print("[SERVER] Shared AES key established.")

    # Step 3: Start receiver thread
    server.start_receiver()

    # Step 4: Sending loop
    try:
        while True:
            msg = input("[SERVER] Enter message (or 'send <filename>' or 'close'): ").strip()
            if not msg:
                continue

            if msg.lower() == 'close':
                print("[SERVER] Closing connection...")
                break

            if msg.lower().startswith('send '):
                # Send file
                filename = msg[5:].strip()
                if filename:
                    server.send_encrypted_file(filename)
                else:
                    print("[SERVER] Please specify a filename after 'send'.")
            else:
                # Send normal text message
                server.send_encrypted_text(msg.encode())

    except KeyboardInterrupt:
        print("\n[SERVER] Interrupted by user.")

    finally:
        server.close()

if __name__ == "__main__":
    main()
