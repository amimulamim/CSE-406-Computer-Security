from aes_constants import S_BOX,INV_S_BOX, MIXER, INV_MIXER, AES_MODULUS
from typing import List
from BitVector import BitVector


class AESBlock:
    def __init__(self, input_block: bytes):
        assert len(input_block) == 16, "Input block must be 16 bytes"
        # AES state is 4x4 matrix: state[column][row]
        #here [col][row] is used to access a byte instead of [row][col] because
        #the words are stored in column-major order
        self.state = [[input_block[row + 4 * col] for row in range(4)] for col in range(4)]

    def add_round_key(self, round_key: List[List[int]]):
        """XOR each byte of the state with the round key"""
        for col in range(4):
            for row in range(4):
                self.state[col][row] ^= round_key[col][row]

    def sub_bytes(self):
        """Apply the S-box to each byte in the state"""
        for col in range(4):
            for row in range(4):
                self.state[col][row] = S_BOX[self.state[col][row]]
                
    def inverse_sub_bytes(self):
        """Apply the inverse S-box to each byte in the state"""
        for col in range(4):
            for row in range(4):
                self.state[col][row] = INV_S_BOX[self.state[col][row]]
    


    def shift_rows(self):
        """Left rotate each row by its index"""
        rows = [[self.state[col][row] for col in range(4)] for row in range(4)]
        for r in range(1, 4):
            rows[r] = rows[r][r:] + rows[r][:r]
        for col in range(4):
            for row in range(4):
                self.state[col][row] = rows[row][col]

    def inverse_shift_rows(self):
        """Right rotate each row by its index"""
        rows = [[self.state[col][row] for col in range(4)] for row in range(4)]
        for r in range(1, 4):
            rows[r] = rows[r][-r:] + rows[r][:-r]
        for col in range(4):
            for row in range(4):
                self.state[col][row] = rows[row][col]

    #private method         
    def _apply_matrix(self, matrix: List[List[BitVector]]):
        """Apply a matrix transformation to the state"""
        """The use of _ is to indicate that this is a private method"""
        for c in range(4):
            col = [BitVector(intVal=self.state[c][r], size=8) for r in range(4)]
            result = [0] * 4
            for r in range(4):
                acc = BitVector(intVal=0, size=8)
                for k in range(4):
                    acc ^= matrix[r][k].gf_multiply_modular(col[k], AES_MODULUS, 8)
                result[r] = int(acc)
            for r in range(4):
                self.state[c][r] = result[r]


    def mix_columns(self):
        """Apply MixColumns transformation to each column of the state"""
        self._apply_matrix(MIXER)
                
    def inverse_mix_columns(self):
        """Apply inverse MixColumns transformation to each column of the state"""
        self._apply_matrix(INV_MIXER)

    def get_state_bytes(self) -> bytes:
        """Flatten state into a 16-byte block (row-major order)"""
        return bytes(self.state[col][row] for col in range(4) for row in range(4))

    @staticmethod
    def flatten_round_key(key_words: List[List[int]], round_index: int) -> List[List[int]]:
        """Return the 4x4 round key matrix for the given round index"""
        start = round_index * 4
        return key_words[start:start + 4]

    def encrypt(self, round_keys: List[List[int]]):
        
        num_rounds = (len(round_keys) // 4) - 1

        # Initial round
        self.add_round_key(self.flatten_round_key(round_keys, 0))

        # Main rounds
        for r in range(1, num_rounds):
            self.sub_bytes()
            self.shift_rows()
            self.mix_columns()
            self.add_round_key(self.flatten_round_key(round_keys, r))

        # Final round (no MixColumns)
        self.sub_bytes()
        self.shift_rows()
        self.add_round_key(self.flatten_round_key(round_keys, num_rounds))

    def decrypt(self, round_keys: List[List[int]]):
        num_rounds = (len(round_keys) // 4) - 1

        # Initial round
        self.add_round_key(self.flatten_round_key(round_keys, num_rounds))

        # Main rounds
        for r in range(num_rounds - 1, 0, -1):
            self.inverse_shift_rows()
            self.inverse_sub_bytes()
            self.add_round_key(self.flatten_round_key(round_keys, r))
            self.inverse_mix_columns()

        # Final round (no MixColumns)
        self.inverse_shift_rows()
        self.inverse_sub_bytes()
        self.add_round_key(self.flatten_round_key(round_keys, 0))
