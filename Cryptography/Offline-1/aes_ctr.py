from aes_strategy import AESStrategy
from aes_block import AESBlock
from multiprocessing import Pool, cpu_count
from typing import List, Tuple

class AESCTR(AESStrategy):
    def __init__(self, key: bytes, block_size: int = 16, debug: bool = False, parallel: bool = True):
        from settings import aes_key_len  # moved cleanly to avoid circular import
        super().__init__(key, aes_key_len, block_size, debug, parallel)

    def _encrypt_counter(self, counter_block: bytes) -> bytes:
        aes = AESBlock(counter_block)
        aes.encrypt(self.round_keys)
        return aes.get_state_bytes()

    def encrypt_text(self, plaintext: bytes) -> bytes:
        nonce = self._generate_unique_random()[:self.block_size // 2]
        
        ciphertext = b''

        padded = plaintext  # In CTR, no padding needed
        blocks = self._split_blocks(padded)
        counters = [self._create_counter_block(nonce, i) for i in range(len(blocks))]

        if self.parallel:
            encrypted_counters = self._parallel_encrypt_counters(counters)
        else:
            encrypted_counters = [self._encrypt_counter(counter_block) for counter_block in counters]

        for block, enc_counter in zip(blocks, encrypted_counters):
            cipher_block = self._xor_bytes(block, enc_counter)
            ciphertext += cipher_block

        self._debug_info({"Nonce": ' '.join(f'{b:02X}' for b in nonce)})
        return nonce + ciphertext

    def decrypt_text(self, ciphertext: bytes) -> bytes:
        if len(ciphertext) < self.block_size // 2:
            raise ValueError("Ciphertext too short to contain nonce")

        nonce = ciphertext[:self.block_size // 2]
        ciphertext_body = ciphertext[self.block_size // 2:]
        blocks = self._split_blocks(ciphertext_body)
        counters = [self._create_counter_block(nonce, i) for i in range(len(blocks))]

        if self.parallel:
            encrypted_counters = self._parallel_encrypt_counters(counters)
        else:
            encrypted_counters = [self._encrypt_counter(counter_block) for counter_block in counters]

        plaintext = b''
        for block, enc_counter in zip(blocks, encrypted_counters):
            plain_block = self._xor_bytes(block, enc_counter)
            plaintext += plain_block

        self._debug_info({"Nonce": ' '.join(f'{b:02X}' for b in nonce)})
        return plaintext #no unpadding needed in CTR mode

    def _create_counter_block(self, nonce: bytes, counter: int) -> bytes:
        counter_bytes = counter.to_bytes(self.block_size // 2, byteorder='big')
        return nonce + counter_bytes

    def _parallel_encrypt_counters(self, counters: List[bytes]) -> List[bytes]:
        """Encrypt counter blocks in parallel."""
        with Pool(processes=cpu_count()) as pool:
            args = [(counter_block, self.round_keys) for counter_block in counters]
            return pool.map(AESCTR._encrypt_worker_static, args)

    @staticmethod
    def _encrypt_worker_static(args: Tuple[bytes, List[bytes]]) -> bytes:
        counter_block, round_keys = args
        aes = AESBlock(counter_block)
        aes.encrypt(round_keys)
        return aes.get_state_bytes()
