import numpy as np
from scipy.stats import pearsonr
from tqdm import tqdm
import pickle


def find_matrix_of_tuples(trace, min_correlation):
    result = []
    for i in range(10, 30):
        print(f"Iteration {i} / {30}")
        patterns = find_patterns(trace, i)
        candidates = find_candidates(patterns, min_correlation)
        result.append(candidates)
    result_filename = 'matrix_of_tuples.pkl'
    with open(result_filename, 'wb') as file:
        pickle.dump(result, file)
    print("Saved")


def greatest_match(trace, min_correlation, nbr_expected_matches):
    """
    Find the best two correlated sequences for different wave lengths
    logic: longer sequences are more valuable, since they are less likely to happen
    """
    # create list of tuples. Each tuple is composed of the largest 2 unique patterns of size n.
    # all_large_tuples = []
    # for i in range(10, 30):
    #     patterns = find_patterns(trace, i)
    #     candidates = find_candidates(patterns, min_correlation)
    #     all_large_tuples.append(candidates)

    with open("matrix_of_tuples.pkl", 'rb') as file:
        all_large_tuples = pickle.load(file)

    # I want a loading bar, bc it's fun.
    total_iterations = len(all_large_tuples)

    # Start from the smallest pattern and check if we have a pattern that fits after it. If not, go next pattern.
    # If yes, try matching until full pattern is found.
    # tqdm with its keywords 'desc' and 'unit' is to create a loading bar for fun. Other than that, it's a simple for loop.
    for i in tqdm(range(total_iterations), desc="Processing", unit="iteration"):
        # len(all_large_tuples[i]) is equal to 2, since we decided for now, that we only need the two best patterns
        # from each length
        for j in range(len(all_large_tuples[i])):
            pattern_1 = all_large_tuples[i][j][0]
            # check wave after this one
            # Note, that the below line gives the first position that is NOT included in pattern_1
            end_of_p1_in_trace = all_large_tuples[i][j][1] + len(pattern_1)
            # To get second pattern
            # we have to iterate over all elements in all_large_tuples, since we only ruled out previous elements
            # that start the sequence. They still could be the second element.
            for k in range(len(all_large_tuples)):
                for m in range(len(all_large_tuples[k])):
                    # Make sure the algo is not trying to match patterns further than the length of the trace.
                    # This will only be called, if no repeating pattern is found at all.
                    if end_of_p1_in_trace + len(all_large_tuples[k][m][0]) > len(trace):
                        return "No Repeating patterns found"
                    if get_correlation(trace, end_of_p1_in_trace, all_large_tuples[k][m], min_correlation):
                        exponent = find_bin_exp(trace, all_large_tuples[i][j], all_large_tuples[k][m], min_correlation)
                        # Workaround solution to make sure that the second match is not just a subpattern of the
                        # correct pattern.
                        if len(exponent) > 2:
                            return exponent


