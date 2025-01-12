'''
Author: Guy Pickering
Date: Dec-27-2024

Puzzle:

Part 1
Part one was reasonably straightforward, simply follow the instructions on the calculation and generate the secret
after 2,000 iterations.

Part 2
Part 2 depended on pre-calculating the combinations of 4 deltas together with the associated price. The key was to use
dictionaries for fast lookup. Then it was a brute force attack on the various combinations - keeping track of the
previously checked combinations. The process took < 1 min.
'''

import copy
import os

class MonkeyMarket:
    def __init__(self, filename: str, price_filename: str, force_reprice=False):
        self.initial_secret_numbers = []
        self.prices = {}
        self._load_data(filename)
        self.generate_prices(price_filename, 2000, force_reprice=force_reprice)
        self._load_prices(price_filename)

    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            for row in f:
                self.initial_secret_numbers.append(int(row.strip()))

    def _load_prices(self, filename: str):
        with open(filename, 'r') as f:
            f.readline()
            for row in f:
                values = row.strip().split(':')
                if len(values) == 3:
                    values.append('')
                    (buyer, iteration, price) = values
                else:
                    (buyer, iteration, price, delta) = values
                if buyer not in self.prices:
                    self.prices[buyer] = []

                self.prices[buyer].append((int(iteration), int(price), int(delta) if delta != '' else None))

    def analyze_prices(self):
        price_analysis = []

        for buyer in range(0, len(self.prices)):
            combinations = {}
            sequence = []
            for p in self.prices[str(buyer)][1:]:
                (iteration, price, delta) = p
                sequence.append(delta)
                if len(sequence) < 4:
                    continue
                else:
                    combination = tuple(sequence)
                    if combination not in combinations:
                        combinations[combination] = price
                    sequence = sequence[1:]
            price_analysis.append(combinations)


        already_checked = {}
        max_bananas = None
        max_combo = None
        for buyer in range(0, len(self.prices)):
            for c in list(price_analysis[int(buyer)].keys()):
                if c in already_checked:
                    continue

                bananas = 0
                for b in range(0, len(self.prices)):
                    if c in price_analysis[int(b)]:
                        bananas += price_analysis[int(b)][c]
                if max_bananas is None or bananas > max_bananas:
                    max_bananas = bananas
                    max_combo = c

                already_checked[c] = True

        return max_bananas

    def calculate(self, n: int):
        m1 = 16777216
        n1 = ((n * 64) ^ n) % m1
        n2 = ((n1 // 32) ^ n1) % m1
        n3 = ((n2 * 2048) ^ n2) % m1
        return n3

    def generate_prices(self, filename, iterations: int=2000, force_reprice: bool=False):
        if os.path.exists(filename) and not force_reprice:
            pass
        else:
            with open(filename, 'w') as f:
                f.write('Buyer:Iteration:Price:Delta\n')
                secrets = copy.copy(self.initial_secret_numbers)
                for i, secret_number in enumerate(secrets):
                    f.write(f'{i}:0:{str(secret_number)[-1]}:\n')
                    last_price = int(str(secret_number)[-1])
                    for iteration in range(0, iterations):
                        secret_number = self.calculate(secret_number)
                        new_price = int(str(secret_number)[-1])
                        f.write(f'{i}:{iteration+1}:{new_price}:{new_price-last_price}\n')
                        last_price = new_price

    def get_answer_1(self) -> int:
        secret_numbers = copy.copy(self.initial_secret_numbers)
        for i in range(0, 2000):
            secret_numbers = [self.calculate(n) for n in secret_numbers]

        return sum(secret_numbers)

    def get_answer_2(self) -> int:
        price_analysis = self.analyze_prices()
        return price_analysis

test_solution = MonkeyMarket('test.txt', 'test_prices.txt', force_reprice=True)
assert test_solution.get_answer_1() == 37327623

test2_solution = MonkeyMarket('test2.txt', 'test2_prices.txt', force_reprice=True)
assert test2_solution.get_answer_2() == 23

solution_1 = MonkeyMarket('data.txt', 'data_prices.txt')
answer_1 = solution_1.get_answer_1()
print(f'Task 1 Answer: {answer_1}')
answer_2 = solution_1.get_answer_2()
print(f'Task 2 Answer: {answer_2}')
