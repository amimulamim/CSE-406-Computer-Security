from aes_strategy import AESStrategy


class AESCTR(AESStrategy):
	def __init__(self, key: bytes, block_size: int = 16, debug: bool = False):
		from config import aes_key_len
		super().__init__(key, aes_key_len, block_size, debug)

	