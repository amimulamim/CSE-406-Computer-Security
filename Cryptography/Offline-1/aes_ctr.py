from aes_strategy import AESStrategy
from aes_block import AESBlock


class AESCTR(AESStrategy):
    def __init__(self, key: bytes, block_size: int = 16, debug: bool = False):
        from settings import aes_key_len  # moved cleanly to avoid circular import
        super().__init__(key, aes_key_len, block_size, debug)



    def _encrypt_counter(self, counter_block: bytes) -> bytes:
        aes = AESBlock(counter_block)
        aes.encrypt(self.round_keys)
        return aes.get_state_bytes()

    def encrypt_text(self, plaintext: bytes) -> bytes:
        nonce = self._generate_unique_random()[:self.block_size // 2]  # 8 bytes if block size is 16
        counter = 0
        ciphertext = b''

        padded = plaintext  # In CTR, no padding needed

        for i in range(0, len(padded), self.block_size):
            block = padded[i:i + self.block_size]
            counter_block = self._create_counter_block(nonce, counter)
            encrypted_counter_nonce = self._encrypt_counter(counter_block)
            cipher_block = self._xor_bytes(block, encrypted_counter_nonce)
            ciphertext += cipher_block
            counter += 1

        self._debug_info({"Nonce": ' '.join(f'{b:02X}' for b in nonce)})
        return nonce + ciphertext

    def decrypt_text(self, ciphertext: bytes) -> bytes:
        if len(ciphertext) < self.block_size // 2:
            raise ValueError("Ciphertext too short to contain nonce")

        nonce = ciphertext[:self.block_size // 2]
        ciphertext = ciphertext[self.block_size // 2:]
        counter = 0
        plaintext = b''

        for i in range(0, len(ciphertext), self.block_size):
            block = ciphertext[i:i + self.block_size]
            counter_block = self._create_counter_block(nonce, counter)
            encrypted_counter_nonce = self._encrypt_counter(counter_block)
            plain_block = self._xor_bytes(block, encrypted_counter_nonce)
            plaintext += plain_block
            counter += 1

        self._debug_info({"Nonce": ' '.join(f'{b:02X}' for b in nonce)})
        return plaintext  # No unpadding needed

    def _create_counter_block(self, nonce: bytes, counter: int) -> bytes:
        counter_bytes = counter.to_bytes(self.block_size // 2, byteorder='big')
        return nonce + counter_bytes  # 8 bytes nonce + 8 bytes counter = 16 bytes block


