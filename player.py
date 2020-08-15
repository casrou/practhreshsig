from shared import powmod, H, H_prime, L_1
from random import randint
from sympy import jacobi_symbol


class Player:
    def receive(self, index, public_key, secret_key_share, v, verification_keys):
        self.i = index
        self.n, self.e = public_key
        self.s_i = secret_key_share
        self.v = v
        self.vks = verification_keys

    def generate_signature_share(self, delta, protocol):
        x = protocol.get_hashed_message()
        x_i = protocol.calculate_share(x, self.s_i)

        proof_of_correctness = compute_proof_of_correctness(
            self.n, self.v, x, delta, self.s_i, self.vks[self.i], x_i, protocol)
        return x_i, proof_of_correctness


def compute_proof_of_correctness(n, v, x, delta, s_i, v_i, x_i, protocol):
    x_tilde = protocol.calculate_x_tilde(x)
    r = randint(0, pow(2, n.bit_length() + (2*L_1) - 1))
    v_prime = powmod(v, r, n)
    x_prime = powmod(x_tilde, r, n)
    c = H_prime(v=v, x_tilde=x_tilde, v_i=v_i, x_i2=powmod(x_i, 2, n),
                v_prime=v_prime, x_prime=x_prime)
    z = s_i * c + r
    return (z, c)
