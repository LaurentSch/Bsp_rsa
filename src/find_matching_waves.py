import numpy as np
from scipy.stats import pearsonr
import heapq


def greatest_match(trace):
    """
    Find the best two correlated sequences for different wave lengths
    logic: longer sequences are more valuable, since they are less likely to happen
    """
    winner = 0
    for i in range(5, 40):
        patterns = find_patterns(trace, i)
        largest_tuples = find_candidates(patterns)

        # gauntlet
        print(f"largest_tuples[0][0]: {largest_tuples[0][0]} and largest_tuples[1][0]: {largest_tuples[1][0]}")
        if largest_tuples[0][0] > 1 and largest_tuples[1][0] > 1:
            winner = largest_tuples
        else:
            # to stop when nothing better will be found (probably)
            break
    return winner


def find_patterns(trace, wave_length):
    """
    Get all sets of values of size 'wave length' that follow directly after each other as a list of lists.
    """
    patterns = []
    for i in range(len(trace) - wave_length + 1):
        pattern = []
        for j in range(wave_length):
            pattern.append(trace[i + j])
        patterns.append(pattern)
    return patterns


def find_candidates(patterns):
    """
    Find the amount of times, each pattern is repeating
    Return the two most repeated patterns with the number of times they repeated.
    """
    pattern_repetition = []
    for i in range(len(patterns)):
        count = 0
        pattern = []
        for j in range(i + 1, len(patterns)):
            correlation, _ = pearsonr(patterns[i], patterns[j])
            if correlation > 0.8:
                count += 1
                pattern.append(j)

        pattern_repetition.append((count, patterns[i], pattern))
    # Use heapq to find the two tuples in our list of tuples, that have the largest element in it's first position.
    # key=lambda x: x[0] targets the first position of the tuple
    largest_tuples = heapq.nlargest(2, pattern_repetition, key=lambda x: x[0])
    return largest_tuples


def find_exponent(winner):
    """
    Applies pearson of the winning wave sections on the trace again
    """
    list_a = winner[0][2]
    list_b = winner[1][2]
    max_value = max(max(list_a, default=0), max(list_b, default=0))
    binary_string = ""

    for num in range(1, max_value + 1):
        if num in list_a:
            binary_string += '1'
        elif num in list_b:
            binary_string += '0'

    return binary_string



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
    trace = np.random.rand(50)
    # Display the generated list
    print(trace)
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

    winner = greatest_match(trace)
    print(find_exponent(winner))


