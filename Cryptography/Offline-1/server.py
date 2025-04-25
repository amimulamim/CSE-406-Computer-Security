#simulating Bob
from socket_wrapper import SecureSocketWrapper
from e_curve import EllipticCurve
from ec_point import ECPoint

def main():
    server = SecureSocketWrapper(role='server', port=9999)

    print("\n[SERVER] Starting secure communication...")
    server.start_connection()

    # Step 1: Receive curve and G
    server.exchange_curve_and_generator()
    print("[SERVER] Curve and generator received.")

    # Step 2: Perform ECDH key exchange
    server.establish_shared_key()
    print("[SERVER] Shared AES key established.")

    # Step 3: Receive encrypted message
    message = server.receive_encrypted_text()
    print(f"[SERVER] Received (decrypted): {message.decode()}")

    # Step 4: Send encrypted reply
    reply = b"Hello from Bob (Server)"
    server.send_encrypted_text(reply)
    print(f"[SERVER] Sent (encrypted): {reply.decode()}")

    server.close()
    print("[SERVER] Connection closed.")

if __name__ == "__main__":
    main()
