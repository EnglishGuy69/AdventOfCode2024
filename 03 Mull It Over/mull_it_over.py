import re

class MullItOver:
    def __init__(self, filename: str):
        self.input = None

        self.load_file(filename)

    def load_file(self, filename):
        with open(filename, 'r') as f:
            self.input = f.read().strip()

    def __str__(self):
        return self.input[:40] + '...' if len(self.input) > 40 else ''

    def extract_tokens(self):
        tokens = re.findall(r"mul\([0-9]{1,3},[0-9]{1,3}\)", self.input)
        return tokens

    def extract_tokens_including_do_dont(self):
        tokens = re.findall(r"mul\([0-9]{1,3},[0-9]{1,3}\)|do\(\)|don't\(\)", self.input)
        return tokens

    @staticmethod
    def _calc_mul_pairs(mul_pairs: [str]):
        return sum([int(x[0])*int(x[1]) for x in mul_pairs])


    def calc_answer_1(self):
        tokens = self.extract_tokens()
        mul_pairs = [s[4:-1].split(',') for s in tokens]
        return MullItOver._calc_mul_pairs(mul_pairs)

    def calc_answer_2(self):
        tokens = self.extract_tokens_including_do_dont()
        included_tokens = []
        include_token = True
        for t in tokens:
            if t == 'do()':
                include_token = True
            elif t == "don't()":
                include_token = False
            elif include_token:
                included_tokens.append(t)

        mul_pairs = [s[4:-1].split(',') for s in included_tokens]
        return MullItOver._calc_mul_pairs(mul_pairs)

test1_solution = MullItOver('test1.txt')
assert test1_solution.calc_answer_1() == 161

test2_solution = MullItOver('test2.txt')
assert test2_solution.calc_answer_2() == 48

solution = MullItOver('data.txt')

answer_1 = solution.calc_answer_1()
print(f'Answer 1: {answer_1}')

answer_2 = solution.calc_answer_2()
print(f'Answer 2: {answer_2}')
