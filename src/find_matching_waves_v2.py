import numpy as np
from scipy.stats import pearsonr
import matplotlib.pyplot as plt


def greatest_match(trace, min_correlation, nbr_expected_matches):
    """
    Find the best two correlated sequences for different wave lengths
    logic: longer sequences are more valuable, since they are less likely to happen
    """
    # create list of tuples. Each tuple is composed of the largest 2 unique patterns of size n.
    all_large_tuples = []
    for i in range(1, 30):
        patterns = find_patterns(trace, i)
        # print(len(patterns))
        all_large_tuples.append(patterns)

    possible_exponents = []
    # Start from the smallest pattern and check if we have a pattern that fits after it. If not, go next pattern.
    # If yes, try matching until full pattern is found.
    # tqdm with its keywords 'desc' and 'unit' is to create a loading bar for fun. Other than that, it's a simple for loop.
    # for i in range(len(all_large_tuples)):
    for i in [15, 16, 17, 23, 24, 25, 26]:
        print("--------------------------------")
        print(f"Number of total iterations: {i+1} / {len(all_large_tuples)}")
        # len(all_large_tuples[i]) is equal to 2, since we decided for now, that we only need the two best patterns
        # from each length
        # for j in range(len(all_large_tuples[i])):
        for j in range(60):

            pattern_1 = all_large_tuples[i][j][0]
            # check wave after this one
            # Note, that the below line gives the first position that is NOT included in pattern_1
            end_of_p1_in_trace = all_large_tuples[i][j][1] + len(pattern_1)
            # To get second pattern
            # we have to iterate over all elements in all_large_tuples, since we only ruled out previous elements
            # that start the sequence. They still could be the second element.
            #for k in range(len(all_large_tuples)):
            for k in [16, 17, 23, 24, 25, 26]:
                # for m in range(len(all_large_tuples[k])):
                for m in range(60):
                    if all_large_tuples[i][j][1] > 60:
                        break
                    # Make sure the algo is not trying to match patterns further than the length of the trace.
                    # This will only be called, if no repeating pattern is found at all.
                    if end_of_p1_in_trace + len(all_large_tuples[k][m][0]) > len(trace):
                        return "No Repeating patterns found"
                    # this can match the same pattern twice
                    # if get_correlation(trace, end_of_p1_in_trace, all_large_tuples[k][m], min_correlation):
                    exponent = find_bin_exp(trace, all_large_tuples[i][j], all_large_tuples[k][m], nbr_expected_matches, min_correlation)
                    # Workaround solution to make sure that the second match is not just a subpattern of the
                    # correct pattern.
                    if len(exponent[2]) >= nbr_expected_matches - 1:
                        # Add new found match to list of matches, if it's not a duplicate
                        is_duplicate = False
                        for u in possible_exponents:
                            if exponent[2] == u[2]:
                                is_duplicate = True
                        if not is_duplicate:
                            possible_exponents.append(exponent)
    return possible_exponents


def find_bin_exp(trace, tuple_1, tuple_2, nbr_expected_matches, min_correlation=0.7):
    """
    Takes two patterns and tries to match them to the trace.
    :param trace: Energy consumption trace in form of a list of values
    :param tuple_1: tuple containing (list of values, initial position in the trace, integer number)
    :param tuple_2: tuple containing (list of values, initial position in the trace, integer number)
    :param nbr_expected_matches: expected length of the exponent
    :param min_correlation: Value between 0 and 1 that represents how closely the patterns need to match the trace.
    The higher the number, the larger the expected correlation is.
    :return: String representation of a binary number
    """

    # We will assume that the first matched pattern is a 1 in the exponent. It could also represent a 0.
    # We simply have no way to know
    exponent = "1"
    current_trace_loc = tuple_1[1] + len(tuple_1[0])
    while True:
        # check if length of next pattern has a positional equivalent inside the trace
        if current_trace_loc + len(tuple_1[0]) > len(trace):
            break

        # Check if the next bit matches pattern_1
        if get_correlation(trace, current_trace_loc, tuple_1, min_correlation):
            exponent += "1"
            current_trace_loc += len(tuple_1[0])
            # skip to next loop iteration
            continue
        # Check for patter_2

        if get_correlation(trace, current_trace_loc, tuple_2, min_correlation):
            exponent += "0"
            current_trace_loc += len(tuple_2[0])
            # skip to next loop iteration
            continue

        # If neither if condition holds, we assume we arrived at the end of the exponent and break out of the loop
        break
    # To get only at least decent results
    if len(exponent) == nbr_expected_matches - 1:
        print(f"The Exponent is 1{exponent} or 1{''.join(['1' if bit == '0' else '0' for bit in exponent])}")
    found_exponent_trace = [tuple_1, tuple_2, exponent]
    return found_exponent_trace


