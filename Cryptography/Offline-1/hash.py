import hashlib

def normalize_key(user_key: str, bits=128) -> bytes:
    assert bits in (128, 192, 256)
    if len(user_key.encode()) == bits // 8:
        return user_key.encode()
    return hashlib.sha256(user_key.encode()).digest()[:bits // 8]
