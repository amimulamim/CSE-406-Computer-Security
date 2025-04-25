import time
from ecdh_key_exchange import ECDHKeyExchange
from e_curve import EllipticCurve
from ec_point import ECPoint
from typing import Dict
from prime_utils import PrimeUtils

class ECDHBenchmarkRunner:
    def __init__(self, curve: EllipticCurve, G: ECPoint):
        self.ecdh = ECDHKeyExchange(curve, G)

    def run_benchmark(self):
        print("Running ECDH Benchmark...")
        t0 = time.perf_counter()
        a_priv, a_pub = self.ecdh.generate_keypair()
        tA = time.perf_counter()
        
        print(f"Private Key A: {a_priv}, Public Key A: ({a_pub.x}, {a_pub.y})")

        

        b_priv, b_pub = self.ecdh.generate_keypair()
        tB = time.perf_counter()

        shared_A = self.ecdh.compute_shared_secret(a_priv, b_pub)
        shared_B = self.ecdh.compute_shared_secret(b_priv, a_pub)
        tR = time.perf_counter()
        
        print(f"Private Key B: {b_priv}, Public Key B: ({b_pub.x}, {b_pub.y})")
        print(f"Shared Secret A: ({shared_A.x}, {shared_A.y})")
        print(f"Shared Secret B: ({shared_B.x}, {shared_B.y})")
        

        assert shared_A.x == shared_B.x and shared_A.y == shared_B.y, "Shared secrets do not match"

        return {
            "A": (tA - t0) * 1000,
            "B": (tB - tA) * 1000,
            "R": (tR - tB) * 1000
        }
    
def run_trials(bit_size: int, trials: int = 5, strategy='euler'):
    p = PrimeUtils.generate_prime(bit_size)
    a, b = PrimeUtils.random_curve_coefficients(p)
    curve = EllipticCurve(a, b, p)
    Gx, Gy = curve.find_point_on_curve(strategy)
    G = ECPoint(curve, Gx, Gy)

    runner = ECDHBenchmarkRunner(curve, G)
    times = {"A": 0, "B": 0, "R": 0}
    for _ in range(trials):
        result = runner.run_benchmark()
        for k in times:
            times[k] += result[k]

    print(f"\nResults for {bit_size}-bit prime:")
    for k in times:
        print(f"{k} Avg Time: {times[k] / trials:.3f} ms")

if __name__ == "__main__":
    bit_sizes = [128, 192, 256]
    trials = 5
    for bit_size in bit_sizes:
      run_trials(bit_size, trials)
