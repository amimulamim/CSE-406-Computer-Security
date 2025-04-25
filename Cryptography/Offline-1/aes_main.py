
import time
import os
from aes_block import AESBlock
from key_schedule import expand_key
from padding import pad_pkcs7, unpad_pkcs7

def print_bytes(label, data: bytes):
    print(f"{label}:\nIn HEX: {' '.join(f'{b:02X}' for b in data)}")
    print(f"In ASCII: {data.decode(errors='replace')}\n")