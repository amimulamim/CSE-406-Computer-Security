# client.py
import time
from socket_wrapper import SecureSocketWrapper
from prime_utils import PrimeUtils
from e_curve import EllipticCurve
from ec_point import ECPoint

def main():
    print("[CLIENT] Starting...")
    client = SecureSocketWrapper(role='client', host='127.0.0.1', port=9999)

    client.start_connection()

    # Step 1: Generate and send curve and generator
    print("[CLIENT] Generating curve and point...")
    p = PrimeUtils.generate_prime(128)  # or 192/256 for more security
    a, b = PrimeUtils.random_curve_coefficients(p)
    curve = EllipticCurve(a, b, p)
    Gx, Gy = curve.find_point_on_curve(strategy='tonelli')  # or 'euler'
    G = ECPoint(curve, Gx, Gy)
    print(f"[CLIENT] Curve: y² = x³ + {a}x + {b} mod {p}")
    print(f"[CLIENT] Generator Point G: ({Gx}, {Gy})")

    client.exchange_curve_and_generator(curve, G)

    # Step 2: ECDH shared key
    print("[CLIENT] Establishing shared key...")
    client.establish_shared_key()
    print("[CLIENT] Shared AES key established.")

    # Step 3: Start receiver thread
    client.start_receiver()

    # Step 4: Sending loop
    try:
        while True:
            msg = input("[CLIENT] Enter message (or 'send <filename>' or 'close'): ").strip()
            if not msg:
                continue

            if msg.lower() == 'close':
                print("[CLIENT] Closing connection...")
                break

            if msg.lower().startswith('send '):
                filename = msg[5:].strip()
                if filename:
                    client.send_encrypted_file_command(filename)
                else:
                    print("[CLIENT] Please specify a filename after 'send'.")
            else:
                client.send_encrypted_text(msg.encode())

    except KeyboardInterrupt:
        print("\n[CLIENT] Interrupted by user.")

    finally:
        client.close()

if __name__ == "__main__":
    main()
