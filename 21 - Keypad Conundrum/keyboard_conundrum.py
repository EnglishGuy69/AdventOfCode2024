'''
Author: Guy Pickering
Date: 2025-01-09

Notes:
So I realized fairly early on a couple of things. Firstly, that if you have two ways to get from one key to another
(e.g. <<^ and ^<<) we ideally want to decide which is the better when we iterate over and over. Secondly, if we
iterate a large number of times, we can't maintain the full string of commands - we must instead 'compress' the
keystrokes and keep track of the number of times each set of keystrokes exist in a string.

Because every command ends in an 'A', it means that the order of command sets (ending in an 'A') can occur in any order.
So: ^<<A>>vA is the same as >>vA^<<A, which can be stored as {'^<<A': 1, '>>vA': 1}. This allows the expansion of
commands to a series of other command sets ('...A..A...A...A') which can themselves be stored in 'compressed' form.

It is also clear that having more 'runs' of commands is better than more short combinations (e.g. <<vvA is better than
<v<vA). For that reason, our initial combinations are limited to a maximum of 2 options for those key-to-key
instructions that allow it (and don't go through the space key).

What I did, was use uncompressed expansion of the multiple options for key-to-key instructions to determine where
one expands slower (i.e. short sets of instructions) as we iterate. Then use the compressed expansion to do the 25x
iterations.

This problem took me a long time because it was really tricky to visualize the arrays of instructions before I limited
each key-to-key instruction set to a single (optimal) instruction. I eventually got a solution that worked for part 1
but for some reason got an incorrect answer for part 2. I finally broke down and searched Reddit which confirmed I had
identified correctly the way to approach the problem, but there must have been a defect in my code. So I eventually
started a new file and re-wrote the code from scratch. This second time through yielded the correct answer for both
parts and finally allowed me to complete Day 25.

'''

from itertools import permutations

