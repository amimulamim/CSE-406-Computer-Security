import time
from random import randint
from e_curve import EllipticCurve
from ec_point import ECPoint
from typing import Tuple


class ECDHKeyExchange:
    def __init__(self, curve: EllipticCurve, generator_point: ECPoint):
        self.curve = curve               #  shared elliptic curve E
        self.generator_point = generator_point  #  public generator point G,a point on E,(x,y)∈E
    
    def generate_keypair(self) -> Tuple[int, ECPoint]:
        private_key = randint(1, self.curve.p - 1)   #  K_a or K_b ,is a random integer in the range [1, p-1]
        public_key = self.generator_point.scalar_mul(private_key)  #  A = K_a·G is the public key or is B = K_b·G
        return private_key, public_key
    
    def compute_shared_secret(self, priv: int, pub: ECPoint) -> ECPoint:
        return pub.scalar_mul(priv)   #  R = K_a · B or K_b · A

		

        
	
