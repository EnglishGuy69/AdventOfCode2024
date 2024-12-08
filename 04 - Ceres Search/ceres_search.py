'''


M S    M M    S M     S S
 A      A      A       A
M S    S S    S M     M M
'''


import re

class CeresSearch:
    def __init__(self, filename: str):
        self._rows = []

        self.load_data(filename)

    def load_data(self, filename: str):
        with open(filename, 'r') as f:
            self._rows = [row.strip() for row in f]

    @property
    def width(self) -> int:
        return len(self._rows[0])

    @property
    def height(self) -> int:
        return len(self._rows)

    def __str__(self):
        return self._rows[0][:10] + '...'

    def get_row(self, n: int) -> str:
        return self._rows[n]

    def get_column(self, n: int) -> str:
        return ''.join([row[n] for row in self._rows])

    def _get_cells(self, x: int, y: int, dx: int, dy: int) -> str:
        xx = x
        yy = y
        assert dx != 0 or dy != 0

        s = ''
        while 0 <= xx < self.width and 0 <= yy < self.height:
            s += self._rows[yy][xx]
            xx += dx
            yy += dy

        return s

    def get_diag_down(self, x: int, y: int) -> str:
        return self._get_cells(x, y, 1, 1)

    def get_diag_up(self, x: int, y: int) -> str:
        return self._get_cells(x, y, 1, -1)

    def get_columns(self) -> [str]:
        return [self.get_column(n) for n in range(0, self.width)]

    def get_rows(self) -> [str]:
        return self._rows

    def get_diags_down(self) -> [str]:
        d1 = [self.get_diag_down(0, y) for y in range(1,self.height)]
        d2 = [self.get_diag_down(x, 0) for x in range(0, self.width)]
        d1.extend(d2)
        return d1

    def get_diags_up(self) -> [str]:
        d1 = [self.get_diag_up(0, y) for y in range(0,self.height-1)]
        d2 = [self.get_diag_up(x, self.height-1) for x in range(0, self.width)]
        d1.extend(d2)
        return d1

    @staticmethod
    def _find_match(word: str, array: [str]):
        matches = []
        for w in array:
            matches.extend(re.findall(word, w))
            matches.extend(re.findall(word, w[::-1]))

        return matches


    def find_word(self, word: str) -> int:
        matches_rows = CeresSearch._find_match(word, self.get_rows())
        matches_cols = CeresSearch._find_match(word, self.get_columns())
        matches_diag_up = CeresSearch._find_match(word, self.get_diags_up())
        matches_diag_down = CeresSearch._find_match(word, self.get_diags_down())

        return len(matches_rows) + len(matches_cols) + len(matches_diag_up) + len(matches_diag_down)

    # def generate_templates(self, word: str):
    #     templates = []
    #
    #     for i in range(0, 4):
    #         for r


test_solution = CeresSearch('test.txt')
assert test_solution.find_word('XMAS') == 18

solution = CeresSearch('data.txt')
answer_1 = solution.find_word('XMAS')
print(f'Part 1 Answer: {answer_1}')

# ToDo: Part 2