class KeyPad:
    dx_dy = {'>': (1,0),
             '<': (-1,0),
             '^': (0,-1),
             'v': (0,1)}

    def __init__(self,
                 keys: str,
                 width: int,
                 direction_keypad: "KeyPad"):
        self.keys = [[k for k in keys[i:i+width]] for i in range(0,len(keys), width)]
        perms = list(permutations(keys.replace(' ',''), r=2))
        directions_list = [(f,t,self._generate_directions(f,t)) for (f,t) in perms]
        self.directions = {}
        for (from_key, to_key, directions) in directions_list:
            self.directions[(from_key, to_key)] = directions

        self._optimize_directions(direction_keypad)

    def _optimize_directions(self, direction_keypad: "KeyPad"):
        multi_direction_key_pairs = [d for d in self.directions if len(self.directions[d]) > 1]
        for key_pairs in multi_direction_key_pairs:
            directions = self.directions[key_pairs]
            expanded_directions = [(direction, [direction]) for direction in directions]
            iterations = 0
            while True:
                iterations += 1
                new_expanded_directions = []
                for i, (direction, expanded_direction_list) in enumerate(expanded_directions):
                    new_expanded_directions.append((direction, direction_keypad.expand_instructions_list(expanded_direction_list)))

                expanded_directions = new_expanded_directions
                min_expanded_directions = {}
                min_overall_length = None
                for (direction, expanded_direction_list) in expanded_directions:
                    min_expanded_direction = min([len(d) for d in expanded_direction_list])
                    if min_overall_length is None or min_overall_length > min_expanded_direction:
                        min_overall_length = min_expanded_direction
                    min_expanded_directions[direction] = min_expanded_direction

                shortest_directions = [d for d in min_expanded_directions
                                       if min_expanded_directions[d] == min_overall_length]

                if len(shortest_directions) == 1:
                    self.directions[key_pairs] = [shortest_directions[0]]
                    break

    def _position(self, key: str):
        return [(x,y) for x in range(len(self.keys[0])) for y in range(len(self.keys)) if self.keys[y][x] == key][0]

    def expand_instructions_list(self, instructions: [str]) -> [str]:
        ret = []
        for keys in instructions:
            ret.extend(self.expand_instructions(keys))
        return ret

    def get_directions(self,prior_key: str, next_key: str):
        if prior_key == next_key:
            return 'A'
        else:
            return self.directions[(prior_key, next_key)]

    @staticmethod
    def compress_instructions(instructions: str) -> {(str, int)}:
        ret = {}
        for instruction in [i+'A' for i in instructions.split('A')][:-1]:
            if instruction in ret:
                ret[instruction] += 1
            else:
                ret[instruction] = 1
        return ret

    @staticmethod
    def length_of_compressed_instructions(compressed_instructions: dict):
        return sum([len(s)*compressed_instructions[s] for s in compressed_instructions])

    def expand_instructions_compressed(self, compressed_instructions: dict):
        ret = {}
        for instruction in compressed_instructions:
            instruction_count = compressed_instructions[instruction]
            expanded_instructions = self.expand_instructions(instruction)
            assert len(expanded_instructions) == 1
            new_compressed_instructions = KeyPad.compress_instructions(expanded_instructions[0])
            for new_compressed_instruction in new_compressed_instructions:
                if new_compressed_instruction in ret:
                    ret[new_compressed_instruction] += new_compressed_instructions[new_compressed_instruction]*instruction_count
                else:
                    ret[new_compressed_instruction] = new_compressed_instructions[new_compressed_instruction]*instruction_count
        return ret

    def expand_instructions(self, keys: str) -> [str]:
        prior_key = 'A'
        instructions = []
        instructions = self.get_directions(prior_key, keys[0])
        prior_key = keys[0]
        for current_key in keys[1:]:
            directions = self.get_directions(prior_key, current_key)
            for direction in directions:
                new_instructions = [instruction+direction for instruction in instructions for direction in directions]
            instructions = new_instructions
            prior_key = current_key
        return instructions

    def _generate_directions(self, from_key: str, to_key: str) -> [str]:
        (x1,y1) = self._position(from_key)
        (x2,y2) = self._position(to_key)
        directions = list(set([('>'*(x2-x1) if x2 > x1 else '<'*(x1-x2)) +
                               ('v'*(y2-y1) if y2 > y1 else '^'*(y1-y2)),
                               ('v' * (y2 - y1) if y2 > y1 else '^' * (y1 - y2)) +
                               ('>' * (x2 - x1) if x2 > x1 else '<' * (x1 - x2))
                               ]))
        directions = [d+'A' for d in directions if d != ' ' and self._are_valid_directions(from_key, d)]

        return directions

    def _are_valid_directions(self, from_key: str, directions: str) -> bool:
        (x,y) = self._position(from_key)
        for d in directions:
            (dx,dy) = KeyPad.dx_dy[d]
            (x,y) = (x+dx, y+dy)
            if self.keys[y][x] == ' ':
                return False
        return True

    def __str__(self):
        return ', '.join(''.join(row) for row in self.keys)

class KeyPadDirectional(KeyPad):
    def __init__(self):
        super().__init__(' ^A<v>', 3, self)

class KeyPadNumeric(KeyPad):
    def __init__(self):
        dk = KeyPadDirectional()
        super().__init__('789456123 0A', 3, dk)

class KeyPadConundrum:
    def __init__(self):
        pass

    def get_answer_1(self, filename: str, iterations: int):
        kn = KeyPadNumeric()
        kd = KeyPadDirectional()

        codes = []
        with open(filename, 'r') as f:
            for row in f:
                codes.append(row.strip())

        complexity = 0
        for code in codes:
            instructions = kn.expand_instructions(keys=code)
            assert len(instructions) == 1
            compressed_instructions = KeyPad.compress_instructions(instructions[0])

            for i in range(iterations):
                compressed_instructions = kd.expand_instructions_compressed(compressed_instructions)

            complexity += int(code[:-1]) * KeyPad.length_of_compressed_instructions(compressed_instructions)

        return complexity



solution = KeyPadConundrum()
test_1 = solution.get_answer_1('test.txt', 2)
assert test_1 == 126384

answer_1 = solution.get_answer_1('data.txt', 2)
print(f'Answer 1: {answer_1}')

answer_2 = solution.get_answer_1('data.txt', 25)
print(f'Answer 2: {answer_2}')

