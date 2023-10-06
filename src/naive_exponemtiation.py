import math
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
def naive_exponent(base, exp, mod):
    """
    Problem with this implementation: Does not work for large numbers because of float size limitations
    """

    number = base**exp
    fit = math.floor(number / mod)
    a = mod * fit
    return number - a


@check_time_decorator
def more_naive_exponent(base, exp, mod):
    result = 1
    for i in range(exp):
        result = (result * base) % mod
        # print(i)

    return result


def testing_stuff():
    keys = rsa()
    modulo = keys["modulo"]
    # Almost exactly 5 seconds: 4.961990118026733 seconds
    print(f"The result is {more_naive_exponent(2, 19000000, modulo)}")


if __name__ == "__main__":
    testing_stuff()


