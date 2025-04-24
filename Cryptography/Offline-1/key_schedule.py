from BitVector import BitVector
from aes_constants import AES_MODULUS
from aes_constants import S_BOX
from typing import List

def generate_rcon(num_rounds: int) -> list:
    """
    Generate a list of round constants (Rcon) used in AES key expansion.

    Each round constant is a 4-byte word [r, 0x00, 0x00, 0x00],
    where r is an element of GF(2^8) starting from 0x01 and multiplied by 2
    in each round using modular reduction with the AES polynomial.

    :param num_rounds: Number of round constants to generate
    :return: List of 4-byte Rcon words (as lists of integers)
    """
    rcon = []
    r = BitVector(intVal=1, size=8)

    for _ in range(num_rounds):
        rcon.append([int(r), 0x00, 0x00, 0x00])
        r = r.gf_multiply_modular(BitVector(intVal=2), AES_MODULUS, 8)

    return rcon

def substitute_word(word: List[int]) -> List[int]:
    return [S_BOX[b] for b in word]

def rotate_word(word: List[int]) -> List[int]:
    return word[1:] + word[:1]


def expand_key(key: bytes) -> List[List[int]]:
    key_len = len(key)
    assert key_len in (16, 24, 32), "Key must be 128, 192, or 256 bits long"

    num_key_words = key_len // 4                      # Number of 32-bit words in the key
    num_rounds = {4: 10, 6: 12, 8: 14}[num_key_words]         # Rounds
    nb = 4                                 # Always 4 for AES

    key_words = [list(key[i:i+4]) for i in range(0, len(key), 4)]
    rcon = generate_rcon(num_rounds + 1)
    
    for i in range(num_key_words, nb * (num_rounds + 1)):
        temp = key_words[i - 1].copy()
        
        if i % num_key_words == 0:
            temp = substitute_word(rotate_word(temp))
            temp = [t ^ r for t, r in zip(temp, rcon[i // num_key_words - 1])]

        elif num_key_words > 6 and i % num_key_words == 4:
            temp = substitute_word(temp)

        word = [t ^ k for t, k in zip(temp, key_words[i - num_key_words])]
        key_words.append(word)

    return key_words

# 🔧 Test code: Run only when this file is executed directly

# 🔧 Test if this works
if __name__ == "__main__":
    sample_key = b'Thats my Kung Fu'  # AES-128 key
    expanded = expand_key(sample_key)

    print("Expanded Round Keys:")
    for i in range(0, len(expanded), 4):
        block = expanded[i:i+4]
        print(f"Round {i//4}: ", end='')
        for word in block:
            print(' '.join(f"{b:02X}" for b in word), end='  ')
        print() 
