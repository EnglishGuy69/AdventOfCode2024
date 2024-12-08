import copy

class Equation:
    OPERATORS_1 = ['*', '+']
    OPERATORS_2 = ['*', '+', '||']

    def __init__(self, answer: int, values:[int]):
        self.answer = answer
        self.values = values

    def solve(self, operators: [str], all_operators: [str]):
        if len(operators) == len(self.values)-1:
            total = self.values[0]
            for i, operator in enumerate(operators):
                if operator == '*':
                    total *= self.values[i+1]
                elif operator == '+':
                    total += self.values[i+1]
                elif operator == '||':
                    total = int(str(total) + str(self.values[i+1]))
                else:
                    raise ValueError(f'operator {operator} not supported')
            return total == self.answer
        else:
            for operator in all_operators:
                if self.solve(operators=operators + [operator],
                              all_operators=all_operators):
                    return True

        return False


    def is_solvable(self, all_operators: [str]) -> bool:
        return self.solve([], all_operators)


class BridgeRepair:
    def __init__(self, filename: str):
        self.equations = []
        self._load_data(filename)

    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            for row in f:
                answer = int(row.split(':')[0])
                values = [int(x) for x in row.split(':')[1].strip().split(' ')]
                self.equations.append(Equation(answer, values))

    def _get_answer(self, all_operators: [str]):
        answer = 0
        for equation in self.equations:
            if equation.is_solvable(all_operators):
                answer += equation.answer

        return answer

    def get_answer_1(self) -> int:
        return self._get_answer(all_operators=Equation.OPERATORS_1)

    def get_answer_2(self) -> int:
        return self._get_answer(all_operators=Equation.OPERATORS_2)


test_solution = BridgeRepair('test.txt')
assert test_solution.get_answer_1() == 3749
assert test_solution.get_answer_2() == 11387

solution_1 = BridgeRepair('data.txt')
answer_1 = solution_1.get_answer_1()
print(f'Task 1 Answer: {answer_1}')

solution_2 = BridgeRepair('data.txt')
answer_2 = solution_2.get_answer_2()
print(f'Task 2 Answer: {answer_2}')