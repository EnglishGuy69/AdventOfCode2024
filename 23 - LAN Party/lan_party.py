'''
Author: Guy Pickering
Date: Dec 24, 2024

Puzzle:

Part 1
Storing the computers in a dictionary with the list of connected computers as a list allows fast lookup of computers.
For the first part of the question we simply filter the list of computers to the target list we are looking for,
then find the pairs of computers (computer two and computer three) to see if they are connected. We do this with
an outer loop looking at all computers connected to the target and an inner loop that looks at the computers after
that, e.g.

        A,B,C,D -> A-B, A-C, A-D, B-C, B-D, C-D

Part 2
As always, Part 2 is an optimization problem. Once the number of combinations gets large, exhaustively looking for the
longest group become computationally expensive. I had an inkling that filtering down was the key, but was not sure
how do it initially. I realized that sets could help here...if we have the set of computers connected to A, we could
then try A,B, A,C, A,D, A,B,C, A,B,D, etc. For each combination that we want to test, performing an intersect should
yield the full set. E.g. if we are testing A,B,C, we can perform:

    set(A) & set(B) & set(C) should equal [A,B,C]

With the longer combinations we will quickly drop computers as we perform the intersection and so can quickly exit that
test. Furthermore, if we start with the longest possible combinations (i.e. all computers connected to A, then all but
one, etc.) we will find the longest sooner. Starting with the shortest combinations is wasted because shorter ones will
always be a subset of longer ones. I.e. searching backwards is quicker than searching forwards and avoids performing
the same test multiple times.
'''

import copy

class LAN_Party:
    def __init__(self, filename: str):
        self.lan_pairs = {}
        self._load_data(filename)

    def _add_pair(self, m1: str, m2: str):
        if m1 not in self.lan_pairs:
            self.lan_pairs[m1] = []

        if m2 not in self.lan_pairs[m1]:
            self.lan_pairs[m1].append(m2)

    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            for row in f:
                (m1, m2) = row.strip().split('-')

                self._add_pair(m1, m2)
                self._add_pair(m2, m1)

    def _target_computers(self) -> [str]:
        """
        :return: Computers beginning with 't'
        """
        return list([c for c in self.lan_pairs.keys() if c[0] == 't'])

    def num_computers(self) -> int:
        return len(self.lan_pairs.keys())

    def get_combinations(self, computer: str) -> [(str,str)]:
        computer_list = self.lan_pairs[computer]
        n = pow(2, len(computer_list))
        combinations = []
        for i in range(1, n):
            s = bin(i)[2:].zfill(len(computer_list))
            combination = [computer]
            for j,c in enumerate(s):
                if c == '1':
                    combination.append(computer_list[j])
            combinations.append(combination)
        return combinations

    def is_combo_fully_connected(self, combo: [str]):
        full_set = set(combo)

        filtered_set = full_set
        for computer in combo:
            new_set = set(self.lan_pairs[computer] + [computer])
            filtered_set = filtered_set & new_set
            if filtered_set != full_set:
                return False

        return True

    def _find_largest_group(self, computer: str, minimum_length: int) -> str:
        combos = self.get_combinations(computer)

        combos = [c for c in combos if len(c) >= minimum_length]
        combos = sorted(combos, key=lambda x: len(x), reverse=True)

        largest_combo = None
        while combos:
            combo = combos.pop(0)
            if self.is_combo_fully_connected(combo):
                largest_combo = combo
                combos = [c for c in combos if len(c) > len(largest_combo)]
                combos = sorted(combos, key=lambda x: len(x), reverse=True)

        return largest_combo

    def find_largest_group(self) -> [str]:
        longest_group = None
        for computer in self.lan_pairs.keys():
            new_longest_group = self._find_largest_group(computer, len(longest_group) if longest_group else 0)
            if new_longest_group:
                longest_group = new_longest_group

        return longest_group

    def get_answer_1(self) -> int:
        target_computers = self._target_computers()

        answer = {}

        for target_computer in target_computers:
            peer_computers = self.lan_pairs[target_computer]
            for i,computer_two in enumerate(peer_computers):
                computer_two_connections = self.lan_pairs[peer_computers[i]]
                for j,computer_three in enumerate(peer_computers[i+1:]):
                    if computer_three in computer_two_connections:
                        answer_list = ','.join(sorted([target_computer, computer_two, computer_three]))
                        answer[answer_list] = True

        return len(list(answer.keys()))

    def get_answer_2(self) -> str:
        largest_group = self.find_largest_group()
        return ','.join(sorted(largest_group))


test_solution = LAN_Party('test.txt')
combos = sorted(test_solution.get_combinations('tc'), key=lambda x: len(x), reverse=True)
assert test_solution.get_answer_1() == 7
assert test_solution.get_answer_2() == 'co,de,ka,ta' # update

solution_1 = LAN_Party('data.txt')
answer_1 = solution_1.get_answer_1()
print(f'Task 1 Answer: {answer_1}')
answer_2 = solution_1.get_answer_2()
print(f'Task 2 Answer: {answer_2}')
