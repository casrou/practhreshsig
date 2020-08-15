from sys import version_info
import argparse
from sympy import factorial, jacobi_symbol
from random import randint
from dealer import Dealer
from player import Player
from shared import powmod, H, H_prime, L_1, PrimeGenMethod, LogLevel, _divmod
from protocol import Protocol1, Protocol2

global loglevel
loglevel = None


def main(args=None):
    assert version_info.major == 3 and version_info.minor == 8, "Ensure python version (= 3.8)"

    """ SETUP """
    if args is None:
        args = parse_args()

    global loglevel
    loglevel = LogLevel[args.log]

    l, k, t = args.l, args.k, args.t
    log(f"Participating players: {l}, Number of collaborating players (Quorom size): {k}, Maximum number of corrupt players: {t}")

    assert l >= t + \
        k, ("total number of participating players has to be larger than number of collaborating players and corrupt players combined")
    assert k >= t + \
        1, ("the minimum requried number of collaborating parties has to be at least one larger than the maximum number of corrupt parties")

    primegen_method = args.primegen
    log(f"Prime generation method: {primegen_method}")

    """ 
        THE DEALER 

        Generates safe primes for the public key modulus.
        Deals secret key shares and verification key shares.
    """

    bitlength = args.bitlength
    log(f"Bitlength of primes: {bitlength}")

    # the fourth Fermat number - basically just a large number known to be prime
    e = pow(2, pow(2, 4)) + 1
    assert e > l, "e has to be a prime larger than number of players"

    players = [Player() for _ in range(l)]

    dealer = Dealer(bitlength, e, primegen_method)

    # Shared values
    n, e = dealer.public_key
    v, u, m = dealer.v, dealer.u, dealer.m

    log(f"Bitlength of modulus: {n.bit_length()}")

    message = args.message
    log(f"message: {message}", LogLevel.VERBOSE)

    delta = factorial(l)

    protocol = None
    if k == t + 1:
        log("Protocol 1")
        protocol = Protocol1(message=message, n=n, delta=delta, m=m)
    else:
        # k > t + 1:
        log("Protocol 2")
        protocol = Protocol2(message=message, n=n, delta=delta, m=m, u=u, e=e)

    vks = dealer.deal(players, k, protocol)

    # Dealer is no longer used
    del dealer

    # Hashed message
    x = protocol.get_hashed_message()
    log(f"hashed message: {x}", LogLevel.VERBOSE)

    """ 
        COMBINING SHARES 
        
        Combines signature shares to get a signature.
        We simulate that we receive generated signature shares from k players.
    """

    from random import sample
    S = sample(range(1, l + 1), k)

    log(f"Combining shares of players {S}", LogLevel.VERBOSE)

    w = 1
    for i in S:
        x_i, poc_i = players[i-1].generate_signature_share(delta, protocol)

        # verify proof of correctness
        verify_poc(protocol, x, vks, i, poc_i, v, x_i, n)

        # combine signature share
        lambda_S_0i = lambda_(delta, 0, i, S)
        temp = powmod(x_i, 2 * lambda_S_0i, n)
        w = (w * temp) % n
    log(f"w: {w}", LogLevel.VERBOSE)

    e_prime = protocol.calculate_e_prime()
    gcd, a, b = xgcd(e_prime, e)
    assert gcd == 1, "gcd(e', e) != 1"

    xe_prime = powmod(x, e_prime, n)
    we = powmod(w, e, n)
    assert we == xe_prime, "w^e != x^e'"

    assert e_prime * a + e * b == 1, "e'a + eb != 1"

    wa = powmod(w, a, n)
    xb = powmod(x, b, n)
    y = protocol.calculate_y(wa, xb)

    ye = powmod(y, e, n)
    log(f"y^e: {ye}", LogLevel.VERBOSE)

    assert ye == H(message, n), "Invalid message signature"
    log("Message signature was valid!", LogLevel.DEFAULT)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Practical Threshold Signatures')
    parser.add_argument(
        'l', type=int, help='total number of participating players')
    parser.add_argument('k', type=int,
                        help='minimum required number of collaborating players to generate signature (quorom size)')
    parser.add_argument(
        't', type=int, help='maximum number of corrupted players')
    parser.add_argument('bitlength', metavar='b', type=int,
                        help='bit length of primes p and q')
    parser.add_argument('message', metavar='M', type=str,
                        help='message to be signed')
    parser.add_argument('-primegen', type=PrimeGenMethod, default=PrimeGenMethod.OPENSSL,
                        help='prime generation method (default: OPENSSL)', choices=list(PrimeGenMethod))
    parser.add_argument('-log', default="DEFAULT",
                        help='log level (default: DEFAULT)', choices=LogLevel.__members__)
    args = parser.parse_args()
    return args


def xgcd(a, b):
    """ 
        Python program for Extended Euclidean algorithm
        https://www.techiedelight.com/extended-euclidean-algorithm-implementation/ 
    """
    if a == 0:
        return (b, 0, 1)
    else:
        gcd, x, y = xgcd(b % a, a)
        # the operator // is for integer division (i.e. quotient without remainder)
        return (gcd, y - (b//a) * x, x)


def verify_poc(protocol, x, vks, i, poc_i, v, x_i, n):
    x_tilde = protocol.calculate_x_tilde(x)
    v_i = vks[i-1]
    z, c = poc_i
    vp1 = powmod(v, z, n)
    vp2 = powmod(v_i, -c, n)

    xp1 = powmod(x_tilde, z, n)
    xp2 = powmod(x_i, -2 * c, n)

    new_v_prime = (vp1 * vp2) % n
    new_x_prime = (xp1 * xp2) % n

    verification = H_prime(v=v, x_tilde=x_tilde, v_i=v_i, x_i2=powmod(x_i, 2, n),
                           v_prime=new_v_prime, x_prime=new_x_prime)

    assert verification == c, "proof of correctness could not be verified"


def lambda_(delta, i, j, S):
    S_except_j = list(filter(lambda s: s != j, S))

    above = 1
    for a in [(i - j_prime) for j_prime in S_except_j]:
        above = above * a
    below = 1
    for b in [(j - j_prime) for j_prime in S_except_j]:
        below = below * b

    return delta * above // below


def log(message, level=LogLevel.DEFAULT):
    global loglevel
    if loglevel >= level:
        print(message)


if __name__ == "__main__":
    main()
