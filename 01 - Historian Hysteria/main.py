'''
Author: Guy Pickering

Date: 12-01-2024

Puzzle
======
The data file contains a list of pairs of location identifiers collected by two groups.

Part 1: Compare the IDs from each list (in order from smallest to largest) and sum the total difference between the
numbers.

Part 2: Multiply each ID in list 1 by the count of the number of times the ID appears in list 2.
'''

from collections import Counter

class HistorianHysteria:
    def __init__(self, filename='data.txt'):
        self.location_1 = []
        self.location_2 = []

        self._load_data(filename)

    def _load_data(self, filename):
        with open(filename, 'r') as f:
            for row in f:
                l1, l2 = row.strip().replace('   ',' ').split(' ')
                self.location_1.append(int(l1))
                self.location_2.append(int(l2))

    def total_difference(self):
        location_pairs = zip(sorted(self.location_1), sorted(self.location_2))
        return sum([abs(l[1]-l[0]) for l in location_pairs])

    def similarity_score(self):
        l2_count = Counter(self.location_2)
        return sum([l1 * (l2_count.get(l1, 0)) for l1 in self.location_1])


solution = HistorianHysteria()

# Part 1
total_difference = solution.total_difference()
print(f'Part 1 - Total Distance:   {total_difference}')  # 1580061

# Part 2
similarity_score = solution.similarity_score()
print(f'Part 2 - Similarity Score: {similarity_score}')  # 23046913
