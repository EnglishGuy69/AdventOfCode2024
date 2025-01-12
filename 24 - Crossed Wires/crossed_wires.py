'''
Author: Guy Pickering
Date:

Puzzle:

Part 1

Part 2
I could not find a generic way to solve Part 2. I had to use the knowledge that addition using gates is a
well-structured process where each bit is calculated using the 'sum' of the two incoming bits, plus the
carryover of the prior bit. Once you get beyond bit one, the general structure is:

XOR
    SUM[n]              <- x[n] XOR y[n]
    OR
        CARRY[n-1]      <- x[n-1] AND y[n-1]
        AND
            ...

You have to start searching for errors with the least significant bit (z00) and work up. As each bit is confirmed
to be correct, the only error that can be found in the next bit is in this first section of XOR...OR...AND. I did not
automate the solution here initially (I'll go back and do that later). I ran a set of tests, setting the x bit and y
bit to 1 sequentially   ( ..0001 + ..0001, ..0010 + ..0001, ..0100 + ..0001, etc.) to find the first bit that had
an error. Then for each error bit I looked at the first section to identify what was wrong and I manually found the
right fix.

'''

def operator_or(a: int, b: int):
    return a or b

def operator_and(a: int, b: int):
    return a and b

def operator_xor(a: int, b: int):
    return a ^ b


class Component:
    def __init__(self, output_name: str):
        self._output_name = output_name
        self.error_count = 0

        self._override_name = None

    @property
    def override_name(self):
        return self._override_name

    def set_override_name(self, override_name: str):
        self._override_name = override_name

    @property
    def depth(self) -> int:
        raise NotImplementedError('Override in derived class')

    @property
    def output_name(self) -> str:
        return self._output_name

    def set_output_name(self, output_name: str):
        self._output_name = output_name

    @property
    def value(self) -> int:
        raise NotImplementedError('value() not implemented')

    def set_value(self, v: int):
        raise NotImplementedError('value() not implemented')

    @property
    def level(self) -> int:
        raise NotImplementedError('level() not implemented')

    def reset_error_count(self):
        self.error_count = 0

    def reset_cache(self):
        raise NotImplementedError('reset_cache() not implemented')

    def reset_level(self):
        raise NotImplementedError('reset_level() not implemented')

    def record_error(self):
        raise NotImplementedError('apply_difference() not implemented')

    def __str__(self):
        return f'{self.output_name} {self.value}'

    def render_backwards(self, level=0):
        raise NotImplementedError('Implement in derived class')


class Input(Component):
    def __init__(self, output_name: str, value: int):
        super().__init__(output_name)
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    @property
    def level(self) -> int:
        return 0

    @property
    def depth(self) -> int:
        return 0

    def reset_cache(self):
        pass

    def reset_level(self):
        pass

    def set_value(self, v: int):
        self._value = v

    def record_error(self):
        pass

    def __str__(self):
        return f'[0] {self.output_name} {self.value}'

    def render_backwards(self, level=0):
        print(f'{"    "*level} [{self.output_name}] = {self.value}')


