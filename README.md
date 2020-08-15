# Practical Threshold Signatures
As described in [[Shoup, 2000]](https://www.shoup.net/papers/thsig.pdf)

## Prerequisites
* Python 3.8: Can be downloaded at the official website [python.org](python.org)
* SymPy 1.6.1: Install using the Python package installer, `pip install sympy==1.6.1`

## How to run
`python main.py -h`

```
usage: main.py [-h] [-primegen {SINGLEPROCESS,MULTIPROCESS,SYMPY,OPENSSL}] [-log {NONE,DEFAULT,VERBOSE}] l k t b M

Practical Threshold Signatures

positional arguments:
  l                     total number of participating players
  k                     minimum required number of collaborating players to generate signature (quorom size)
  t                     maximum number of corrupted players
  b                     bit length of primes p and q
  M                     message to be signed

optional arguments:
  -h, --help            show this help message and exit
  -primegen {SINGLEPROCESS,MULTIPROCESS,SYMPY,OPENSSL}
                        prime generation method (default: OPENSSL)
  -log {NONE,DEFAULT,VERBOSE}
                        log level (default: DEFAULT)
```
