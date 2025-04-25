from aes_cbc import AESCBC
from padding import pad_pkcs7
import time

def print_hex_ascii(label, data):
    print(f"{label}:\nIn HEX: {' '.join(f'{b:02X}' for b in data)}")
    print(f"In ASCII: {data.decode(errors='replace')}\n")


def main():
    key = b"BUET CSE20 Batch"  # 16 bytes = AES-128
    plaintext = b"We need picnic"

    aes = AESCBC(key)

    print("Key:")
    print_hex_ascii("In ASCII", key)
    print_hex_ascii("In HEX", key)

    print("Plain Text:")
    print_hex_ascii("In HEX", plaintext)
    padded = pad_pkcs7(plaintext, aes.block_size)
    print_hex_ascii("In ASCII (After Padding)", padded)

    start_enc = time.time()
    ciphertext = aes.encrypt_text(plaintext)
    end_enc = time.time()

    print("Ciphered Text:")
    print_hex_ascii("In HEX", ciphertext)
    print_hex_ascii("In ASCII", ciphertext)

    start_dec = time.time()
    decrypted = aes.decrypt_text(ciphertext)
    end_dec = time.time()


    print("Deciphered Text:")

    print_hex_ascii("After Unpadding", decrypted)

    print("Execution Time Details:")
    print(f"Encryption Time: {1000 * (end_enc - start_enc):.6f} ms")
    print(f"Decryption Time: {1000 * (end_dec - start_dec):.6f} ms")


if __name__ == "__main__":
    main()