class LogicGate(Component):
    def __init__(self,
                 arg1_name: str,
                 arg2_name: str,
                 operator: str,
                 output_name: str,
                 gates: "Gates"):
        super().__init__(output_name)

        self.arg1_name: str = arg1_name
        self.arg2_name: str = arg2_name
        self._output_name: str = output_name
        self.gates: Gates = gates

        self._cached_value: int|None = None
        self._cached_arg1_gate: Component | None = None
        self._cached_arg2_gate: Component | None = None
        self._cached_level: int | None = None

        self.operator_name: str = operator
        if self.operator_name == 'AND':
            self.operator = operator_and
        elif self.operator_name == 'OR':
            self.operator = operator_or
        elif self.operator_name == 'XOR':
            self.operator = operator_xor
        else:
            raise ValueError(f'{self.operator} not recognized')

    def reset_cache(self):
        self._cached_value: int|None = None
        self._cached_arg1_gate: Component | None = self.gates.find_gate(self.arg1_name)
        self._cached_arg2_gate: Component | None = self.gates.find_gate(self.arg2_name)

    @property
    def depth(self) -> int:
        arg1_depth = self.arg1_gate.depth
        arg2_depth = self.arg1_gate.depth
        max_depth = max([arg1_depth, arg2_depth])
        return max_depth + 1

    def reset_level(self):
        self._set_level()

    @property
    def level(self):
        return self._cached_level

    def set_value(self, v: int):
        raise NotImplementedError('You cannot set the value of a logic node')

    def _set_level(self):
        gate = self
        level = 0
        while True:
            if gate.output_name.startswith('x') or gate.output_name.startswith('y'):
                self._cached_level = level
                return
            else:
                gate = gate.arg1_gate
                level += 1

    @property
    def _value(self) -> int:
        val1 = self.arg1_value
        val2 = self.arg2_value

        return self.operator(val1, val2)

    @property
    def value(self) -> int:
        return self._value

        # if self.cached_value is None:
        #     self.cached_value = self._value
        #
        # return self.cached_value

    def record_error(self):
        self.error_count += 1
        self.arg1_gate.record_error()
        self.arg2_gate.record_error()

    @property
    def arg1_gate(self):
        if self._cached_arg1_gate is None:
            self.reset_cache()
        return self._cached_arg1_gate

    @property
    def arg2_gate(self):
        if self._cached_arg2_gate is None:
            self.reset_cache()
        return self._cached_arg2_gate

    @property
    def arg1_value(self):
        if self._cached_arg1_gate is None:
            self.reset_cache()
        return self._cached_arg1_gate.value

    @property
    def arg2_value(self):
        if self._cached_arg2_gate is None:
            self.reset_cache()
        return self._cached_arg2_gate.value

    def __str__(self):
        error_str = '' if self.error_count == 0 else f' ({self.error_count} errors)'
        return f'[{self.level}] {self.output_name} {self.arg1_value} {self.operator_name} {self.arg2_value} = {self.value} {error_str}'

    def render_backwards(self, level=0):
        """
            0 (ABC) AND (DEF) 1 = 0 (Z01)
                1 XYZ AND RST 0 = 0 (ABC)

        :return:
        """
        if self.override_name:
            print(f'{"    " * level} {self.override_name} ({self.output_name})')
            return

        arg1_name = self.arg1_gate.output_name
        arg2_name = self.arg2_gate.output_name
        arg1_value = self.arg1_value
        arg2_value = self.arg2_value
        print(f'{"    "*level} ({arg1_name}) {arg1_value} {self.operator_name} {arg2_value} ({arg2_name}) = {self.value} ({self.output_name})')
        if self.arg1_gate.depth < self.arg2_gate.depth:
            self.arg1_gate.render_backwards(level+1)
            self.arg2_gate.render_backwards(level+1)
        else:
            self.arg2_gate.render_backwards(level+1)
            self.arg1_gate.render_backwards(level+1)


class Gates:
    def __init__(self):
        self.gates = {}
        self.swap_list = []

    def add_gate(self, gate: Component):
        self.gates[gate.output_name] = gate

    def find_gate(self, output_name: str):
        return self.gates[output_name]

    def find_gate_from_detail(self, input1: str, input2: str, operator_name: str):
        return [g
                for g in self.gates.values()
                if isinstance(g, LogicGate) and \
                set([g.arg1_name, g.arg2_name]) == set([input1, input2]) and \
                g.operator_name == operator_name]

    @property
    def all_gate_names(self):
        return list(self.gates.keys())

    @property
    def all_gates(self):
        return list(self.gates.values())

    def reset_caches(self):
        gate: Component
        for gate in self.all_gates:
            gate.reset_cache()

        for gate in self.all_gates:
            gate.reset_level()

    def gates_by_level(self):
        level = 0
        levels = []
        while True:
            level_list = [g for g in self.all_gates if g.level == level]
            if not level_list:
                break
            else:
                levels.append(level_list)
            level += 1

        return levels

    def __str__(self):
        z_bits = ''.join([str(self.find_gate(g).value) for g in sorted(self.all_gate_names, reverse=True) if g.startswith('z')])
        return z_bits

    def render(self):
        gates_by_level = self.gates_by_level()
        max_gates = max([len(gates) for gates in gates_by_level])

        padding = 4
        widths_by_level = [max([len(str(g))+padding for g in gates]) for gates in gates_by_level]
        for i in range(0, max_gates):
            for l,level in enumerate(gates_by_level):
                if i >= len(level):
                    print(' '*widths_by_level[l])
                    break
                else:
                    print(f'{str(level[i]): >{widths_by_level[l]}}')

    def get_output_binary(self):
        output_gates = sorted([g.output_name for g in self.all_gates if g.output_name.startswith('z')], reverse=True)
        return ''.join(['1' if self.gates[gg].value else '0' for gg in output_gates])

    def get_output_diff(self, expected_value: str):
        actual_bin = self.get_output_binary()
        assert len(actual_bin) == len(expected_value)

        return ''.join(['1' if expected_value[i] == actual_bin[i] else 'x' for i in range(0, len(actual_bin))])

    def swap(self, output_name_1: str, output_name_2: str):
        gate_1:Component = self.find_gate(output_name_1)
        gate_2:Component = self.find_gate(output_name_2)

        gate_1.set_output_name(output_name_2)
        gate_2.set_output_name(output_name_1)
        self.gates[output_name_1] = gate_2
        self.gates[output_name_2] = gate_1
        self.reset_caches()
        self.swap_list.append(output_name_1)
        self.swap_list.append(output_name_2)

    @property
    def all_swapped(self):
        return ','.join(sorted(self.swap_list))

    @property
    def levels(self):
        levels = set([g.level for g in self.all_gates])
        return sorted(list(levels))

