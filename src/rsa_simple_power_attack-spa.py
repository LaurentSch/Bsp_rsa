import time
import random
import matplotlib.pyplot as plt


# This is the implementation of the exponent function from the fast_exponentiation.py file
# aka my left to right exponentiation
def fast_exponent(base, exp, mod):
    start_time = time.time()
    power_trace = []
    if exp == 0:
        return 1
    if exp == 1:
        return base % mod
    binary_exponent = bin(exp)[3:]
    step = base
    for i in binary_exponent:
        step = step**2 % mod
        # need to pause the function for a little bit, since the computations are otherwise to fast
        time.sleep(0.01)
        # add a tuple for this operation to the trace. First element is the time elapsed,
        # and second element is an arbitrarily chosen power number and some small random number for noise.
        power_trace.append((time.time() - start_time, 5 + random.uniform(0.1, 0.5)))
        if i == "1":
            step = step * base % mod
            time.sleep(0.01)
            power_trace.append((time.time() - start_time, 8 + random.uniform(0.1, 0.5)))
    return step, power_trace


# handout right-to-left exponentiation
def fast_exp(a, n, m):
    start_time = time.time()
    power_trace = []

    x = a  # x = a^20
    y = a if n & 1 else 1  # y = a^n0
    while n > 0:
        n >>= 1  # Right shift n by 1 (equivalent to n //= 2)
        x = (x ** 2) % m  # x = a^(2i-1) → x = a^(2i)
        time.sleep(0.01)
        power_trace.append((time.time() - start_time, 5 + random.uniform(0.1, 0.5)))

        if n & 1:
            y = x if y == 1 else (y * x) % m  # y = a^(ni-1) → y = a^ni
            time.sleep(0.01)
            power_trace.append((time.time() - start_time, 8 + random.uniform(0.1, 0.5)))
    return y, power_trace


def plot_side_by_side(power_trace1, power_trace2):
    plt.subplot(1, 2, 1)
    plot_power_trace(power_trace1, 'Left-to-Right')

    plt.subplot(1, 2, 2)
    plot_power_trace(power_trace2, 'Right-to-Left')

    plt.show()


def plot_power_trace(power_trace, title):
    time_values, y_values = zip(*power_trace)
    plt.plot(time_values, y_values, marker='o', linestyle='-')
    plt.xlabel('Time')
    plt.ylabel('Power Consumption')
    plt.title(title)


# works only for left to right exponentiation
def translate_trace(power_trace):
    private_exponent = "1"
    # Boolean variable that tracks if the previous step was the basic step for every bit in the exponent
    was_basic = False
    for i, item in enumerate(power_trace):
        if item[1] < 7:
            # check if element is the last in the trace.
            if was_basic or (i == len(power_trace) - 1):
                private_exponent += "0"
            was_basic = True
        else:
            private_exponent += "1"
            was_basic = False
    print(private_exponent)
    return int(private_exponent, 2)


# works for right-to-left exp
def translate_trace_rtl(power_trace):
    private_exponent = ""
    # Boolean variable that tracks if the previous step was a computation spike for every bit in the exponent
    was_spike = False
    for i, item in enumerate(power_trace):
        if item[1] < 7:
            # check if element is the last in the trace.
            if not was_spike:
                private_exponent += "0"
            was_spike = False
        else:
            private_exponent += "1"
            was_spike = True
    # reverse the string
    private_exponent = private_exponent[::-1]
    print(private_exponent)
    return int(private_exponent, 2)


if __name__ == "__main__":
    result, trace = fast_exponent(4288743, 8234214, 43)
    print(bin(8234214)[2:])
    print(translate_trace(trace))
    result2, trace2 = fast_exp(4288743, 8234214, 43)
    print(translate_trace_rtl(trace2))
    plot_side_by_side(trace, trace2)
