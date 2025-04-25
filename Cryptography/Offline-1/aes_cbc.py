import os
from Crypto.Random import get_random_bytes
from aes_block import AESBlock
from key_schedule import expand_key
from padding import pad_pkcs7, unpad_pkcs7

import hashlib



def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


class AESCBC:
    def __init__(self, key: bytes, block_size: int = 16,debug: bool = False):
        self.debug = debug
        assert len(key) in (16, 24, 32), "Key must be 128, 192, or 256 bits"
        assert block_size == 16, "AES only supports 16-byte blocks (128 bits)"
        self.key = key
        self.block_size = block_size
        self.round_keys = expand_key(key)

    def _encrypt_block(self, block: bytes, prev: bytes) -> bytes:
        xored = xor_bytes(block, prev)
        aes = AESBlock(xored)
        aes.encrypt(self.round_keys)
        return aes.get_state_bytes()

    def _decrypt_block(self, block: bytes, prev: bytes) -> bytes:
        aes = AESBlock(block)
        aes.decrypt(self.round_keys)
        decrypted = aes.get_state_bytes()
        return xor_bytes(decrypted, prev)

    def encrypt_text(self, plaintext: bytes) -> bytes:
        iv = get_random_bytes(self.block_size)
        padded = pad_pkcs7(plaintext, self.block_size)
        ciphertext = b''
        prev = iv
        for i in range(0, len(padded), self.block_size):
            block = padded[i:i + self.block_size]
            encrypted = self._encrypt_block(block, prev)
            ciphertext += encrypted
            prev = encrypted

        self._debug_iv(iv)

        return iv + ciphertext

    def decrypt_text(self, ciphertext: bytes) -> bytes:
        if len(ciphertext) < self.block_size:
            raise ValueError("Ciphertext too short to contain IV")
        iv = ciphertext[:self.block_size]
        ciphertext = ciphertext[self.block_size:]
        decrypted = b''
        prev = iv
        for i in range(0, len(ciphertext), self.block_size):
            block = ciphertext[i:i + self.block_size]
            plain_block = self._decrypt_block(block, prev)
            decrypted += plain_block
            prev = block

        self._debug_iv(iv) 

        return unpad_pkcs7(decrypted)

    def encrypt_file(self, input_path: str, output_path: str):
        with open(input_path, 'rb') as f:
            data = f.read()

        encrypted = self.encrypt_text(data)

        with open(output_path, 'wb') as f:
            f.write(encrypted)

        print(f" Encrypted: {input_path} → {output_path}")

    def decrypt_file(self, input_path: str, output_path: str):
        with open(input_path, 'rb') as f:
            encrypted = f.read()

        decrypted = self.decrypt_text(encrypted)

        with open(output_path, 'wb') as f:
            f.write(decrypted)

        print(f" Decrypted: {input_path} → {output_path}")


        assert len(iv) == self.block_size
        padded = pad_pkcs7(plaintext, self.block_size)
        ciphertext = b''
        prev = iv
        for i in range(0, len(padded), self.block_size):
            block = padded[i:i + self.block_size]
            encrypted = self._encrypt_block(block, prev)
            ciphertext += encrypted
            prev = encrypted
        return iv + ciphertext
    def decrypt_bytes(self, encrypted_bytes: bytes) -> bytes:
        return self.decrypt_text(encrypted_bytes)


  

    def _debug_iv(self, iv: bytes):
        if self.debug:
            print(f"[DEBUG] Key: {' '.join(f'{b:02X}' for b in self.key)}")
            print(f"[DEBUG] IV: {' '.join(f'{b:02X}' for b in iv)}")
            print(f"[DEBUG] Block size: {self.block_size}")
            print(f"[DEBUG] Fingerprint: {hashlib.sha256(self.key).hexdigest()}")
            print("[DEBUG] Round keys:")
            for i in range(0, len(self.round_keys), 4):
                round_words = self.round_keys[i:i+4]
                hex_words = [' '.join(f'{b:02X}' for b in word) for word in round_words]
                print(f"  Round {i//4:2}: {'   '.join(hex_words)}")



