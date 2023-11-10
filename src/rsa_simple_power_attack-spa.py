import time
import random
import matplotlib.pyplot as plt


# This is the implementation of the exponent function from the fast_exponentiation.py file
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


def plot_power_trace(power_trace):
    time_values, y_values = zip(*power_trace)
    plt.plot(time_values, y_values, marker='o', linestyle='-')
    plt.xlabel('Time')
    plt.ylabel('Power Consumption')
    plt.show()


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


if __name__ == "__main__":
    result, trace = fast_exponent(4288743, 8234214, 43)
    print(bin(8234214)[2:])
    print(translate_trace(trace))
    plot_power_trace(trace)