def find_bin_exp(trace, tuple_1, tuple_2, min_correlation=0.7):
    """
    Takes two patterns and tries to match them to the trace.
    :param trace: Energy consumption trace in form of a list of values
    :param tuple_1: tuple containing (list of values, initial position in the trace, integer number)
    :param tuple_2: tuple containing (list of values, initial position in the trace, integer number)
    :param min_correlation: Value between 0 and 1 that represents how closely the patterns need to match the trace.
    The higher the number, the larger the expected correlation is.
    :return: String representation of a binary number
    """
    # We will assume that the first matched pattern is a 1 in the exponent. It could also represent a 0.
    # We simply have no way to know
    exponent = "1"
    current_trace_loc = tuple_1[1] + len(tuple_1[0])
    while True:
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
    print(f"The Exponent is 1{exponent} or 1{''.join(['1' if bit == '0' else '0' for bit in exponent])}")
    return exponent


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


    # Set a seed for reproducibility
    np.random.seed(42)
    # Generate a random list of size 50
    trace_a = np.random.rand(50)
    # Display the generated list
    print(trace_a)
    # print(frequent_patterns)
    # x = [1, 6, 1.2, 8, 0.4, 9]
    # y = [1.2, 8, 0.5, 5, 0.9, 8]
    # print(pearsonr(x, y))
    # z = [0.2, 0.8, 0.5, 0.5, 0.9, 0.8]
    # print(pearsonr(x, z))

    # wave_length = 6
    # patterns = find_patterns(trace, wave_length)
    # print(patterns)
    # most_common = find_candidates(patterns)
    # print(most_common)

    trace_a = [-0.31640625, -0.109375, -0.2421875, -0.46875, -0.1484375, -0.12890625, -0.296875, -0.47265625, -0.4453125, -0.4609375, -0.21484375, -0.1171875, -0.28515625, -0.1796875, -0.26171875, -0.1875, -0.07421875, -0.0703125, -0.24609375, -0.453125, -0.109375, -0.23046875, -0.421875, -0.15234375, -0.24609375, -0.14453125, -0.2890625, -0.18359375, -0.27734375, -0.1796875, -0.2421875, -0.1484375, -0.26953125, -0.12890625, -0.2734375, -0.1796875, -0.265625, -0.16796875, -0.3046875, -0.1484375, -0.28515625, -0.1953125, -0.27734375, -0.16015625, -0.26953125, -0.1953125, -0.0703125, -0.16796875, -0.3359375, -0.21484375, -0.29296875, -0.19140625, -0.33203125, -0.23046875, -0.3046875, -0.1796875, -0.32421875, -0.2421875, -0.30859375, -0.17578125, -0.2734375, -0.19140625, -0.0859375, -0.17578125, -0.34765625, -0.21875, -0.30078125, -0.19140625, -0.328125, -0.21875, -0.29296875, -0.19140625, -0.32421875, -0.25, -0.30859375, -0.16796875, -0.27734375, -0.20703125, -0.078125, -0.17578125, -0.34765625, -0.22265625, -0.29296875, -0.19140625, -0.328125, -0.23046875, -0.30859375, -0.21484375, -0.2890625, -0.19921875, -0.30859375, -0.17578125, -0.3203125, -0.203125, -0.30078125, -0.19921875, -0.33203125, -0.16015625, -0.296875, -0.2109375, -0.296875, -0.19140625, -0.28515625, -0.22265625, -0.09765625, -0.19140625, -0.36328125, -0.23828125, -0.30859375, -0.2109375, -0.3515625, -0.25, -0.33203125, -0.22265625, -0.29296875, -0.2109375, -0.32421875, -0.18359375, -0.3203125, -0.21875, -0.296875, -0.203125, -0.33984375, -0.19140625, -0.328125, -0.23828125, -0.3203125, -0.1953125, -0.296875, -0.23046875, -0.10546875, -0.203125, -0.37890625, -0.25390625, -0.328125, -0.2109375, -0.3515625, -0.25, -0.3359375, -0.21875, -0.3515625, -0.265625, -0.33203125, -0.1875, -0.29296875, -0.21484375, -0.1015625, -0.1953125, -0.3671875, -0.2421875, -0.3125, -0.2109375, -0.3515625, -0.25390625, -0.328125, -0.2109375, -0.34765625, -0.2578125, -0.3203125, -0.1875, -0.2890625, -0.21875, -0.1015625, -0.19140625, -0.36328125, -0.23046875, -0.30859375, -0.203125, -0.34765625, -0.25390625, -0.33203125, -0.2265625, -0.2890625, -0.19921875, -0.3203125, -0.19140625, -0.32421875, -0.21875, -0.30078125, -0.20703125, -0.33984375, -0.17578125, -0.31640625, -0.23828125, -0.3203125, -0.19140625, -0.30078125, -0.21875, -0.09765625, -0.19140625, -0.36328125, -0.24609375, -0.3203125, -0.21484375, -0.35546875, -0.25390625, -0.33203125, -0.2109375, -0.35546875, -0.2734375, -0.3359375, -0.19140625, -0.2890625, -0.21875, -0.09765625, -0.19140625, -0.37109375, -0.23828125, -0.3203125, -0.203125, -0.3515625, -0.25, -0.33203125, -0.23828125, -0.30078125, -0.2109375, -0.31640625, -0.19140625, -0.31640625, -0.21484375, -0.30078125, -0.2109375, -0.3359375, -0.22265625, -0.3359375, -0.23046875, -0.31640625, -0.19921875, -0.296875, -0.23046875, -0.1015625, -0.1875, -0.36328125, -0.23828125, -0.31640625, -0.21484375, -0.35546875, -0.25390625, -0.33203125, -0.203125, -0.34765625, -0.26171875, -0.33203125, -0.19140625, -0.29296875, -0.2109375, -0.09375, -0.19140625, -0.35546875, -0.23046875, -0.30859375, -0.20703125, -0.34765625, -0.2421875, -0.328125, -0.203125, -0.34375, -0.26171875, -0.3359375, -0.19140625, -0.28515625, -0.2109375, -0.0859375, -0.19140625, -0.359375]
    winner = greatest_match(trace_a, 0.4, 2)
    print(winner)


