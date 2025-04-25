from e_curve import EllipticCurve

class ECPoint:
    def __init__(self, curve: EllipticCurve, x: int, y: int):
        self.curve = curve
        self.x = x
        self.y = y
        assert self.curve.is_on_curve(x, y), "Point not on curve"

    def __neg__(self):
        return ECPoint(self.curve, self.x, -self.y % self.curve.p)

    def __add__(self, other):
        if self.curve != other.curve:
            raise ValueError("Points not on the same curve")
        if self == other:
            return self.double()
        return self.add(other)

    def double(self):
        p = self.curve.p
        a = self.curve.a
        s = ((3 * self.x ** 2 + a) * pow(2 * self.y, -1, p)) % p #s=(3x^2+a/2y)/y mod p for double function
        x_r = (s ** 2 - 2 * self.x) % p             #x_3=s^2-x_1 -x_2 mod p ,here x_1=x_2
        y_r = (s * (self.x - x_r) - self.y) % p
        return ECPoint(self.curve, x_r, y_r)

    def add(self, other):
        if self.x == other.x and self.y != other.y:
            return None  # Point at infinity
        p = self.curve.p
        s = ((other.y - self.y) * pow(other.x - self.x, -1, p)) % p #s=(y2-y1)/(x2-x1) mod p for add function
        x_r = (s ** 2 - self.x - other.x) % p
        y_r = (s * (self.x - x_r) - self.y) % p
        return ECPoint(self.curve, x_r, y_r)

    def scalar_mul(self, k: int):
        result = None
        addend = self
        while k:
            if k & 1:
                result = addend if result is None else result + addend
            addend = addend + addend
            k >>= 1
        return result
