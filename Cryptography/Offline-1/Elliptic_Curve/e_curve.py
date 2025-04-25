from prime_utils import PrimeUtils
from random import randint
from typing import Optional, Tuple
from math import isqrt

class EllipticCurve:
    def __init__(self, a: int, b: int, p: int):
        assert PrimeUtils.is_prime(p), "Modulus p must be a prime number."
        self.a = a
        self.b = b
        self.p = p
        self._check_nonsingular()

    def _check_nonsingular(self):
        # Ensure the curve is non-singular: 4a^3 + 27b^2 != 0 (mod p)
        if (4 * pow(self.a, 3, self.p) + 27 * pow(self.b, 2, self.p)) % self.p == 0:
            raise ValueError("Singular curve: 4a^3 + 27b^2 ≡ 0 (mod p)")

    def is_on_curve(self, x: int, y: int) -> bool:
        return (y * y - (x ** 3 + self.a * x + self.b)) % self.p == 0

    def euler_criterion(self, a: int) -> bool:
        return pow(a, (self.p - 1) // 2, self.p) == 1

    def tonelli_shanks(self, a: int) -> Optional[int]:
        """Compute sqrt(a) mod p using Tonelli-Shanks algorithm."""
        if not self.euler_criterion(a):
            return None

        if self.p % 4 == 3:
            return pow(a, (self.p + 1) // 4, self.p)

        # Find Q and S such that p-1 = Q * 2^S with Q odd
        q, s = self.p - 1, 0
        while q % 2 == 0:
            q //= 2
            s += 1

        # Find z such that (z | p) = -1 (i.e., z is non-residue mod p)
        z = 2
        while self.euler_criterion(z):
            z += 1

        m, c, t, r = s, pow(z, q, self.p), pow(a, q, self.p), pow(a, (q + 1) // 2, self.p)

        while t != 1:
            i, temp = 1, pow(t, 2, self.p)
            while temp != 1:
                temp = pow(temp, 2, self.p)
                i += 1
                if i == m:
                    return None
            b = pow(c, 2 ** (m - i - 1), self.p)
            m, c, t, r = i, pow(b, 2, self.p), (t * b * b) % self.p, (r * b) % self.p

        return r

    def find_point_on_curve(self, strategy: str = 'euler') -> Tuple[int, int]:
        """
        Find a point (x, y) on the elliptic curve using either:
        - 'euler': uses Euler Criterion (fast for p ≡ 3 mod 4)
        - 'tonelli': uses Tonelli–Shanks (works for all odd primes)
        """
        while True:
            x = randint(0, self.p - 1)
            rhs = (x ** 3 + self.a * x + self.b) % self.p

            if strategy == 'euler':
                if self.p % 4 != 3:
                    continue  # not safe to use Euler method
                if self.euler_criterion(rhs):
                    y = pow(rhs, (self.p + 1) // 4, self.p)
                    if self.is_on_curve(x, y):
                        return x, y
                strategy = 'tonelli'
            # If Euler fails or we are using Tonelli

            elif strategy == 'tonelli':
                y = self.tonelli_shanks(rhs)
                if y and self.is_on_curve(x, y):
                    return x, y

            else:
                raise ValueError("Unknown strategy. Use 'euler' or 'tonelli'.")
