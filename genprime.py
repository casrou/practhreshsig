from time import time
from random import randint
import multiprocessing as mp
import subprocess
from sympy import randprime, isprime


def search_safe_prime_single(bitsize):
    """
        Search for (probable) safe primes using a single process
    """
    p, p_prime = None, None
    while p is None:
        p, p_prime = try_get_safe_prime(bitsize)
    return p, p_prime


def search_safe_prime_multi(bitsize):
    """
        Search for (probable) safe primes using multiple processes
    """
    processes = []
    result = mp.Queue()
    for i in range(mp.cpu_count()):
        p = mp.Process(target=multi_search_helper, args=(i, result, bitsize))
        processes.append(p)
        p.start()

    for process in processes:
        process.join()

    res = result.get()
    p, p_prime = res[0], res[1]
    return p, p_prime


def multi_search_helper(i, result, bitsize):
    while result.empty():
        p, p_prime = try_get_safe_prime(bitsize)
        if p is None:
            continue
        result.put([p, p_prime])


def try_get_safe_prime(bitsize):
    p_prime = random_odd_int_of_bitsize(bitsize)
    if not is_probable_prime(p_prime):
        return None, None

    p = 2*p_prime+1
    if not is_probable_prime(p):
        return None, None

    return p, p_prime


def random_odd_int_of_bitsize(bitsize):
    bits = "1"
    for _ in range(bitsize-3):
        bits += str(randint(0, 1))
    bits += str(1)
    random_odd_int = int("".join(str(b) for b in bits), 2)
    return random_odd_int


def is_probable_prime(n, rounds=40):
    """
        Miller-Rabin primality test.

        A return value of False means n is certainly not prime. A return value of
        True means n is very likely a prime.    
        https://en.wikipedia.org/wiki/Miller-Rabin_primality_test#Miller–Rabin_test

        rounds = 40
        https://stackoverflow.com/a/6330138/9549916
    """
    if n == 1:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # Write n as 2^r * d + 1 with d odd
    r = 0
    d = n - 1
    while d % 2 == 0:
        d >>= 1
        r += 1

    assert(pow(2, r) * d + 1 == n)

    def inner_loop(r, x):
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                return True
        return False

    # WitnessLoop
    for _ in range(rounds):
        a = randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue

        if inner_loop(r, x):
            continue

        return False

    return True


def search_safe_prime_sympy(bitsize):
    p, p_prime = None, None
    while p is None:
        p, p_prime = try_get_safe_prime_sympy(bitsize)
    return p, p_prime


def try_get_safe_prime_sympy(bitsize):
    # find prime in range such that it is correct bitsize after multiplying by 2 and adding 1
    p_prime = randprime(pow(2, bitsize-2), pow(2, bitsize-1) - 1)
    p = 2*p_prime+1
    if not isprime(p):
        return None, None

    return p, p_prime


def get_safe_prime_openssl(bitsize):
    p = int(
        subprocess
        .run(["openssl", "prime", "-generate", "-safe", "-bits", str(bitsize)],
             stdout=subprocess.PIPE, text=True)
        .stdout
    )
    p_prime = (p-1) // 2
    return p, p_prime
