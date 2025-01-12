'''
Author: Guy Pickering
Date:

Puzzle:

Part 1

Part 2

'''

class Template:
    def __init__(self, filename: str):
        self.locks = []
        self.keys = []
        self.max_lock_key = None

        self._load_data(filename)

    def transpose(self, array: [str], is_key: bool):
        rows = len(array)
        columns = len(array[0])

        if is_key:
            new_array = [''.join([array[rows-y-1][x] for y in range(0,rows)]) for x in range(0, columns)]
        else:
            new_array = [''.join([array[y][x] for y in range(0,rows)]) for x in range(0, columns)]

        return new_array

    def flush_lock_or_key(self, lock_or_key: [str]):
        if self.max_lock_key is None:
            self.max_lock_key = len(lock_or_key)-2

        is_key = False
        if lock_or_key[0].find('.') >= 0:
            is_key = True

        array = self.transpose(lock_or_key, is_key)
        combination = [s.find('.')-1 for s in array]
        if is_key:
            self.keys.append(combination)
        else:
            self.locks.append(combination)


    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            lock_or_key = []
            for row in f:
                if row.strip() == '':
                    self.flush_lock_or_key(lock_or_key)
                    lock_or_key = []
                else:
                    lock_or_key.append(row.strip())

            self.flush_lock_or_key(lock_or_key)

    def does_lock_fit(self, lock: [int], key: [int]) -> bool:
        overlap = sum([1 if lock[i]+key[i] > self.max_lock_key else 0 for i in range(0, len(lock))])
        return not overlap

    def find_lock_key_combinations(self):
        combo_counts = 0
        for lock in self.locks:
            for key in self.keys:
                if self.does_lock_fit(lock, key):
                    combo_counts += 1

        return combo_counts

    def get_answer_1(self) -> int:
        return self.find_lock_key_combinations()

    def get_answer_2(self) -> int:
        return 0


test_solution = Template('test.txt')
assert test_solution.get_answer_1() == 3
#assert test_solution.get_answer_2() == 0 # update

solution_1 = Template('data.txt')
answer_1 = solution_1.get_answer_1()
print(f'Task 1 Answer: {answer_1}')
