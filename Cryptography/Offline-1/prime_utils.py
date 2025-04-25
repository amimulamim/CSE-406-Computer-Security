import math
import random
from sympy import isprime, nextprime, mod_inverse, randprime
from typing import Optional, Tuple

class PrimeUtils:
    @staticmethod
    def generate_prime(bits: int) -> int:
        """Generate a random prime number of given bit length."""
        assert bits in (128, 192, 256), "Bit length must be 128, 192, or 256"
        lower = 2 ** (bits - 1)
        upper = 2 ** bits - 1
        return randprime(lower, upper)

    @staticmethod
    def is_prime(n: int) -> bool:
        """Check whether a number is prime."""
        return isprime(n)

    @staticmethod
    def next_prime(n: int) -> int:
        """Get the next prime greater than n."""
        return nextprime(n)

    @staticmethod
    def modinv(a: int, p: int) -> Optional[int]:
        """Compute modular inverse a⁻¹ mod p. Return None if not invertible."""
        try:
            return mod_inverse(a, p)
        except ValueError:
            return None

    @staticmethod
    def random_coprime(p: int) -> int:
        """Find a random number in [2, p-1] that is coprime to p."""
        while True:
            candidate = random.randint(2, p - 1)
            if math.gcd(candidate, p) == 1:
                return candidate

    @staticmethod
    def random_curve_coefficients(p: int) -> Tuple[int, int]:
        """
        Randomly select coefficients a, b ∈ [0, p) such that 4a³ + 27b² ≠ 0 mod p
        This ensures the curve y² = x³ + ax + b is non-singular over F_p.
        """
        while True:
            a = random.randrange(p)
            b = random.randrange(p)
            discriminant = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
            if discriminant != 0:
                return a, b
    
        