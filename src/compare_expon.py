from math import ceil, log2
from src.naive_exponemtiation import more_naive_exponent
from src.fast_exponentialion import fast_exponent
from src.rsa_simple import rsa
import time


keys = rsa()
modulo = keys["modulo"]
exponent = 19 * 10**400000
smaller_exponent = ceil(log2(exponent))
print(smaller_exponent)
smaller_exponent *= 15
print(smaller_exponent)
print(f"Is {smaller_exponent} larger then the expected 19 * 10**6? {smaller_exponent > 19 * 10**6}")
print(f"My fast result is {fast_exponent(modulo-1, exponent, modulo)}")
print(f"My slow result is {more_naive_exponent(modulo-1, smaller_exponent, modulo)}")

