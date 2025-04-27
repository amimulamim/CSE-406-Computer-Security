
#using CBC with PKCS7 padding

from logger import print_hex_ascii

def pad_pkcs7(data: bytes, block_size: int = 16) -> bytes:
	pad_length = block_size - (len(data) % block_size)
	padding = bytes([pad_length] * pad_length)

	print_hex_ascii(data + padding, "after padding")


	return data + padding

def unpad_pkcs7(data: bytes) -> bytes:
	if not data:
		return data
	pad_length = data[-1]

	if pad_length < 1 or pad_length > 16:
		raise ValueError("Invalid padding length")
	if data[-pad_length:] != bytes([pad_length] * pad_length):
		raise ValueError("Invalid padding")
	
	print_hex_ascii(data, "before unpadding")
	print_hex_ascii(data[:-pad_length], "after unpadding")
	
	return data[:-pad_length]
