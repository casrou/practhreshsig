from genprime import search_safe_prime_single, search_safe_prime_multi, search_safe_prime_sympy, get_safe_prime_openssl
from random import randint
from sympy import sqrt, factorial, jacobi_symbol
from shared import PrimeGenMethod, find_u, evaluate_poly


class Dealer:
    def __init__(self, bitlength, e, prime_gen_method):
        if prime_gen_method is PrimeGenMethod.SINGLEPROCESS:
            p, p_prime = search_safe_prime_single(bitlength)
            q, q_prime = search_safe_prime_single(bitlength)
        elif prime_gen_method is PrimeGenMethod.MULTIPROCESS:
            p, p_prime = search_safe_prime_multi(bitlength)
            q, q_prime = search_safe_prime_multi(bitlength)
        elif prime_gen_method is PrimeGenMethod.SYMPY:
            p, p_prime = search_safe_prime_sympy(bitlength)
            q, q_prime = search_safe_prime_sympy(bitlength)
        else:
            # prime_gen_method is PrimeGenMethod.OPENSSL:
            p, p_prime = get_safe_prime_openssl(bitlength)
            q, q_prime = get_safe_prime_openssl(bitlength)

        assert(p != q)

        self.n = p * q
        self.m = p_prime * q_prime

        self.public_key = (self.n, e)
        self.d = pow(e, -1, self.m)

        self.u = find_u(self.n)
        self.v = random_square(self.n)

    def deal(self, players, k, protocol):
        secret_key_shares = self.compute_secret_key_shares(len(players), k, protocol)

        verification_keys = self.compute_verification_keys_from_key_shares(
            secret_key_shares)

        for i, (p, s_i) in enumerate(zip(players, secret_key_shares)):
            p.receive(i, self.public_key, s_i, self.v, verification_keys)

        return verification_keys

    def compute_secret_key_shares(self, l, k, protocol):
        a_0 = self.d
        a_i = [randint(0, self.m) for x in range(1, k)]
        coefficients = [a_0] + a_i

        # print_poly(coefficients)
        assert(evaluate_poly(coefficients, 0) % self.m == a_0)

        secret_key_shares = protocol.calculate_secret_key_shares(coefficients, l)

        return secret_key_shares

    def compute_verification_keys_from_key_shares(self, secret_key_shares):
        verification_keys = [pow(self.v, share, self.n) for share in secret_key_shares]
        return verification_keys


def print_poly(coeffs):
    """
        Print a readable polynomial corresponding to the given coefficients
    """
    res = "f(X) = "
    for i, c in enumerate(coeffs):
        if i == 0:
            res += "%.4e" % c
        else:
            res += " + %.4ex^%s" % (c, i)
    print(res)


def random_square(upper):
    """
        Return a random square between 1 and given upper-bound
    """
    r = randint(1, int(sqrt(upper)))
    return pow(r, 2)
