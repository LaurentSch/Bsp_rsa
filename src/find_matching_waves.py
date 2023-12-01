import numpy as np
from scipy.stats import pearsonr


def greatest_match(trace, min_correlation, nbr_expected_matches):
    """
    Find the best two correlated sequences for different wave lengths
    logic: longer sequences are more valuable, since they are less likely to happen
    """
    # Run the loop once to initialize the first values of winners
    patterns = find_patterns(trace, 10)
    largest_tuples = find_candidates(patterns, min_correlation)
    winners = largest_tuples
    for i in range(11, 40):
        patterns = find_patterns(trace, i)
        largest_tuples = find_candidates(patterns, min_correlation)

        # gauntlet
        print(f"largest_tuples[0][0]: {largest_tuples[0][0]} and largest_tuples[1][0]: {largest_tuples[1][0]}")
        # if largest_tuples[0][0] + largest_tuples[1][0] >= nbr_expected_matches - 1:
        #     winner = largest_tuples
        # else:
        #     # to stop when nothing better will be found (probably)
        #     break

        # gauntlet
        winners = gauntlet(winners, largest_tuples[0], nbr_expected_matches)
        winners = gauntlet(winners, largest_tuples[1], nbr_expected_matches)

    return winners


def gauntlet(winners, challenger, nbr_expected_matches):
    """
    Checks if current best guess should be replaced by new one or not.
    :param winners: current best repeating pattern guess
    :param challenger: new potential best pattern guess
    :param nbr_expected_matches: expected exponent lenght
    :return: updated best repeating pattern guess
    """

    correlation_win1_new1 = abs(average_correlation(winners[0][1], challenger[1]))
    correlation_win2_new1 = abs(average_correlation(winners[1][1], challenger[1]))

    # 1) pattern match and larger length -> replace (no questions asked)
    # no need to check length, since this is the first element, so it's size is always larger
    if correlation_win1_new1:
        winners[0] = challenger
        # 1.1) pattern match and larger length -> replace (no questions asked)
        if correlation_win2_new1:
            winners[1] = challenger
        # 1.2) pattern doesn't match. Check match amount in comparison to nbr_expected_matches
        elif winners[0][0] + challenger[0] >= nbr_expected_matches:
            winners[1] = challenger
    # 2) pattern doesn't match.
    else:
        # 2.1) pattern matches winners[1] -> replace
        if correlation_win2_new1:
            winners[1] = challenger
        # 2.2) pattern length bigger than winners[0] and bigger or equal to nbr_expected_matches -> replace
        elif len(winners[0][1]) < len(challenger[1]) and winners[1][0] + challenger[0] >= nbr_expected_matches:
            winners[0] = challenger
        # 2.3) pattern length bigger than winners[1]  and bigger or equal to nbr_expected_matches -> replace
        elif winners[0][0] + challenger[0] >= nbr_expected_matches:
            winners[1] = challenger

    return winners


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


def find_candidates(patterns, min_correlation):
    """
    Find the amount of times, each pattern is repeating
    Return the two most repeated patterns with the number of times they repeated.
    """
    pattern_repetition = []
    for i in range(len(patterns)):
        count = 0
        pattern = []
        correlation_total = 0
        for j in range(i + 1, len(patterns)):
            correlation, _ = pearsonr(patterns[i], patterns[j])
            correlation = abs(correlation)
            if correlation > min_correlation:
                count += 1
                pattern.append(j)
                correlation_total += correlation

        pattern_repetition.append((count, patterns[i], pattern, correlation_total))
    # sort list by third element in the tuple
    sorted_list = sorted(pattern_repetition, key=lambda x: x[2])

    largest_tuples = find_largest_with_low_correlation(sorted_list)

    return largest_tuples


def find_largest_with_low_correlation(sorted_list):
    """
    Finds the largest two lists of numbers that don't have a height pearson correlation
    :param sorted_list: list of tuples containing a list of elements in the second postion
    :return: the two largest tuples with low pearson correlation
    """
    largest_tuple = sorted_list[0]
    largest_tuples = [largest_tuple]
    for element in sorted_list[1:]:
        # check if there is a high correlation. If yes, pass
        if pearsonr(largest_tuple[1], element[1]).statistic > 0.4:
            continue
        else:
            second_largest = element
            largest_tuples.append(second_largest)
            break
    return largest_tuples


def average_correlation(list_1, list_2):
    """
    Calculates the average peason correlation between two lists.
    :param list_1: list of elements
    :param list_2: list of elements
    :return: average pearson correlation
    """
    # Find the larger and smaller lists
    if len(list_1) >= len(list_2):
        list_a = list_1
        list_b = list_2
    else:
        list_a = list_2
        list_b = list_1

    correlations = []
    # Iterate over the possible windows of list_a
    for i in range(len(list_a) - len(list_b) + 1):
        compare_list = list_a[i:i + len(list_b)]
        correlation, _ = pearsonr(compare_list, list_b)
        correlations.append(correlation)

    # Calculate the average correlation
    average_corr = sum(correlations) / len(correlations)

    return average_corr


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

    winner = greatest_match(trace, 0.4, 2)
    print(winner)
    print(find_exponent(winner))


