import sys
import time
from src.rsa_simple import rsa


# Decorator function to measure execution time
def check_time_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time for {func.__name__}: {execution_time} seconds")
        return result
    return wrapper


@check_time_decorator
def fast_exponent(base, exp, mod):
    x = base
    y = base if exp % 2 == 1 else 1
    exp //= 2
    while exp > 0:
        x = (x ** 2) % mod
        if exp % 2 == 1:
            y = (x if y == 1 else (y * x) % mod)
        exp //= 2
        if exp < 10**100:
            print(exp)
            print(x)
            print(y)
    return y


def testing_stuff():
    keys = rsa()
    modulo = keys["modulo"]
    # Almost exactly 5 seconds: 4.9 seconds
    #print(f"The result is {fast_exponent(2, 19 * 10**34000, modulo)}")
    print(f"The result is {fast_exponent(5, 19, 13)}")


if __name__ == "__main__":
    #sys.set_int_max_str_digits(10**1000)
    testing_stuff()