class CrossedWires:
    def __init__(self, filename: str):
        self.initial_values = {}
        self.gates = Gates()

        self._load_data(filename)

    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            for row in f:
                if row.strip() == '':
                    break
                (name, value) = [s.strip() for s in row.strip().split(':')]
                self.gates.add_gate(Input(name, int(value)))

            for row in f:
                if row[0] == '#':
                    continue
                (logic, output_name) = [s.strip() for s in row.strip().split('->')]
                (arg1, operator, arg2) = [s.strip() for s in logic.strip().split(' ')]
                gate = LogicGate(arg1, arg2, operator, output_name, self.gates)
                self.gates.add_gate(gate)

            self.gates.reset_caches()

    def get_answer_1(self) -> int:
        output_gates = [self.gates.gates[gate_name] for gate_name in list(self.gates.gates.keys()) if gate_name.startswith('z')]
        output_gates = sorted(output_gates, key=lambda g: g.output_name, reverse=True)
        binary_number = ''.join([str(g.value) for g in output_gates])
        return int(binary_number,2)

    def _set_initial(self, v: int, prefix: str):
        bits = len([g for g in self.gates.all_gates if g.output_name.startswith(prefix)])
        v_binary = bin(v)[2:].zfill(bits)
        self._set_initial_bin(v_binary, prefix)

    def _set_initial_bin(self, v_binary: str, prefix: str):
        bits = len([g for g in self.gates.all_gates if g.output_name.startswith(prefix)])
        for i in range(0, bits):
            v_name = f'{prefix}{i:02}'
            gate: Component = self.gates.find_gate(v_name)
            bit_value = int(v_binary[-i-1:-i] if i != 0 else v_binary[-1:])
            gate.set_value(bit_value)

    def record_error(self, x: int, y: int, expected_output_bin: str):
        self.set_initial_x(x)
        self.set_initial_y(y)
        actual_output = self.gates.get_output_binary()


    def reset_cache(self):
        for gate_name in self.gates.gates.keys():
            gate = self.gates.gates[gate_name]
            gate._cached_value = None

    def num_bits(self, prefix: str):
        return len([g for g in self.gates.all_gates if g.output_name.startswith(prefix)])

    def max_value(self, prefix: str):
        return pow(2, self.num_bits(prefix))

    def set_initial_x(self, x: int):
        self._set_initial(x, 'x')

    def set_initial_y(self, y: int):
        self._set_initial(y, 'y')

    def set_initial_x_bin(self, x_bin: str):
        self._set_initial_bin(x_bin, 'x')

    def set_initial_y_bin(self, y_bin: str):
        self._set_initial_bin(y_bin, 'y')

    @property
    def x_bits(self):
        return self.num_bits('x')

    @property
    def y_bits(self):
        return self.num_bits('y')

    @property
    def z_bits(self):
        return self.num_bits('z')

    def test_input_output(self):
        tests = [('100000', '100000', '100000'),
                 ('010000', '010000', '010000'),
                 ('001000', '001000', '001000'),
                 ('000100', '000100', '000100'),
                 ('000010', '000010', '000010'),
                 ('000001', '000001', '000001'),
                 ]

        for test in tests:
            self.reset_cache()
            (x,y,expected_results) = test
            self._compare_results(int(x,2), int(y,2), expected_results)

    def calc_expected_value_binary(self, x: int, y: int, operator: str, output_bits: int):

        if operator == '&':
            expected_value = x & y
        elif operator == '+':
            expected_value = x + y
        else:
            raise NotImplementedError('Only & and + supported')

        return bin(expected_value)[2:].zfill(output_bits)

    def diff(self, a_bin: str, b_bin: str):
        if len(a_bin) < len(b_bin):
            a_bin = a_bin.zfill(len(b_bin)-len(a_bin))
        elif len(b_bin) < len(a_bin):
            b_bin = b_bin.zfill(len(a_bin)-len(b_bin))

        s = ''.join(['1' if a_bin[i] == b_bin[i] else 'x' for i in range(0, len(a_bin))])
        return s

    def _calc_diff(self, x_bin: str, y_bin: str, operator: str, z_bits: int):
        x = int(x_bin, 2)
        y = int(y_bin, 2)
        self.set_initial_x_bin(x_bin)
        self.set_initial_y_bin(y_bin)
        expected_z = self.calc_expected_value_binary(x, y, operator, z_bits)
        actual_z = self.gates.get_output_binary()
        diff = self.gates.get_output_diff(expected_z)

        return expected_z, actual_z, diff

    def _extract_children_in_order(self, gate: LogicGate) -> (Component, Component):
        gate1 = gate.arg1_gate
        gate2 = gate.arg2_gate

        if gate1.depth < gate2.depth:
            return (gate1, gate2)
        else:
            return (gate2, gate1)

    def _check_structure_bit_0(self) -> bool:
        gate_zero: LogicGate = self.gates.find_gate('z00')

        if gate_zero.operator_name != 'XOR':
            return False

        if set([gate_zero.arg1_name, gate_zero.arg2_name]) != set['x00', 'y00']:
            return False

    def _check_structure(self, root_gate: LogicGate, bit_number: int) -> bool:
        sum_gate: LogicGate
        or_gate: LogicGate
        carry_gate: LogicGate
        and_gate: LogicGate

        if bit_number == 1:
            return True

        (sum_gate, or_gate) = self._extract_children_in_order(root_gate)

        (carry_gate, and_gate) = self._extract_children_in_order(or_gate)

        if not sum_gate.override_name.startswith('SUM['): return False
        if not int(sum_gate.override_name[4:-1]) == bit_number: return False

        if not carry_gate.override_name.startswith('CARRY['): return False
        if not int(carry_gate.override_name[6:-1]) == bit_number-1: return False

        return self._check_structure(root_gate=and_gate, bit_number=bit_number-1)

    def check_structure(self) -> (bool, int):
        if not self._check_structure_bit_0(): return (False, 0)

        for i in range(1, self.z_bits):
            root_gate: LogicGate = self.gates.find_gate(f'z{i:02}')

            if root_gate.operator_name != 'XOR':
                print('Root gate is not XOR')
                return (False, i)

            if not self._check_structure(root_gate, i):
                return (False, i)

        return (True, None)

    def _fix_bit(self, bad_bit):
        expected_sum_gate: LogicGate
        # ToDo


    def run_scan_test(self, operator: str):
        g: Component
        for g in self.gates.all_gates:
            g.reset_error_count()

        z_bits = self.z_bits

        carry_dict = {}
        sum_dict = {}
        sum0 = self.gates.find_gate('z00')
        sum0.set_override_name('SUM[0]')
        sum_dict[0] = sum0

        sum1 = self.gates.find_gate_from_detail('x01','y01','XOR')[0]
        sum1.set_override_name('SUM[1]')
        sum_dict[1] = sum1

        carry0 = self.gates.find_gate_from_detail('x00','y00','AND')[0]
        carry0.set_override_name('CARRY[0]')
        carry_dict[0] = carry0

        for i in range(1, self.x_bits):
            carry_n_list = self.gates.find_gate_from_detail(f'x{i:02}',f'y{i:02}', 'AND')
            if len(carry_n_list) > 1:
                raise ValueError(f'Carry for x{i:02} AND y{i:02} has multiple values')
            elif len(carry_n_list) == 0:
                raise ValueError(f'Carry for x{i:02} AND y{i:02} has no values')

            carry_n_list[0].set_override_name(f'CARRY[{i}]')

            sum_n_list = self.gates.find_gate_from_detail(f'x{i:02}',f'y{i:02}', 'XOR')
            if len(sum_n_list) > 1:
                raise ValueError(f'Carry for x{i:02} XOR y{i:02} has multiple values')
            elif len(sum_n_list) == 0:
                raise ValueError(f'Carry for x{i:02} XOR y{i:02} has no values')

            sum_n_list[0].set_override_name(f'SUM[{i}]')



        gates_swapped = []
        while True:
            (good_structure, bad_bit) = self.check_structure()
            if good_structure:
                break

            self._fix_bit(bad_bit)

        self.gates.swap('hbs','kfp')  # z09
        self.gates.swap('z18','dhq')  # z18
        self.gates.swap('pdg','z22')  # z22
        self.gates.swap('jcp','z27')  # z27

        print(self.gates.all_swapped)

        g = self.gates.find_gate_from_detail('x00','y00','XOR')
        matches = 0
        non_matches = 0
        for xp in range(0, self.x_bits):
            for yp in range(0, self.y_bits):
                self.reset_cache()
                x_bin = '0'*(self.x_bits-xp-1)+'1'+'0'*xp
                y_bin = '0'*(self.y_bits-yp-1)+'1'+'0'*yp


                expected_z1, actual_z1, diff1 = self._calc_diff(x_bin, y_bin, operator, z_bits)
                expected_z2, actual_z2, diff2 = self._calc_diff(y_bin, x_bin, operator, z_bits)


                if diff1.find('x') < 0:
                    matches += 1
                else:
                    non_matches += 1
                    print(f'X:    {x_bin}')
                    print(f'Y:    {y_bin}')
                    print(f'Act: {actual_z1}')
                    print(f'Exp: {expected_z1}')
                    print('---------------------------------------------')

                    print(f'X:    {y_bin}')
                    print(f'Y:    {x_bin}')
                    print(f'Act: {actual_z2}')
                    print(f'Exp: {expected_z2}')
                    print('==============================================')
                    pass

                for i,c in enumerate(diff1):
                    if c != '1':
                        i_lsb = len(diff1)-i-1
                        gate: Component = self.gates.find_gate(f'z{i_lsb:02}')
                        gate.render_backwards(0)
                        print('=================================')
                        gate.record_error()

        return matches, non_matches

    def run_full_test(self, operator: str) -> (int, int):
        g: Component
        for g in self.gates.all_gates:
            g.reset_error_count()

        max_x = self.max_value('x')
        max_y = self.max_value('y')
        z_bits = self.z_bits

        matches = 0
        non_matches = 0
        for x in range(0, max_x):
            for y in range(0, max_y):
                self.reset_cache()
                self.set_initial_x(x)
                self.set_initial_y(y)
                expected_z = self.calc_expected_value_binary(x,y,operator,z_bits)
                diff = self.gates.get_output_diff(expected_z)

                if diff.find('x') < 0:
                    matches += 1
                else:
                    non_matches += 1

                for i,c in enumerate(diff):
                    if c != '1':
                        i_lsb = len(diff)-i-1
                        gate: Component = self.gates.find_gate(f'z{i_lsb:02}')
                        gate.record_error()

        return matches, non_matches

    def attempt_repair(self, operator: str):
        self.run_scan_test(operator)



        layer_gate_swaps = []
        for level in self.gates.levels:
            if level == 0:
                continue

            level_gates = [g for g in self.gates.all_gates if g.level == level]
            gate_errors = sorted([(g.output_name, g.error_count) for g in level_gates], key=lambda g: g[1], reverse=True)



    def _compare_results(self, x: int, y: int, expected_result: str, operator: str) -> (str, str, str, str, str):
        self.reset_cache()
        self.set_initial_x(x)
        self.set_initial_y(y)
        x_bin = bin(x)[2:].zfill(self.x_bits)
        y_bin = bin(y)[2:].zfill(self.y_bits)
        actual_result = str(self.gates)
        diff = ''.join(['1' if expected_result[i] == actual_result[i] else 'x' for i in range(0, len(actual_result))])
        s = f'{x_bin} {operator} {y_bin} = {actual_result} (act) vs {expected_result} (exp), diff: {diff}'
        print(s)

        wrong_gates: [LogicGate] = [self.gates.gates[f'z{i:02}'] for i in range(0, self.z_bits) if diff[self.z_bits - i - 1] == 'x']
        if wrong_gates:
            wrong_gate: LogicGate = wrong_gates[0]
            arg1_gate = wrong_gate.arg1_gate

        return (x_bin, y_bin, actual_result, expected_result, diff)

    def get_answer_2(self) -> int:
        results = []
        for x in range(0, pow(2, self.x_bits)):
            for y in range(0, pow(2, self.y_bits)):
                if x+y >= pow(2, self.z_bits):
                    continue

                result = self._compare_results(x, y, bin(x + y)[2:].zfill(self.z_bits), '&')
                results.append(result)
        return 0

# test2_solution = CrossedWires('test2.txt')
# test2_solution.get_answer_2()

test_solution = CrossedWires('test.txt')
test_solution.gates.render()
assert test_solution.get_answer_1() == 2024
#test_solution.attempt_repair('+')
#(match, non_match) = test_solution.run_full_test('+')


# assert test_solution.get_answer_2() == 0 # update

solution_1 = CrossedWires('data.txt')
answer_1 = solution_1.get_answer_1()
print(f'Task 1 Answer: {answer_1}')
solution_1.attempt_repair(operator='+')

# 100 0000 0000 0000 0000