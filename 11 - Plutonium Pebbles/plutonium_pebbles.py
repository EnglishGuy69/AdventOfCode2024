'''
Author: Guy Pickering
Date:

Puzzle:

Part 1

Part 2

'''

import copy

class Pebble:
    pebbles = {}
    iteration_level = -1
    depth = 0

    def __init__(self, pebble_number: str):
        self.pebble_number = pebble_number
        self.children = []
        self._count_cache = {}

    def _as_string(self):
        s = '[' + ', '.join([f"'{x.pebble_number}'" for x in self.children]) + ']'
        return s

    def __str__(self):
        return self._as_string()

    def _add_child(self, pebble_number: str):
        if pebble_number in Pebble.pebbles:
            self.children.append(Pebble.pebbles[pebble_number])
        else:
            new_pebble = Pebble(pebble_number=pebble_number)
            self.pebbles[pebble_number] = new_pebble
            self.children.append(new_pebble)
            pass

    def get_count(self, iterations: int, depth=1):
        if depth > Pebble.depth:
            Pebble.depth = depth
            print(f'Depth: {depth}', end='\r')

        if len(self.children) == 0:
            self.populate_children()

        if iterations == 0:
            return 1
        elif iterations == 1:
            return len(self.children)
        elif iterations in self._count_cache:
            return self._count_cache[iterations]
        else:
            total = 0
            child: Pebble
            for child in self.children:
                total += child.get_count(iterations-1, depth+1)
            self._count_cache[iterations] = total
            return total

    def populate_children(self):
        if self.pebble_number == '0':
            new_pebbles = ['1']
        elif len(self.pebble_number) % 2 == 0:
            pebble_1 = str(int(self.pebble_number[0:len(self.pebble_number) // 2]))
            pebble_2 = str(int(self.pebble_number[len(self.pebble_number) // 2:]))
            new_pebbles = [pebble_1, pebble_2]
        else:
            new_pebbles = [str(int(self.pebble_number) * 2024)]

        for new_pebble in new_pebbles:
            self._add_child(new_pebble)

# class Pebbles:
#     def __init__(self, pebbles: [str]):
#         self.pebbles_dict = {}
#         for pebble in pebbles:
#             if pebble in self.pebbles_dict:
#                 self.pebbles_dict[pebble] += 1
#             else:
#                 self.pebbles_dict[pebble] = 1
#
#     def num_pebbles(self):
#         return sum([x for x in self.pebbles_dict.values()])
#
#     def __str__(self):
#         return str(self.pebbles_dict) + f' ({self.num_pebbles()})'

class PlutoniumPebbles:
    def __init__(self, filename: str):
        self.pebbles = []
        self._load_data(filename)

    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            s = f.read()
            self.pebbles = s.strip().split(' ')

#     def apply_rules(self, pebbles_in: Pebbles) -> Pebbles:
#
#         pebbles_out = copy.deepcopy(pebbles_in)
#
#         keys = list(pebbles_in.pebbles_dict.keys())
#         for pebble in keys:
#             num_pebbles = pebbles_in.pebbles_dict[pebble]
#             for i in range(0, num_pebbles):
#                 if pebble == '0':
#                     new_pebbles = ['1']
#                 elif len(pebble) % 2 == 0:
#                     pebble_1 = str(int(pebble[0:len(pebble)//2]))
#                     pebble_2 = str(int(pebble[len(pebble)//2:]))
#                     new_pebbles = [pebble_1, pebble_2]
#                 else:
#                     new_pebbles = [str(int(pebble) * 2024)]
#
# #                print(f'{pebble} -> {str(new_pebbles)}')
#
#                 for new_pebble in new_pebbles:
#                     if new_pebble in pebbles_out.pebbles_dict:
#                         pebbles_out.pebbles_dict[new_pebble] += 1
#                     else:
#                         pebbles_out.pebbles_dict[new_pebble] = 1
#
#                 if pebble in pebbles_out.pebbles_dict:
#                     pebbles_out.pebbles_dict[pebble] -= 1
#                     if pebbles_out.pebbles_dict[pebble] == 0:
#                         del pebbles_out.pebbles_dict[pebble]
#
# #        print('')
#         return pebbles_out

        # while True:
        #     if i == len(pebbles):
        #         return pebbles
        #
        #     pebble = pebbles[i]


    def get_answer_1(self, num_blinks: int) -> int:
        pebbles = []
        total = 0
        for p in self.pebbles:
            pebble = Pebble(p)
            total += pebble.get_count(num_blinks)


        return total

        # total = 0
        # for
        #
        # for i in range(0, num_blinks):
        #     pebbles = self.apply_rules(pebbles)
        #     print(f'{i} of {num_blinks}', end='\r')
        #
        # answer = sum([x for x in pebbles.pebbles_dict.values()])
        # return answer

    def get_answer_2(self) -> int:
        pass


#test_solution = PlutoniumPebbles('test.txt')
#assert test_solution.get_answer_1(1) == 7

test2_solution = PlutoniumPebbles('test2.txt')
assert test2_solution.get_answer_1(6) == 22
assert test2_solution.get_answer_1(25) == 55312 # update

solution_1 = PlutoniumPebbles('data.txt')
answer_1 = solution_1.get_answer_1(25)
print(f'Task 1 Answer: {answer_1}')

solution_2 = PlutoniumPebbles('data.txt')
answer_2 = solution_2.get_answer_1(75)
print(f'Task 2 Answer: {answer_2}')