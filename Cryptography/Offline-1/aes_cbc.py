
from aes_block import AESBlock
from padding import pad_pkcs7, unpad_pkcs7


from aes_strategy import AESStrategy
from typing import Tuple, List
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count,Pool




class AESCBC(AESStrategy):
    def __init__(self, key: bytes, block_size: int = 16,debug: bool = False,parallel: bool = True):
        from settings import aes_key_len  # Import config inside
        super().__init__(key, aes_key_len, block_size, debug, parallel)

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


    
    def _decrypt_single(self, args: Tuple[bytes, bytes]) -> bytes:
        block, prev = args
        return self._decrypt_block(block, prev)

    def decrypt_text(self, ciphertext: bytes) -> bytes:
        if len(ciphertext) < self.block_size:
            raise ValueError("Ciphertext too short to contain IV")
        
        iv = ciphertext[:self.block_size]
        ciphertext_body = ciphertext[self.block_size:]
        blocks = self._split_blocks(ciphertext_body)
        prev_blocks = [iv] + blocks[:-1]  # previous block for each block
        
        if self.parallel:
            decrypted_blocks = self._parallel_decrypt(blocks, prev_blocks)
        else:
            decrypted_blocks = self._sequential_decrypt(blocks, prev_blocks)

        plaintext_padded = b''.join(decrypted_blocks)

        self._debug_info({"IV": ' '.join(f'{b:02X}' for b in iv)})
        return unpad_pkcs7(plaintext_padded)

    def _sequential_decrypt(self, blocks: List[bytes], prev_blocks: List[bytes]) -> List[bytes]:
        return [self._decrypt_single((block, prev)) for block, prev in zip(blocks, prev_blocks)]

    def _parallel_decrypt(self, blocks: List[bytes], prev_blocks: List[bytes]) -> List[bytes]:
        round_keys = self.round_keys  # Expand only once, reuse
        with Pool(processes=cpu_count()) as pool:
            args = [(block, prev, round_keys) for block, prev in zip(blocks, prev_blocks)]
            results = pool.map(AESCBC._decrypt_worker_static, args)
        return results
    
    
    @staticmethod
    def _decrypt_worker_static(args: Tuple[bytes, bytes, List[bytes]]) -> bytes:
        block, prev, round_keys = args
        aes = AESBlock(block)
        aes.decrypt(round_keys)
        decrypted = aes.get_state_bytes()
        return bytes(a ^ b for a, b in zip(decrypted, prev))






