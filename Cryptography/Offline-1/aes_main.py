from aes_cbc import AESCBC
from padding import pad_pkcs7
import time
from logger import print_hex_ascii


def main():
    key = b"BUET CSE20 Batch CSE2020"  # 16 bytes = AES-128
    plaintext = b"We need picnic"

    aes = AESCBC(key)

    print("Key:")
    print_hex_ascii(key)

    print("Plain Text:")
    print_hex_ascii( plaintext)
    print("plain text after padding:")
    padded = pad_pkcs7(plaintext, aes.block_size)
    print_hex_ascii( padded)

    start_enc = time.time()
    ciphertext = aes.encrypt_text(plaintext)
    end_enc = time.time()

    print("Ciphered Text:")
    print_hex_ascii(ciphertext)

    start_dec = time.time()
    decrypted = aes.decrypt_text(ciphertext)
    end_dec = time.time()


    print("Deciphered Text:")
    print_hex_ascii( decrypted)

    print("Execution Time Details:")
    print(f"Key Schedule Time: {aes.key_schedule_time:.6f} ms")
    print(f"Encryption Time: {1000 * (end_enc - start_enc):.6f} ms")
    print(f"Decryption Time: {1000 * (end_dec - start_dec):.6f} ms")


if __name__ == "__main__":
    main()
