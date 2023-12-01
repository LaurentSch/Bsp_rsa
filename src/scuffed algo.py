import numpy as np

def get_exponent_from_trace2(trace, exp_lenght, L):
    prep_trace = np.abs(trace[20:L])
    exponent_list = []
    newBit = True
    count = 0
    previous_nbr = [0, 0]
    panik = False
    for i in enumerate(prep_trace):
        if count in (15, 25):
            print(count)
            print(f"Previous: {previous_nbr[0]}")
            print(f"Current: {prep_trace[i]}")
        if len(exponent_list) > exp_lenght:
            exponent_list = exponent_list[0:exp_lenght]
            break
        if newBit:
            exponent_list.append(prep_trace[i])
            newBit = False
            count += 1
        # Problem: there is no good cutoff (0.2 doesn't work for everything). So I need a second condition.
        # In this case I said: the operation has to take a certain time in addition to an 0.2 energy spike.
        elif (prep_trace[i] + previous_nbr[0] > 0.33) and (count in (15, 25)) or panik:
            exponent_list[len(exponent_list) - 1] += prep_trace[i]
            newBit = True
            count = 0
        else:
            exponent_list[len(exponent_list) - 1] += prep_trace[i]
            count += 1

        previous_nbr[0] = previous_nbr[1]
        previous_nbr[1] = prep_trace[i]
        # print(count)
        if count > 25:
            sum_current = prep_trace[i] + previous_nbr[0]
            sum_15 = prep_trace[i - 10] + prep_trace[i - 12]
            if sum_current > sum_15:
                exponent_list[len(exponent_list) - 1] += prep_trace[i]
                newBit = True
                count = 0
            else:
                i = i - 10
                exponent_list[len(exponent_list) - 1] = 0
                panik = True

    exp = convert_to_nb(exponent_list)
    return exponent_list, exp

def convert_to_nb(exponent_list):
    priv_ex = ""
    for i in exponent_list:
        if i > 1.8:
            priv_ex += "1"
        else:
            priv_ex += "0"
    priv_ex = priv_ex[::-1]
    return priv_ex


def try_other(trace, trace_start, exp_length, L):
    """
    Generates the exponent from the power trace of RSA operation.
    :param trace: Power Trace of the operation
    :param trace_start: Trace number where the RSA operation starts
    :param exp_length: Length of the exponent that we look for
    :param L: Cutoff of the trace (makes the list smaller)
    :return: exponent_list, exp: The list of exponent bits found as a list and a String
    """
    prep_trace = np.abs(trace[trace_start:L])
    exponent_list = []
    new_bit = True
    count = 0
    average = sum(prep_trace[:200]) / 200
    for i, number in enumerate(prep_trace):
        if len(exponent_list) > exp_length:
            exponent_list = exponent_list[0:exp_length]
            break
        if new_bit:
            exponent_list.append(number)
            new_bit = False
            count += 1
        elif number > average > prep_trace[i - 4] and prep_trace[i - 2] > average:
            exponent_list[len(exponent_list) - 1] += prep_trace[i]
            new_bit = True
            count = 0
        else:
            exponent_list[len(exponent_list) - 1] += number
            count += 1
        print(count)
        if count > 30:
            break

    exp = convert_to_nb(exponent_list)
    return exponent_list, exp


