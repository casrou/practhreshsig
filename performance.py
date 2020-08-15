from time import time
from genprime import search_safe_prime_single, search_safe_prime_multi, search_safe_prime_sympy, get_safe_prime_openssl
from main import main
from shared import LogLevel


def implementation_test():
    log = "NONE"
    l = int(input("l: "))
    k = int(input("k: "))
    t = int(input("t: "))
    bitlength = input("prime bit length: ")
    i = int(input("iterations: "))

    test_args = {'log': log, 'l': l, 'k': k, 't': t, 'bitlength': bitlength, 'message': "hej"}

    running_time = 0
    print(f"BITLENGTH: {bitlength}, iterations: {i}", end="", flush=True)
    for _ in range(i):
        start_time = time()
        main(test_args_dict(test_args))
        running_time += time() - start_time
        print(".", end="", flush=True)
    print(f"\nImplementation running time (avg): {running_time / i}")


def prime_gen_test():
    bitsizes = [64, 128, 256, 384, 512]

    single_time = multi_time = sympy_time = openssl_time = 0

    i = int(input("iterations: "))
    for bitlength in bitsizes:
        print(f"\nBITLENGTH: {bitlength}, iterations: {i}", end="", flush=True)
        for _ in range(i):
            # print("single")
            start_time = time()
            search_safe_prime_single(bitlength)
            single_time += time() - start_time

            # print("multi")
            start_time = time()
            search_safe_prime_multi(bitlength)
            multi_time += time() - start_time

            # print("sympy")
            start_time = time()
            search_safe_prime_sympy(bitlength)
            sympy_time += time() - start_time

            # print("openssl")
            start_time = time()
            get_safe_prime_openssl(bitlength)
            openssl_time += time() - start_time

            print(".", end="", flush=True)

        print("\nMETHOD\t\tSEC PER PRIMES GENERATION (avg.)")
        print(f"single:\t\t{single_time/i}")
        print(f"multi:\t\t{multi_time/i}")
        print(f"sympy:\t\t{sympy_time/i}")
        print(f"openssl:\t{openssl_time/i}")

        single_time = multi_time = sympy_time = openssl_time = 0


class test_args_dict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


if __name__ == "__main__":
    print("________________________________________________________________________________")
    print("PERFORMANCE TEST")
    print("________________________________________________________________________________")
    choice = input("Choose test: \n\t[i]mplementation \n\t[p]rime generation \n> ")

    if choice == "i":
        print("--- IMPLEMENTATION TEST ---")
        implementation_test()
    elif choice == "p":
        print("--- PRIME GENERATION TEST ---")
        prime_gen_test()
