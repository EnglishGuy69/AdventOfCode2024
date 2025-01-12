'''
Author: Guy Pickering
Date:

Notes:
Part 1 is simply implementing the logic for the CPU emulator - quite straightforward.

Part 2 requires optimization as a brute-force calculation would take too long. It relies on identifying that
the process represents a finite state machine that will eventually repeat a long sequence of numbers. The key is
to identify ways in which we can 'skip' numbers from a brute force (one-by-one) search of the solution. This involves
starting with the first instruction and identifying the initial 'A' register values that yield the expected instruction.
After a certain period we will see a pattern of the deltas (difference between the successful generation of the
expected instruction). Once we identify a repeating pattern for the deltas, we reset the search and now jump forward
based on the identified sequence, looking for instructions one and two. We repeat the process, looking for patterns
in the successful generation of instructions one and two. As we detect patterns, we update the sequence of increments
of the initial 'A' register and start the search again - the starting point is always the modulus of the last known
successful initial 'A' register value with the sum of the sequence. This ensures we always pass through the last
known successful initial 'A' register value.

'''

from enum import Enum

class NoMatch(BaseException):
    pass

class ChronospacialComputer:
    class OpCodes(Enum):
        adv: 0
        bxl: 1
        bst: 2
        jnz: 3
        bxc: 4
        out: 5
        bdv: 6
        cdv: 7

    def __init__(self, filename: str):
        self.registers = {}
        self.instructions = []
        self._load_data(filename)
        self.output = []

    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            for row in f:
                if row.strip() == '':
                    break

                (register_name, value) = [field.strip()[-1] if i == 0 else int(field.strip()) for i, field in enumerate(row.strip().split(':'))]
                self.registers[register_name] = value

            self.instructions = [[int(c) for c in commands.split(',')]
                                 for i,commands in enumerate(f.read().strip().split(':'))
                                 if i == 1][0]

    def combo_operand(self, operand: int):
        if 0 <= operand <= 3: return operand
        elif operand == 4: return self.registers['A']
        elif operand == 5: return self.registers['B']
        elif operand == 6: return self.registers['C']
        else: raise ValueError(f'Unexpected value {operand}')

    def adv(self, ip: int, operand: int) -> int:
        self.registers['A'] = int(self.registers['A'] / pow(2, self.combo_operand(operand)))
        return ip+2

    def bxl(self, ip: int, operand: int) -> int:
        self.registers['B'] = self.registers['B'] ^ operand
        return ip+2

    def bst(self, ip: int, operand: int) -> int:
        self.registers['B'] = self.combo_operand(operand) % 8
        return ip+2

    def jnz(self, ip: int, operand: int) -> int:
        if self.registers['A'] == 0: return ip+2
        else: return operand

    def bxc(self, ip: int, _: int) -> int:
        self.registers['B'] = self.registers['B'] ^ self.registers['C']
        return ip+2

    def out(self, ip: int, operand: int) -> int:
        self.output.append(self.combo_operand(operand) % 8)
        return ip+2

    def bdv(self, ip: int, operand: int) -> int:
        self.registers['B'] = int(self.registers['A'] / pow(2, self.combo_operand(operand)))
        return ip+2

    def cdv(self, ip: int, operand: int) -> int:
        self.registers['C'] = int(self.registers['A'] / pow(2, self.combo_operand(operand)))
        return ip+2

    def run_program(self,
                    target_output: [int]=None) -> str:
        cmd_map = {0: self.adv,
                   1: self.bxl,
                   2: self.bst,
                   3: self.jnz,
                   4: self.bxc,
                   5: self.out,
                   6: self.bdv,
                   7: self.cdv}

        self.output = []
        ip = 0
        while ip < len(self.instructions):
            opcode = self.instructions[ip]
            operand = self.instructions[ip+1]
            ip = cmd_map[opcode](ip, operand)

            if target_output is not None:
                if self.output != target_output[:len(self.output)]:
                    assert self.output[:-1] == target_output[:len(self.output)-1]
                    raise NoMatch('Output does not match')

                if self.output == target_output:
                    break

        return ','.join([str(o) for o in self.output])

    def get_answer_1(self) -> int:
        return self.run_program()

    def find_pattern_period(self, data: [int], min_periods=3):
        diffs = [data[m + 1] - data[m] for m in range(0, len(data) - 1)]
        period_size = 1
        while True:
            reference_period = diffs[-period_size:]
            found_diff = False
            actual_min_periods = max([len(data) // period_size - 3, min_periods])
            for period in range(actual_min_periods):
                if diffs[-((period+2)*period_size):-((period+1)*period_size)] != reference_period:
                    found_diff = True
                    break

            if not found_diff:
                return reference_period

            period_size += 1
            if period_size*min_periods > len(diffs):
                return None


    def get_answer_2(self) -> int:
        sequence = [1]
        sequence_pos = 0
        match_position = 1
        initial_a = 1
        while True:
            target_output = self.instructions[:match_position]
            successful_matches = []
            while True:
                self.registers['A'] = initial_a
                try:
                    self.run_program(target_output=target_output)
                    successful_matches.append(initial_a)
                    if len(target_output) == len(self.instructions):
                        break
                except:
                    pass

                initial_a += sequence[sequence_pos]
                sequence_pos = (sequence_pos + 1) % len(sequence)

                # look for a pattern every 100 matches (more efficient than after every match). Look for at least 3
                # periods of repeat (from the end)
                LOOK_FOR_PERIOD_EVERY=1
                NUM_PERIODS_BEFORE_DETECTION=10
                if len(successful_matches) % LOOK_FOR_PERIOD_EVERY == 0:
                    diffs = [successful_matches[n+1] - successful_matches[n] for n in range(0, len(successful_matches)-1)]
                    found_diff_period = self.find_pattern_period(successful_matches, NUM_PERIODS_BEFORE_DETECTION)
                    if found_diff_period:
                        print(f"Found match for position {match_position} (repeat period = {len(found_diff_period)}, cycle period = {sum(found_diff_period)}) - [{','.join([str(d) for d in found_diff_period])}]")
                        initial_a = successful_matches[-1]
                        initial_a = initial_a % sum(found_diff_period)
                        sequence = found_diff_period
                        sequence_pos = 0
                        successful_matches = []
                        match_position += 1
                        target_output = self.instructions[:match_position]
            if len(target_output) == len(self.instructions):
                break

        return initial_a


    def __str__(self):
        return ','.join([str(o) for o in self.output])


test_solution = ChronospacialComputer('test.txt')
#assert test_solution.get_answer_1() == '4,6,3,5,6,3,5,2,1,0'

test_solution_2 = ChronospacialComputer('test2.txt')
assert test_solution_2.get_answer_2() == 117440

solution_1 = ChronospacialComputer('data.txt')
#answer_1 = solution_1.get_answer_1()
#print(f'Task 1 Answer: {answer_1}')
from datetime import datetime, timedelta
t0 = datetime.now()
answer_2 = solution_1.get_answer_2()
t1 = datetime.now()
print(f'Task 2 Answer: {answer_2} (in {(t1-t0).total_seconds()} seconds)')
