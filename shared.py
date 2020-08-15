from enum import Enum, IntEnum
from random import randint
from sympy import jacobi_symbol


def powmod(base, exp, mod):
    base, exp, mod = int(base), int(exp), int(mod)
    return pow(base, exp, mod)


def _divmod(x, y, mod):
    temp = pow(y, -1, mod)
    return (x * temp) % mod


def H(message, n):
    import hashlib
    return int(hashlib.sha256(message.encode('utf-8')).hexdigest(), 16) % n


def find_u(n):
    u = None
    while u is None:
        temp = randint(0, n)
        if jacobi_symbol(temp, n) == -1:
            u = temp
    return u


# Secondary security parameter. 128 suggested in paper.
L_1 = 128


def H_prime(**values):
    c = H(str(values), L_1)
    return c


def evaluate_poly(coeffs, point):
    n, res = 0, 0
    for c in coeffs:
        res = res + (c * pow(point, n))
        n += 1
    return res


class PrimeGenMethod(Enum):
    SINGLEPROCESS = "SINGLEPROCESS"
    MULTIPROCESS = "MULTIPROCESS"
    SYMPY = "SYMPY"
    OPENSSL = "OPENSSL"

    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self)


class LogLevel(IntEnum):
    NONE = 0
    DEFAULT = 1
    VERBOSE = 2
    # DEBUG = 3

    def __str__(self):
        return self.name
