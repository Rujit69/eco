import math
import sys

# Global lists for defender and challenger.
set1 = []      # Defender: holds the year numbers.
values1 = []   # Defender: holds the amounts.
set2 = []      # Challenger: holds the year numbers.
values2 = []   # Challenger: holds the amounts.
size1 = 0      # Number of entries for defender.
size2 = 0      # Number of entries for challenger.
total_years = 0  # Service life (target sum of years).

# Global interest rate in percent.
i_rate = 0.0

# Global variables for tracking the best combination.
min_pw = float("inf")
best_defender_indices = None  # Will be a list of indices (or None)
best_challenger_indices = None
best_defender_count = 0
best_challenger_count = 0


# Conversion Factor Functions

def P_F(i, n):
    """Present-Factor: returns 1/(1+i/100)^n."""
    return 1.0 / ((1.0 + i/100.0) ** n)

def P_A(i, n):
    """Annuity factor.
       If interest rate is 0, return n.
       Else: ( (1+i/100)^n - 1 ) / ((i/100)*(1+i/100)^n)
    """
    if i == 0:
        return n
    return (math.pow(1 + i/100.0, n) - 1) / ((i/100.0) * math.pow(1 + i/100.0, n))


# Present Worth Calculation

def process_combination(def_indices, chal_indices):
    """Compute the present worth for a given combination.
       def_indices and chal_indices are lists of indices into set1 and set2.
       The combination is processed in order: first defender then challenger.
       Each item’s cost is converted as:
         cost * P_A(i_rate, period) * P_F(i_rate, cumulative)
       and the cumulative period is increased after each item.
    """
    current_pw = 0.0
    cumulative = 0
    # Process defender items.
    if def_indices is not None:
        for idx in def_indices:
            period = set1[idx]
            cost = values1[idx]
            # Multiply the cost by its annuity factor for its own period
            # and discount it back based on cumulative time so far.
            current_pw += cost * P_A(i_rate, period) * P_F(i_rate, cumulative)
            cumulative += period
    # Process challenger items.
    if chal_indices is not None:
        for idx in chal_indices:
            period = set2[idx]
            cost = values2[idx]
            current_pw += cost * P_A(i_rate, period) * P_F(i_rate, cumulative)
            cumulative += period
    return current_pw


# Update the best combination if current present worth is lower.
def update_best(def_indices, chal_indices, pw):
    global min_pw, best_defender_indices, best_challenger_indices, best_defender_count, best_challenger_count

    if pw < min_pw:
        # Copy the lists (or set them to None if empty).
        best_defender_indices = list(def_indices) if def_indices is not None else None
        best_challenger_indices = list(chal_indices) if chal_indices is not None else None
        best_defender_count = len(def_indices) if def_indices is not None else 0
        best_challenger_count = len(chal_indices) if chal_indices is not None else 0
        min_pw = pw


# Print a combination and update the best combination.
def print_combination(def_indices, chal_indices):
    pw = process_combination(def_indices, chal_indices)
    print("Combination:")
    total = 0
    if def_indices is not None:
        for idx in def_indices:
            print("  Defender - Year: {}, Value: {}".format(set1[idx], values1[idx]))
            total += set1[idx]
    if chal_indices is not None:
        for idx in chal_indices:
            print("  Challenger - Year: {}, Value: {}".format(set2[idx], values2[idx]))
            total += set2[idx]
    print("Total Years: {}".format(total))
    print("Present Worth: {:.2f}".format(pw))
    print()
    update_best(def_indices, chal_indices, pw)


# Recursive functions

def find_set2_combinations(remaining, def_indices, chal_indices, start):
    """Recursively find all combinations from challenger that add up to 'remaining' years.
       def_indices: current defender selection (list of indices) – may be None.
       chal_indices: current challenger selection (list of indices).
       start: starting index for challengers.
    """
    if remaining == 0:
        # Found a valid combination.
        print_combination(def_indices, chal_indices)
        return
    if remaining < 0:
        return

    for i in range(start, size2):
        chal_indices.append(i)
        find_set2_combinations(remaining - set2[i], def_indices, chal_indices, i)
        chal_indices.pop()


def find_set1_combinations(def_indices, start):
    """Recursively find defender combinations.
       According to the original code, a defender can be used at most once.
       When a defender is used (i.e. len(def_indices)==1), fill the gap using challenger combinations.
    """
    if len(def_indices) > 1:
        return  # Defender can be used at most once.
    
    current_sum = sum(set1[i] for i in def_indices)
    if current_sum > total_years:
        return

    if len(def_indices) == 1:
        remaining = total_years - current_sum
        if remaining >= 0:
            # Process challenger combinations.
            find_set2_combinations(remaining, def_indices, [], 0)
    
    # Allow adding defender only if not already added.
    if len(def_indices) == 0:
        for i in range(start, size1):
            def_indices.append(i)
            find_set1_combinations(def_indices, i)
            def_indices.pop()


def find_all_challenger_combinations(chal_indices, start):
    """Recursively find all combinations from challenger only that sum exactly to total_years."""
    current_sum = sum(set2[i] for i in chal_indices)
    if current_sum == total_years:
        print_combination(None, chal_indices)
        return
    if current_sum > total_years:
        return

    for i in range(start, size2):
        chal_indices.append(i)
        find_all_challenger_combinations(chal_indices, i)
        chal_indices.pop()


# Main function
def main():
    global set1, values1, set2, values2, size1, size2, total_years, i_rate

    # Fixed Defender Input (6 years)
    size1 = 6
    fixed_set1 = [1, 2, 3, 4, 5, 6]
    fixed_values1 = [53800, 52032, 54686, 58441, 62578, 66832]
    set1 = fixed_set1[:]  # copy
    values1 = fixed_values1[:]  # copy

    # Fixed Challenger Input (8 years)
    size2 = 8
    fixed_set2 = [1, 2, 3, 4, 5, 6, 7, 8]
    fixed_values2 = [77000, 61836, 57557, 56249, 56312, 57205, 58694, 60665]
    set2 = fixed_set2[:]  # copy
    values2 = fixed_values2[:]  # copy

    # User inputs.
    try:
        total_years = int(input("Enter the service life (total years): "))
    except ValueError:
        print("Invalid input for service life.")
        sys.exit(1)

    try:
        i_rate = float(input("Enter the interest rate (%): "))
    except ValueError:
        print("Invalid input for interest rate.")
        sys.exit(1)

    print("\nCombinations including defender input:")
    find_set1_combinations([], 0)

    print("Combinations using only challenger input:")
    find_all_challenger_combinations([], 0)

    print("\nOptimal Combination with Minimum Present Worth (PW = {:.2f}):".format(min_pw))
    if best_defender_indices is not None and len(best_defender_indices) > 0:
        for idx in best_defender_indices:
            print("  Defender - Year: {}, Value: {}".format(set1[idx], values1[idx]))
    if best_challenger_indices is not None and len(best_challenger_indices) > 0:
        for idx in best_challenger_indices:
            print("  Challenger - Year: {}, Value: {}".format(set2[idx], values2[idx]))


if __name__ == "__main__":
    main()