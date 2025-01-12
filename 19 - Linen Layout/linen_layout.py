'''
Author: Guy Pickering
Date:

Puzzle:

Part 1
The idea is to start at the beginning and look for the various size towel sequences that can fit the first 1, 2, 3,
etc. stripes, then recurse the remainder of the sequence to find a match. On the test data this is fine, but the full
set has way too many combinations to complete in a reasonable time.

My first step was to filter the possible towels to only include the ones that match any pattern in the sequence. Using
a dictionary probably makes this optimization not that useful. It didn't work anyway.

Next is to see that if you get half-way through matching and you get to a remainder of the sequence you have seen before
you can remember that sequence and skip it. E.g. if using towels of 1 + 4 + 1 failed (total of 6 stripes), then
2 + 2 + 2 will also fail. This will significantly reduce the number of combinations that need to be checked.

This worked!

Part 2
So this turned out to be significantly easier than I initially thought. I spent a lot of time
trying to use a graph to model the paths, b ut it was so much easier than that. The key is to start at the end, not
at the beginning. We start with the last character and see if we have a match. If so, we record the position and
the combinations (1) for use later. Next we look at the last two characters, and starting with a search for a single
character match with s[-2]. If we find it, we simply remember the number of combos from the cache for the remaining
positions. We continue moving left, one character at a time and look for 1,2,3….N length matches (up to the length
of the longest towel. Any time we find a match, we lookup the combination count of the remaining, e.g.

       12
…[ABC][xxxxxxxxxxxx]

        7
…[ABCD][xxxxxxxxxxx]

In this example, ABC matches and the cached combo count for the next position is 12 and also ABCD matches and the
cached combo count for the next position is 7. So the combo count for this start position (starting at A) is 19.

As you go back, there may be times when no combos match, so that position will have a count of zero. If ultimately
you get to position 0 (leftmost) and the count of that position is zero, then there are no solutions.

This generates a result very quickly.
'''

import copy
from graph import Graph, Node, Path

class LinenLayout:
    def __init__(self, filename: str):
        self.towels = {}
        self.patterns = []

        self._load_data(filename)

        self.max_towel_pattern_length = max([len(s) for s in list(self.towels.keys())])
        pass

    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            for towel in f.readline().strip().split(','):
                self.towels[towel.strip()] = 1

            f.readline()
            for row in f:
                self.patterns.append(row.strip())

    def find_useful_towels(self, pattern: str):
        useful_towels = {}
        for towel in self.towels:
            if pattern.find(towel) >= 0:
                useful_towels[towel] = 1

        return useful_towels

    def _generate_graph(self, pattern: str) -> Graph:
        """
        This creates a node for each position in the pattern. It then looks for towels for each position and generates
        paths between the nodes.

        :param pattern:
        :return: A graph of the possible paths within each position of the pattern
        """


        graph = Graph()

        for i in range(0, len(pattern)+1):
            permanent = i == 0 or i == len(pattern)
            node = Node(identifier=i, permanent_node=permanent)

            graph.nodes.append(node)

        for i in range(0, len(pattern)):
            from_node = graph.nodes[i]
            for l in range(1, self.max_towel_pattern_length+1):
                if i+l > len(pattern):
                    break

                to_node = graph.nodes[i+l]
                sub_pattern = pattern[i:i+l]
                if sub_pattern in self.towels:
                    path = Path(from_node, to_node, description=sub_pattern)
                    graph.paths.append(path)

        graph.remove_duplicates()
        graph.prune_nodes()
        graph.groom_nodes()
        return graph

    def calculate_number_of_paths(self, pattern: str) -> int:
        graph = self._generate_graph(pattern)
        return graph.count_paths()

    def is_possible_v2(self, pattern: str) -> int:
        graph = self._generate_graph(pattern)
        return graph.count_paths(exclude_nodes=[graph.nodes[-1]])

    def is_possible_v1(self,
                       pattern: str,
                       useful_towels: {},
                       max_towel_pattern_length: int,
                       exception_list: {} = None,
                       current_towel_combination: [] = []) -> []:

        if exception_list is None:
            exception_list = {}

        possible_towel_combinations = []

        if not pattern:
            return [current_towel_combination]

        for l in range(1, max_towel_pattern_length+1):
            new_pattern = pattern[l:]
            if new_pattern in exception_list:
                continue

            if pattern[:l] in self.towels:
                tc = copy.copy(current_towel_combination)
                tc.append(pattern[:l])

                possible_combinations =  self.is_possible_v1(new_pattern,
                                                             useful_towels=useful_towels,
                                                             max_towel_pattern_length=max_towel_pattern_length,
                                                             exception_list=exception_list,
                                                             current_towel_combination=tc)
                if possible_combinations:
                    for possible_combination in possible_combinations:
                        if possible_combination not in possible_towel_combinations:
                            possible_towel_combinations.append(copy.copy(possible_combination))
                else:
                    if new_pattern not in exception_list:
                        exception_list[new_pattern] = 1

        return possible_towel_combinations

    def get_answer_1(self) -> int:
        possible_count = 0
        for i, pattern in enumerate(self.patterns):
            useful_towels = self.find_useful_towels(pattern)
            max_towel_pattern_length = min([len(pattern), max([len(t) for t in useful_towels.keys()])])
            possible_combinations = self.is_possible_v1(pattern, useful_towels, max_towel_pattern_length)
            if possible_combinations > 0:
                possible_count += 1
            print(f'{possible_count} of {i+1}')

        return possible_count

    def get_answer_1_v2(self) -> int:
        possible_count = 0
        for i, pattern in enumerate(self.patterns):
            if self.is_possible_v2(pattern):
                possible_count += 1
            print(f'{possible_count} of {i+1}')

        return possible_count

    def get_answer_2(self) -> int:
        possible_combinations_count = 0
        for i, pattern in enumerate(self.patterns):
            possible_combinations = self.is_possible_v2(pattern)
            if possible_combinations:
                possible_combinations_count += possible_combinations
            print(f'Possible combinations after {i} patterns {possible_combinations_count}')

        return possible_combinations_count


test_solution = LinenLayout('test.txt')
assert test_solution.get_answer_1_v2() == 6
assert test_solution.get_answer_2() == 16

solution_1 = LinenLayout('data.txt')
answer_1 = solution_1.get_answer_1()
print(f'Task 1 Answer: {answer_1}')
answer_2 = solution_1.get_answer_2()
print(f'Task 2 Answer: {answer_2}')


# ToDo: Implement solution starting from the right and working left.