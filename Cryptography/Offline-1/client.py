#simulating Alice


from socket_wrapper import SecureSocketWrapper
from e_curve import EllipticCurve
from ec_point import ECPoint
from prime_utils import PrimeUtils

def main():
    print("\n[CLIENT] Initializing elliptic curve and generator...")
    p = PrimeUtils.generate_prime(128)
    a, b = PrimeUtils.random_curve_coefficients(p)
    curve = EllipticCurve(a, b, p)
    gx, gy = curve.find_point_on_curve(strategy="tonelli")
    G = ECPoint(curve, gx, gy)

    print(f"[CLIENT] Curve: y^2 = x^3 + {a}x + {b} (mod {p})")
    print(f"[CLIENT] Generator G: ({gx}, {gy})")

    client = SecureSocketWrapper(role='client', port=9999)

    # Step 1: Connect and send curve + G
    client.start_connection()
    client.exchange_curve_and_generator(curve, G)
    print("[CLIENT] Sent curve and generator.")

    # Step 2: ECDH Key Exchange
    client.establish_shared_key()
    print("[CLIENT] Shared AES key established.")

    # Step 3: Send encrypted message
    msg = b"Hello from Alice (Client)"
    client.send_encrypted_text(msg)
    print(f"[CLIENT] Sent (encrypted): {msg.decode()}")

    # Step 4: Receive encrypted reply
    response = client.receive_encrypted_text()
    print(f"[CLIENT] Received (decrypted): {response.decode()}")

    client.close()
    print("[CLIENT] Connection closed.")

if __name__ == "__main__":
    main()
