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
    if exp == 0:
        return 1
    if exp == 1:
        return base % mod
    binary_exponent = bin(exp)[3:]
    # This first base represents base^1 (1 is a binary number)
    step = base
    for i in binary_exponent:
        # print(i)

        # square
        # The step**2 adds a 0 at the end of the binary exponent, since:
        # step^base * step°base == step^(base+base)
        # And adding a binary number to itself is itself with an added 0 at the end,
        # so out previously chosen matching exponent (with the first n numbers of the exp in binary) will still match.
        # print(f"{step}**2 % {mod} = {step**2 % mod}")
        step = step**2 % mod

        # multiply
        # If we need the last number of the binary exponent to have a 1 at the end (instead of a zero),
        # we multiply the base^exp with base^1, since this is equivalent to base^(exp + 1)
        if i == "1":
            # print(f"{step} * {base} % {mod} = {step*base % mod}")
            step = step * base % mod
    return step


@check_time_decorator
def fast_exponent_paper(base, exp, mod):
    x = base
    y = base if exp % 2 == 1 else 1
    exp //= 2
    while exp > 0:
        x = (x ** 2) % mod
        if exp % 2 == 1:
            y = (x if y == 1 else (y * x) % mod)
        exp //= 2
    return y


@check_time_decorator
def build_in_pow(base, exp, mod):
    return pow(base, exp, mod)


def testing_stuff():
    keys = rsa()
    modulo = keys["modulo"]
    # Almost exactly 5 seconds: 4.9 seconds
    # print(f"The for paper result is {fast_exponent_paper(2, 19 * 10**34000, modulo)}")
    # Fluctuating between 4.9 and 5.5
    print(f"The for my result is {fast_exponent(2, 19 * 10**400000, modulo)}")
    # pow is faster -.-
    # Fluctuating between 4.8 and 4.9
    print(f"Python pow result is {build_in_pow(2, 19 * 10**400000, modulo)}")
    # print(f"The for my result is {fast_exponent(3, 45, 7)}")

    # print(f"The result is {fast_exponent(5, 19, 13)}")


if __name__ == "__main__":
    #sys.set_int_max_str_digits(10**1000)
    testing_stuff()
