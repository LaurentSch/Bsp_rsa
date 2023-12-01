import random
import matplotlib.pyplot as plt


def montgomery_ladder(base, exp, modulus):
    """
    Calculates "base ** exp mod modulus" using the montgomery method
    :param base: integer base
    :param exp: integer exponent
    :param modulus: integer modulo
    :return: base^exp mod modulus
    """
    trace = []
    r_0 = 1
    r_1 = base
    exp_binary = bin(exp)[2:]
    # exp_binary = exp_binary[::-1]
    print(exp_binary)
    for bit in exp_binary:
        if bit == "0":
            trace.append(random.uniform(0, 0.2))
            r_1 = r_0 * r_1 % modulus
            trace.append(random.uniform(0.8, 1))
            r_0 = r_0 ** 2 % modulus
            trace.append(random.uniform(0.6, 0.8))
            print("0")
        else:
            trace.append(random.uniform(0, 0.2))
            r_0 = r_0 * r_1 % modulus
            trace.append(random.uniform(0.8, 1))
            r_1 = r_1 ** 2 % modulus
            trace.append(random.uniform(0.6, 0.8))
            print("1")
    return r_0, trace


def montgomery_ladder_dummy(base, exp_binary, modulus):
    """
    Calculates "base ** exp mod modulus" using the montgomery method
    Takes binary number as the exponent
    NOTE that no matter it the exponent bit is 0 or 1, the first operation is always r_0 * r_1
    This be good
    :param base: integer base
    :param bin_exp: binary exponent
    :param modulus: integer modulo
    :return: base^exp mod modulus
    """
    trace = []
    r_0 = 1
    r_1 = base
    # exp_binary = exp_binary[::-1]
    for bit in exp_binary:
        if bit == 0:
            trace.append(random.uniform(0, 0.2))
            r_1 = r_0 * r_1 % modulus
            trace.append(random.uniform(0.8, 1))
            r_0 = r_0 ** 2 % modulus
            trace.append(random.uniform(0.6, 0.8))
        else:
            trace.append(random.uniform(0, 0.2))
            r_0 = r_0 * r_1 % modulus
            trace.append(random.uniform(0.8, 1))
            r_1 = r_1 ** 2 % modulus
            trace.append(random.uniform(0.6, 0.8))
    return r_0, trace

def montgomery_ladder_bitwise_operations(base, exp, modulus):
    """
    IDK why no work...
    Calculates "base ** exp mod modulus" using the montgomery method
    :param base: integer base
    :param exp: integer exponent
    :param modulus: integer modulo
    :return: base^exp mod modulus
    """
    r_0 = 1
    r_1 = base
    exp_binary = bin(exp)[2:]
    # exp_binary = exp_binary[::-1]
    for bit in exp_binary:
        mask = -(bit == '0')    # 0 if bit '1' and -1 if bit '0'.
        r_0_old = r_0
        r_0 = ((r_0 ** 2 % modulus) & (mask)) | ((r_0 * r_1 % modulus) & (~mask))
        r_1 = ((r_0_old * r_1 % modulus) & (mask)) | ((r_1 ** 2 % modulus) & (~mask))
    return r_0


def plot_power_trace(power_trace, title):
    """
    Plots a power trace.
    :param power_trace: list of power trace values
    """
    plt.plot(power_trace)
    plt.xlabel('Time')
    plt.ylabel('Power')
    plt.title(title)


def plot_side_by_side(power_trace1, power_trace2):
    plt.subplot(1, 2, 1)
    plot_power_trace(power_trace1, "Trace 1")

    plt.subplot(1, 2, 2)
    plot_power_trace(power_trace2, "Trace 2")

    plt.show()


if __name__ == "__main__":
    print(pow(1271, 38815, 352))
    print(montgomery_ladder(1271, 38815, 352))
    print("_________")
    print(montgomery_ladder_bitwise_operations(1271, 38815, 352))
    expon = bin(38815)[2:]
    # Plot two extremes side by side.
    value, power_trace1 = montgomery_ladder_dummy(1271, "00000000", 352)
    value, power_trace2 = montgomery_ladder_dummy(1271, "11111111", 352)
    plot_side_by_side(power_trace1, power_trace2)

