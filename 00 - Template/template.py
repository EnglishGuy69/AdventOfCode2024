'''
Author: Guy Pickering
Date:

Puzzle:

Part 1

Part 2

'''

class Template:
    def __init__(self, filename: str):
        self._load_data(filename)

    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            for row in f:
                pass

    def get_answer_1(self) -> int:
        return 0

    def get_answer_2(self) -> int:
        return 0


test_solution = Template('test.txt')
assert test_solution.get_answer_1() == 0
#assert test_solution.get_answer_2() == 0 # update

solution_1 = Template('data.txt')
answer_1 = solution_1.get_answer_1()
print(f'Task 1 Answer: {answer_1}')
answer_2 = solution_1.get_answer_2()
print(f'Task 2 Answer: {answer_2}')
