from abc import ABC, abstractmethod
import hashlib
import os
import time
from key_schedule import expand_key
from Crypto.Random import get_random_bytes

class AESStrategy(ABC):
    def __init__(self, key: bytes, aes_strength: int, block_size: int = 16, debug: bool = False):
        self.debug = debug
        assert block_size == 16, "AES only supports 16-byte blocks (128 bits)"
        assert aes_strength in (128, 192, 256), "AES strength must be 128, 192, or 256 bits"
        self.block_size = block_size
        self.key = self._process_key(key, aes_strength)
        self.used_ivs = set()
        
        start_time= time.time()
        self.round_keys = expand_key(self.key)
        self.key_schedule_time = (time.time() - start_time)*1000 #in ms


    def _process_key(self, key: bytes, aes_strength: int) -> bytes:
        if aes_strength not in (128, 192, 256):
            raise ValueError("AES strength must be 128, 192, or 256 bits")
        hashed = hashlib.sha256(key).digest()
        return hashed[:aes_strength // 8]

    def _generate_unique_random(self) -> bytes:
        while True:
            iv = get_random_bytes(self.block_size)
            if iv not in self.used_ivs:
                self.used_ivs.add(iv)
                return iv
            
	
    def _xor_bytes(self,a: bytes, b: bytes) -> bytes:
        return bytes(x ^ y for x, y in zip(a, b))

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

    def decrypt_bytes(self, encrypted_bytes: bytes) -> bytes:
        return self.decrypt_text(encrypted_bytes)

    @abstractmethod
    def encrypt_text(self, plaintext: bytes) -> bytes:
        pass

    @abstractmethod
    def decrypt_text(self, ciphertext: bytes) -> bytes:
        pass

    def _debug_info(self, extra_info: dict = None):
        if self.debug:
            print(f"[DEBUG] Key: {' '.join(f'{b:02X}' for b in self.key)}")
            print(f"[DEBUG] Block size: {self.block_size}")
            if extra_info:
                for k, v in extra_info.items():
                    print(f"[DEBUG] {k}: {v}")