def get_correlation(trace, trace_start_loc, tuple_1, min_correlation):
    """
    Checks if the correlation of a tuple compared to a sublist of the trace is larger than min_correlation
    :param trace: Energy consumption trace in form of a list of values
    :param trace_start_loc: Where the sublist of the trace starts at
    :param tuple_1: tuple containing (list of values, initial position in the trace, integer number) that is to
    be compared to the trace sublist
    :param min_correlation: Value between 0 and 1 that represents how closely the patterns need to match the trace.
    The higher the number, the larger the expected correlation is.
    :return: True if the correlation value between sub-trace and tuple is larger than min_correlation.
    False if the correlation value is smaller.
    """
    # Take a snipped out of the trace of the same length as pattern_1
    # print(f"len of trace_start_loc = {trace_start_loc}")
    # print(f"len of trace_start_loc+len(tuple_1[0]) = {trace_start_loc+len(tuple_1[0])}")
    trace_part = trace[trace_start_loc:trace_start_loc+len(tuple_1[0])]
    correlation, _ = pearsonr(trace_part, tuple_1[0])
    correlation = abs(correlation)
    if correlation >= min_correlation:
        return True
    else:
        return False


def find_patterns(trace, wave_length):
    """
    Get all sets of values of size 'wave length' that follow directly after each other as a list of lists.
    :returns list of tuples with first position: list of numbers of the wave, and second position wave start position
    """
    patterns = []
    for i in range(len(trace) - wave_length + 1):
        pattern = []
        for j in range(wave_length):
            pattern.append(trace[i + j])
        # i represents where the pattern started. Useful for finding the right pattern later.
        patterns.append((pattern, i))
    return patterns


def find_candidates(patterns, min_correlation):
    """
    Find the amount of times, each pattern is repeating
    :returns list of tuples:
        first element  = the list of numbers that represent the pattern
        second element   = the starting position of the pattern
        third element   = how often the pattern had a high correlation
    """
    pattern_repetition = []
    for i in range(len(patterns)):
        count = 0
        for j in range(i + 1, len(patterns)):
            correlation, _ = pearsonr(patterns[i][0], patterns[j][0])
            correlation = abs(correlation)
            if correlation > min_correlation:
                count += 1

        # patterns[i][0] for the list of numbers that are the pattern
        # patterns[i][1] for the starting position of the pattern
        # count = how often the pattern had a high correlation
        pattern_repetition.append((patterns[i][0], patterns[i][1], count))
    # sort list by third element in the tuple.
    # Meaning by the number of times it was repeated (by count).
    sorted_list = sorted(pattern_repetition, key=lambda x: x[2])

    largest_tuples = find_largest_with_low_correlation(sorted_list)

    return largest_tuples


def find_largest_with_low_correlation(sorted_list):
    """
    Finds the largest two lists of numbers that don't have a high pearson correlation
    :param sorted_list: list of tuples containing a list of elements in the second postion
    :return: the two largest tuples with low pearson correlation
    """
    largest_tuple = sorted_list[0]
    largest_tuples = [largest_tuple]
    for element in sorted_list[1:]:
        # check if there is a high correlation. If yes, pass
        if pearsonr(largest_tuple[0], element[0]).statistic > 0.4:
            continue
        else:
            second_largest = element
            largest_tuples.append(second_largest)
            break
    return largest_tuples


def plot_lists(list_1, list_2, offset):
    # Shift one list to start at location 22
    list_o = []
    for i in range(offset):
        list_o.append(0)
    shifted_list2 = list_o + list_2

    # Plot the original and shifted lists
    plt.plot(list_1, label='trace')
    plt.plot(shifted_list2, label='List 2 Shifted', linestyle='dashed')

    # Set the y-axis limit to show both lists
    plt.ylim(0, max(max(list_1), max(shifted_list2)) + 5)

    # Add labels and legend
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()

    # Show the plot
    plt.show()


