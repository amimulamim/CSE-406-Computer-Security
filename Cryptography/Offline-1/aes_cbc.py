
from aes_block import AESBlock
from key_schedule import expand_key
from padding import pad_pkcs7, unpad_pkcs7


from aes_strategy import AESStrategy





class AESCBC(AESStrategy):
    def __init__(self, key: bytes, block_size: int = 16,debug: bool = False):
        from settings import aes_key_len  # Import config inside
        super().__init__(key, aes_key_len, block_size, debug)

    def _encrypt_block(self, block: bytes, prev: bytes) -> bytes:
        xored = self._xor_bytes(block, prev)
        aes = AESBlock(xored)
        aes.encrypt(self.round_keys)
        return aes.get_state_bytes()

    def _decrypt_block(self, block: bytes, prev: bytes) -> bytes:
        aes = AESBlock(block)
        aes.decrypt(self.round_keys)
        decrypted = aes.get_state_bytes()
        return self._xor_bytes(decrypted, prev)

    def encrypt_text(self, plaintext: bytes) -> bytes:
        iv = self._generate_unique_random()
        padded = pad_pkcs7(plaintext, self.block_size)
        ciphertext = b''
        prev = iv
        for i in range(0, len(padded), self.block_size):
            block = padded[i:i + self.block_size]
            encrypted = self._encrypt_block(block, prev)
            ciphertext += encrypted
            prev = encrypted

        self._debug_info({"IV": ' '.join(f'{b:02X}' for b in iv)})
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

        self._debug_info({"IV": ' '.join(f'{b:02X}' for b in iv)})

        return unpad_pkcs7(decrypted)




