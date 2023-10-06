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
    binary_exponent = bin(exp)[3:]
    step = base
    for i in binary_exponent:
        # print(i)
        # square
        # print(f"{step}**2 % {mod} = {step**2 % mod}")
        step = step**2 % mod

        # multiply
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


def testing_stuff():
    keys = rsa()
    modulo = keys["modulo"]
    # Almost exactly 5 seconds: 4.9 seconds
    print(f"The for paper result is {fast_exponent_paper(2, 19 * 10**34000, modulo)}")
    print(f"The for my result is    {fast_exponent(2, 19 * 10**500000, modulo)}")
    # print(f"The for my result is {fast_exponent(3, 45, 7)}")

    # print(f"The result is {fast_exponent(5, 19, 13)}")


if __name__ == "__main__":
    #sys.set_int_max_str_digits(10**1000)
    testing_stuff()