if __name__ == "__main__":
    # # Calculate correlation matrix
    # correlation_matrix = calculate_correlation_matrix(data)
    #
    # # Find most frequent patterns (adjust threshold as needed)
    # frequent_patterns = find_most_frequent_patterns(correlation_matrix, threshold=0.8)
    #
    # # Display results
    # print("Correlation Matrix:")
    # print(correlation_matrix)
    # print("\nMost Frequent Patterns:")
    # print(frequent_patterns)

    # wave_length = 6
    # patterns = find_patterns(trace, wave_length)
    # print(patterns)
    # most_common = find_candidates(patterns)
    # print(most_common)
    actual_exponent = "1001010110111000100101001101100100011111000111001010000100000110"
    data_list = [-0.0078125, 0.171875, -0.03515625, 0.49609375, 0.05078125, 0.03125, -0.10546875, -0.12890625, -0.15625, -0.3203125, -0.05078125, 0.0234375, -0.12890625, 0.0078125, -0.06640625, -0.0078125, 0.11328125, 0.1015625, -0.0546875, -0.1015625, 0.15234375, 0.17578125, -0.19140625, 0.078125, -0.04296875, 0.0234375, -0.12890625, 0.04296875, -0.06640625, 0.0234375, -0.14453125, -0.015625, -0.05859375, 0.1640625, -0.00390625, 0.19921875, 0.1171875, 0.0, -0.16015625, 0.05078125, -0.05859375, 0.00390625, -0.15234375, 0.0234375, -0.10546875, 0.08203125, -0.046875, 0.05859375, -0.05078125, 0.08984375, -0.09765625, 0.07421875, -0.0625, 0.015625, -0.10546875, 0.0703125, -0.09765625, 0.0546875, -0.0703125, 0.125, -0.03515625, 0.16796875, 0.08984375, -0.0234375, -0.18359375, 0.02734375, -0.078125, -0.0234375, -0.1875, 0.00390625, -0.1171875, 0.0390625, -0.078125, 0.0234375, -0.08984375, 0.02734375, -0.12890625, 0.04296875, -0.09765625, 0.01171875, -0.09375, 0.08203125, -0.11328125, 0.03515625, -0.08984375, 0.1328125, -0.04296875, 0.171875, 0.08203125, -0.0390625, -0.19921875, 0.00390625, -0.09765625, -0.0234375, -0.1875, -0.015625, -0.125, -0.0390625, -0.19140625, -0.04296875, -0.11328125, 0.10546875, -0.04296875, 0.14453125, 0.07421875, -0.03125, -0.19140625, 0.01953125, -0.09375, -0.0234375, -0.19140625, -0.015625, -0.1171875, -0.04296875, -0.19140625, -0.05078125, -0.10546875, 0.12109375, -0.04296875, 0.1640625, 0.07421875, -0.03515625, -0.1875, 0.00390625, -0.09765625, -0.02734375, -0.19140625, -0.015625, -0.12109375, -0.02734375, -0.18359375, -0.05078125, -0.11328125, 0.1171875, -0.05078125, 0.1640625, 0.078125, -0.03515625, -0.1953125, 0.01171875, -0.09765625, -0.02734375, -0.1953125, -0.0234375, -0.11328125, -0.02734375, -0.1875, -0.0546875, -0.1171875, 0.10546875, -0.04296875, 0.15234375, 0.07421875, -0.0234375, -0.19140625, 0.01171875, -0.10546875, -0.0390625, -0.19921875, -0.015625, -0.10546875, -0.0234375, -0.1875, -0.0546875, -0.125, 0.12890625, -0.04296875, 0.16015625, 0.08203125, -0.03515625, -0.19140625, 0.01953125, -0.10546875, -0.02734375, -0.19140625, 0.0, -0.125, 0.03515625, -0.0859375, 0.01171875, -0.0859375, 0.0625, -0.12890625, 0.04296875, -0.078125, 0.00390625, -0.12890625, 0.02734375, -0.12890625, 0.046875, -0.09765625, 0.1171875, -0.04296875, 0.16015625, 0.0703125, -0.04296875, -0.19921875, 0.01171875, -0.109375, -0.04296875, -0.19921875, -0.01171875, -0.1171875, -0.04296875, -0.1875, -0.05859375, -0.12890625, 0.1171875, -0.05078125, 0.140625, 0.07421875, -0.03515625, -0.1875, 0.01171875, -0.09765625, -0.0390625, -0.19921875, -0.0234375, -0.11328125, -0.0234375, -0.18359375, -0.05078125, -0.125, 0.1171875, -0.04296875, 0.16015625, 0.078125, -0.02734375, -0.19140625, 0.01953125, -0.09765625, -0.046875, -0.203125, -0.0078125, -0.11328125, -0.02734375, -0.17578125, -0.0546875, -0.1171875, 0.1171875, -0.03515625, 0.1640625, 0.08203125, -0.03515625, -0.19140625, 0.01171875, -0.109375, -0.05078125, -0.19140625, 0.00390625, -0.10546875, -0.02734375, -0.1875, -0.05859375, -0.12890625, 0.1171875, -0.04296875, 0.17578125, 0.08203125, -0.02734375, -0.19140625, 0.0234375, -0.09765625, -0.02734375, -0.1796875, -0.0078125, -0.1328125, 0.046875, -0.06640625, 0.02734375, -0.08984375, 0.04296875, -0.12109375, 0.046875, -0.09765625, 0.0, -0.1171875, 0.0546875, -0.1171875, 0.015625, -0.1171875, 0.1171875, -0.05859375, 0.16015625, 0.06640625, -0.02734375, -0.1953125, 0.00390625, -0.109375, -0.05078125, -0.19921875, -0.01953125, -0.12109375, -0.03515625, -0.1875, -0.0625, -0.12890625, 0.1171875, -0.04296875, 0.140625, 0.07421875, -0.02734375, -0.19140625, 0.0, -0.10546875, -0.046875, -0.1953125, -0.01953125, -0.1328125, 0.046875, -0.07421875, 0.01953125, -0.08984375, 0.04296875, -0.140625, 0.04296875, -0.0703125, 0.01171875, -0.15234375, -0.0234375, -0.1484375, -0.015625, -0.11328125, 0.1171875, -0.0546875, 0.15234375, 0.078125, -0.03515625, -0.19921875, 0.00390625, -0.1015625, -0.0390625, -0.19140625, -0.0078125, -0.11328125, -0.03515625, -0.19140625, -0.0703125, -0.12890625, 0.12109375, -0.05078125, 0.1640625, 0.07421875, -0.03515625, -0.19140625, 0.02734375, -0.09375, -0.03125, -0.1953125, -0.01171875, -0.1171875, -0.0390625, -0.19140625, -0.06640625, -0.12890625, 0.12890625, -0.04296875, 0.1875, 0.08984375, -0.02734375, -0.1796875, 0.01953125, -0.09375, -0.03515625, -0.19140625, -0.01171875, -0.14453125, -0.015625, -0.140625, 0.00390625, -0.09765625, 0.01171875, -0.140625, 0.03515625, -0.08203125, 0.01953125, -0.09765625, 0.06640625, -0.09765625, 0.0234375, -0.11328125, 0.12890625, -0.05078125, 0.15234375, 0.08984375, -0.03515625, -0.19140625, 0.00390625, -0.11328125, -0.046875, -0.1875, -0.01171875, -0.1328125, 0.05859375, -0.07421875, 0.00390625, -0.078125, 0.07421875, -0.12109375, 0.04296875, -0.0859375, 0.00390625, -0.125, 0.0390625, -0.1171875, 0.01171875, -0.11328125, 0.1171875, -0.06640625, 0.140625, 0.06640625, -0.04296875, -0.1953125, 0.01171875, -0.1015625, -0.04296875, -0.19921875, -0.015625, -0.1484375, 0.015625, -0.09765625, 0.01171875, -0.09765625, 0.0390625, -0.140625, 0.0234375, -0.09765625, 0.0078125, -0.11328125, 0.06640625, -0.11328125, 0.01953125, -0.125, 0.1015625, -0.06640625, 0.15625, 0.07421875, -0.0390625, -0.19921875, 0.00390625, -0.11328125, -0.046875, -0.1953125, -0.0234375, -0.12109375, -0.02734375, -0.19140625, -0.08203125, -0.13671875, 0.1171875, -0.046875, 0.1640625, 0.08203125, -0.03515625, -0.1953125, 0.00390625, -0.11328125, -0.04296875, -0.19140625, -0.01953125, -0.12109375, -0.01953125, -0.19140625, -0.078125, -0.1328125, 0.12890625, -0.05078125, 0.15234375, 0.07421875, -0.03515625, -0.19921875, 0.01171875, -0.10546875, -0.04296875, -0.1875, -0.015625, -0.1171875, -0.0234375, -0.17578125, -0.07421875, -0.12890625, 0.1171875, -0.046875, 0.15234375, 0.08203125, -0.0390625, -0.1796875, 0.0234375, -0.09375, -0.02734375, -0.19140625, -0.015625, -0.1328125, 0.046875, -0.06640625, 0.0390625, -0.0703125, 0.06640625, -0.12890625, 0.046875, -0.078125, 0.01171875, -0.109375, 0.046875, -0.11328125, -0.0078125, -0.12890625, 0.109375, -0.05859375, 0.16015625, 0.07421875, -0.04296875, -0.19140625, 0.01171875, -0.11328125, -0.05078125, -0.19140625, -0.01953125, -0.140625, -0.01171875, -0.13671875, -0.0078125, -0.09375, 0.046875, -0.12890625, 0.05078125, -0.0859375, 0.0, -0.11328125, 0.0625, -0.11328125, 0.015625, -0.11328125, 0.1171875, -0.05859375, 0.16015625, 0.07421875, -0.04296875, -0.1953125, 0.0078125, -0.12109375, -0.046875, -0.19921875, -0.03515625, -0.15234375, 0.02734375, -0.078125, 0.015625, -0.10546875, 0.0234375, -0.1484375, 0.0390625, -0.078125, 0.00390625, -0.12890625, 0.0390625, -0.12890625, 0.0078125, -0.12890625, 0.1015625, -0.0625, 0.171875, 0.0859375, -0.04296875, -0.19921875, 0.0, -0.1171875, -0.05859375, -0.203125, -0.03515625, -0.14453125, 0.00390625, -0.09765625, 0.01953125, -0.09375, 0.046875, -0.12890625, 0.03515625, -0.09375, 0.00390625, -0.11328125, 0.0546875, -0.12109375, 0.0, -0.125, 0.125, -0.06640625, 0.15234375, 0.06640625, -0.046875, -0.2109375, -0.00390625, -0.11328125, -0.0546875, -0.203125, -0.03515625, -0.1484375, 0.04296875, -0.06640625, 0.0078125, -0.08203125, 0.0546875, -0.140625, 0.03515625, -0.09765625, -0.00390625, -0.1328125, 0.02734375, -0.13671875, -0.01953125, -0.1328125, 0.109375, -0.0703125, 0.1484375, 0.07421875, -0.0390625, -0.20703125, -0.00390625, -0.1171875, -0.05859375, -0.203125, -0.01171875, -0.12109375, -0.03515625, -0.19140625, -0.09765625, -0.1484375, 0.12109375, -0.06640625, 0.16015625, 0.078125, -0.03515625, -0.19921875, 0.00390625, -0.109375, -0.046875, -0.1953125, -0.01953125, -0.125, -0.03515625, -0.1875, -0.08984375, -0.140625, 0.12890625, -0.046875, 0.1796875, 0.08984375, -0.03515625, -0.1953125, 0.01171875, -0.10546875, -0.04296875, -0.19140625, -0.01953125, -0.11328125, -0.03125, -0.18359375, -0.078125, -0.13671875, 0.1328125, -0.05078125, 0.15234375, 0.08984375, -0.03515625, -0.18359375, 0.01171875, -0.09375, -0.03515625, -0.19140625, -0.015625, -0.12890625, 0.0234375, -0.09375, 0.0078125, -0.08984375, 0.046875, -0.13671875, 0.01953125, -0.1171875, -0.0078125, -0.09375, 0.0703125, -0.10546875, 0.01171875, -0.12109375, 0.1171875, -0.06640625, 0.1484375, 0.08203125, -0.03515625, -0.19140625, 0.00390625, -0.11328125, -0.05078125, -0.1953125, -0.02734375, -0.1171875, -0.02734375, -0.19140625, -0.08984375, -0.15234375, 0.1328125, -0.0625, 0.1640625, 0.08984375, -0.0234375, -0.18359375, 0.0, -0.11328125, -0.04296875, -0.19140625, -0.0234375, -0.11328125, -0.02734375, -0.17578125, -0.08984375, -0.140625, 0.1484375, -0.05078125, 0.16015625, 0.08984375, -0.02734375, -0.19140625, 0.00390625, -0.109375, -0.02734375, -0.19140625, -0.01953125, -0.13671875, 0.05859375, -0.06640625, 0.02734375, -0.07421875, 0.06640625, -0.12890625, 0.05078125, -0.06640625, 0.01171875, -0.11328125, 0.0546875, -0.09765625, 0.01953125, -0.11328125, 0.1171875, -0.07421875, 0.15234375, 0.07421875, -0.03515625, -0.19921875, 0.0, -0.1171875, -0.0546875, -0.19921875, -0.03515625, -0.13671875, 0.046875, -0.0703125, 0.015625, -0.08203125, 0.046875, -0.12890625, 0.0390625, -0.09375, 0.01171875, -0.09765625, 0.08203125, -0.10546875, 0.0, -0.12890625, 0.1328125, -0.0703125, 0.13671875, 0.07421875, -0.046875, -0.2109375, -0.01953125, -0.1171875, -0.05078125, -0.19921875, -0.04296875, -0.12890625, -0.0390625, -0.19140625, -0.09765625, -0.15625, 0.1171875, -0.07421875, 0.1484375, 0.08203125, -0.02734375, -0.19140625, -0.00390625, -0.10546875, -0.046875, -0.19140625, -0.03515625, -0.14453125, 0.046875, -0.08203125, 0.01953125, -0.0703125, 0.0625, -0.125, 0.0546875, -0.078125, 0.00390625, -0.1171875, 0.046875, -0.1171875, -0.0078125, -0.1328125, 0.1015625, -0.0859375, 0.16796875, 0.07421875, -0.03515625, -0.203125, -0.01953125, -0.12890625, -0.05859375, -0.19921875, -0.0390625, -0.15234375, 0.01953125, -0.08984375, 0.015625, -0.10546875, 0.015625, -0.1328125, 0.046875, -0.0859375, 0.0, -0.10546875, 0.0546875, -0.1171875, -0.01171875, -0.13671875, 0.1171875, -0.07421875, 0.13671875, 0.07421875, -0.05078125, -0.203125, -0.015625, -0.1171875, -0.04296875, -0.1953125, -0.0390625, -0.12890625, -0.03125, -0.1875, -0.0859375, -0.15625, 0.109375, -0.078125, 0.140625, 0.08203125, -0.02734375, -0.19140625, -0.00390625, -0.10546875, -0.03515625, -0.18359375, -0.0390625, -0.1171875, -0.0234375, -0.17578125, -0.0859375, -0.1484375, 0.109375, -0.06640625, 0.15234375, 0.08984375, -0.015625, -0.17578125, 0.0, -0.10546875, -0.02734375, -0.19140625, -0.0234375, -0.13671875, 0.04296875, -0.07421875, 0.015625, -0.07421875, 0.07421875, -0.1171875, 0.0546875, -0.06640625, 0.0234375, -0.10546875, 0.0703125, -0.10546875, 0.01953125, -0.12890625, 0.109375, -0.0859375, 0.15234375, 0.08203125, -0.03515625, -0.203125, -0.0390625, -0.12890625, -0.046875, -0.19140625, -0.02734375, -0.12890625, -0.02734375, -0.1796875, -0.07421875, -0.1484375, 0.109375, -0.07421875, 0.16015625, 0.08984375, -0.02734375, -0.203125, -0.01171875, -0.11328125, -0.03515625, -0.18359375, -0.0234375, -0.13671875, 0.03515625, -0.078125, 0.0234375, -0.09765625, 0.0390625, -0.13671875, 0.0390625, -0.09375, -0.0078125, -0.08984375, 0.0859375, -0.09375, 0.01953125, -0.12890625, 0.09765625, -0.0859375, 0.16015625, 0.08984375, -0.01953125, -0.1953125, -0.0234375, -0.12109375, -0.04296875, -0.1953125, -0.0234375, -0.11328125, -0.0234375, -0.17578125, -0.08984375, -0.15625, 0.0859375, -0.0703125, 0.16015625, 0.10546875, -0.0078125, -0.19140625, -0.01953125, -0.125, -0.04296875, -0.17578125, -0.01171875, -0.11328125, -0.015625, -0.17578125, -0.078125, -0.15234375, 0.11328125, -0.06640625, 0.1640625, 0.1015625, -0.0078125, -0.19140625, -0.015625, -0.109375, -0.03125, -0.17578125, -0.01171875, -0.12890625, 0.0546875, -0.05859375, 0.02734375, -0.06640625, 0.07421875, -0.11328125, 0.0546875, -0.05859375, 0.0234375, -0.13671875, 0.0234375, -0.12109375, 0.0, -0.12890625, 0.10546875, -0.0859375, 0.1484375, 0.08984375, -0.01953125, -0.203125, -0.0234375, -0.12890625, -0.05078125, -0.1953125, -0.01953125, -0.11328125, -0.015625, -0.17578125, -0.08203125, -0.1484375, 0.08984375, -0.08203125, 0.15234375, 0.1015625, -0.01953125, -0.19140625, 0.0, -0.11328125, -0.0390625, -0.19140625, -0.015625, -0.10546875, -0.01171875, -0.16796875, -0.0703125, -0.1484375, 0.09765625, -0.07421875, 0.171875, 0.1015625, -0.01171875, -0.19140625, -0.015625, -0.11328125, -0.03515625, -0.17578125, -0.01171875, -0.10546875, -0.01171875, -0.16796875, -0.0703125, -0.140625, 0.10546875, -0.0703125, 0.17578125, 0.10546875, -0.015625, -0.19140625, -0.0234375, -0.11328125, -0.02734375, -0.17578125, 0.0, -0.12890625, 0.01953125, -0.10546875, 0.01171875, -0.09375, 0.04296875, -0.1171875, 0.046875, -0.0859375, 0.00390625, -0.09765625, 0.09375, -0.08203125, 0.0390625, -0.12109375, 0.08984375, -0.08984375, 0.15234375, 0.08984375, -0.0234375, -0.1953125, -0.0234375, -0.12890625, -0.04296875, -0.19140625, -0.03125, -0.140625, 0.0546875, -0.0625, 0.0390625, -0.06640625, 0.08203125, -0.12890625, 0.046875, -0.07421875, 0.02734375, -0.11328125, 0.03515625, -0.1171875, -0.0078125, -0.14453125, 0.0859375, -0.09375, 0.14453125, 0.08984375, -0.02734375, -0.203125, -0.02734375, -0.12890625, -0.05078125, -0.19140625, -0.03515625, -0.140625, 0.01171875, -0.09375, 0.01171875, -0.08203125, 0.0546875, -0.125, 0.046875, -0.08203125, 0.01171875, -0.11328125, 0.06640625, -0.10546875, 0.015625, -0.13671875, 0.07421875, -0.11328125, 0.13671875, 0.07421875, -0.0234375, -0.203125, -0.03515625, -0.12890625, -0.05078125, -0.19140625, -0.04296875, -0.12890625, -0.01953125, -0.17578125, -0.08203125, -0.16015625, 0.07421875, -0.09765625, 0.14453125, 0.09765625, -0.015625, -0.19921875, -0.03515625, -0.13671875, -0.05078125, -0.1875, -0.0234375, -0.140625, 0.0703125, -0.0390625, 0.04296875, -0.06640625, 0.0625, -0.12109375, 0.07421875, -0.0546875, 0.02734375, -0.109375, 0.05078125, -0.11328125, 0.01953125, -0.13671875, 0.0703125, -0.109375, 0.140625, 0.08203125, -0.03515625, -0.21484375, -0.05078125, -0.1328125, -0.05078125, -0.19140625, -0.02734375, -0.15234375, 0.01171875, -0.10546875, 0.0078125, -0.08984375, 0.04296875, -0.13671875, 0.01953125, -0.12890625, -0.0078125, -0.10546875, 0.07421875, -0.08984375, 0.01953125, -0.13671875, 0.0703125, -0.11328125, 0.14453125, 0.09375, -0.02734375, -0.20703125, -0.04296875, -0.140625, -0.04296875, -0.19140625, -0.03515625, -0.12890625, -0.015625, -0.17578125, -0.08203125, -0.16796875, 0.0703125, -0.09765625, 0.15234375, 0.1015625, -0.015625, -0.1953125, -0.03515625, -0.1328125, -0.02734375, -0.17578125, -0.02734375, -0.13671875, 0.05859375, -0.03515625, 0.04296875, -0.06640625, 0.08203125, -0.11328125, 0.0625, -0.0546875, 0.0078125, -0.109375, 0.0546875, -0.109375, 0.01953125, -0.1484375, 0.0625, -0.11328125, 0.14453125, 0.0859375, -0.02734375, -0.2109375, -0.0546875, -0.13671875, -0.04296875, -0.19140625, -0.03515625, -0.12890625, -0.0234375, -0.171875, -0.0625, -0.16015625, 0.06640625, -0.10546875, 0.14453125, 0.1015625, -0.015625, -0.203125, -0.05078125, -0.12890625, -0.04296875, -0.1796875, -0.0234375, -0.1328125, 0.05078125, -0.05859375, 0.046875, -0.0859375, 0.04296875, -0.12890625, 0.046875, -0.07421875, 0.02734375, -0.078125, 0.08984375, -0.08984375, 0.015625, -0.1484375, 0.0546875, -0.11328125, 0.15234375, 0.08984375, -0.01953125, -0.2109375, -0.06640625, -0.13671875, -0.04296875, -0.1796875, -0.04296875, -0.12890625, -0.0234375, -0.17578125, -0.078125, -0.1640625, 0.05859375, -0.09765625, 0.15234375, 0.109375, 0.0, -0.19921875, -0.046875, -0.12890625, -0.03515625, -0.171875, -0.0234375, -0.1171875, -0.01953125, -0.16796875, -0.0703125, -0.1484375, 0.0703125, -0.0859375, 0.15234375, 0.10546875, -0.0078125, -0.19140625, -0.04296875, -0.11328125, -0.03515625, -0.16015625, -0.0234375, -0.1328125, 0.06640625, -0.05078125, 0.046875, -0.05078125, 0.0859375, -0.11328125, 0.0546875, -0.06640625, 0.0390625, -0.08984375, 0.06640625, -0.09765625, 0.0234375, -0.14453125, 0.046875, -0.1171875, 0.14453125, 0.1015625, -0.015625, -0.20703125, -0.0625, -0.16015625, -0.03125, -0.17578125, -0.05078125, -0.171875, -0.0546875, -0.046875, -0.203125, -0.05078125, 0.42578125, -0.0859375, 0.01953125, -0.09375, -0.36328125, -0.0859375, -0.140625, 0.03125, -0.0546875, 0.02734375, -0.1640625, 0.0078125, -0.078125, -0.14453125, 0.00390625, 0.04296875, -0.08984375, 0.0546875, 0.03515625, -0.10546875, -0.1328125, -0.16796875, -0.3359375, -0.04296875, -0.140625, 0.015625, -0.01171875, -0.11328125, -0.16015625, -0.19140625, -0.16015625, -0.29296875, -0.0234375, 0.01953125, -0.08984375, 0.09765625, -0.01171875, -0.06640625, 0.13671875, -0.04296875, -0.2578125, 0.046875, -0.07421875, 0.16015625, 0.0234375, -0.07421875, -0.07421875, -0.0859375, -0.07421875, -0.01953125, 0.0546875, 0.078125, -0.0546875, 0.09765625, -0.08984375, 0.03515625, -0.11328125, 0.17578125, 0.05859375, -0.06640625, -0.0234375, 0.0234375, 0.1015625, 0.12109375, -0.05859375, -0.234375, 0.32421875, 0.0078125, 0.0234375, 0.1640625, 0.0859375, -0.078125, -0.34765625, -0.0625, -0.12890625, 0.140625, 0.02734375, -0.05078125, -0.08984375, -0.05859375, -0.01171875, 0.09765625, 0.19921875, 0.015625, 0.00390625, 0.1015625, -0.04296875, -0.26171875, 0.40234375, 0.21484375, -0.23828125, -0.04296875, -0.140625, -0.01953125, -0.01953125, 0.09765625, -0.0078125, 0.046875, -0.05859375, 0.13671875, -0.04296875, 0.12109375, -0.04296875, -0.140625, 0.0625, -0.0234375, 0.10546875, 0.03515625, -0.15625, -0.04296875, -0.1171875, -0.00390625, 0.0859375, -0.2734375, 0.03515625, -0.04296875, 0.0859375, -0.10546875, -0.28515625, 0.2578125, -0.0234375, -0.1171875, 0.1640625, -0.02734375, -0.02734375, 0.11328125, -0.05859375, -0.1484375, -0.30078125, -0.0078125, -0.125, 0.03125, 0.02734375, -0.0546875, -0.09765625, 0.14453125, -0.03515625, -0.23046875, 0.49609375, 0.27734375, 0.01953125, -0.171875, -0.0234375, -0.09765625, -0.26171875, 0.38671875, -0.0234375, -0.12890625, 0.046875, -0.140625, -0.0078125, -0.125, 0.01171875, 0.12]

    # print(len(data_list))

    # remember that each element of possible winners consist of two tuples and a string of a binary number
    possible_winners = greatest_match(data_list, 0.9, len(actual_exponent))
    for i in possible_winners:
        print(i[0][2])
    # plot_list = []
    # for i in possible_winners[0][2]:
    #     if i == "1":
    #         plot_list.append(possible_winners[0][0][0])
    #     else:
    #         plot_list.append(possible_winners[0][2][0])
    #
    # plot_lists(data_list, plot_list, possible_winners[0][0][1])

    # if actual_exponent in possible_winners:
    #     print("Found exponent")
    # else:
    #     print("Exponent not found")
    print(actual_exponent)


