'''
Author: Guy Pickering
Date:

Puzzle:

Part 1

Part 2

8X010123
78121874
87430965
X654X874
45678X03
3201X012
01329801
10456732


'''

from map import MapBase, Map

class HoofIt(Map):
    dx_dy = [(0,1), (0,-1), (1,0), (-1,0)]
    def __init__(self, filename: str):
        super().__init__(filename)

    def find_trail_starts(self):
        return [(x,y) for y in range(self.height) for x in range(self.width) if self.map[y][x] == '0']

    def count_trail_heads_from_start_position(self,
                                              trail_start: (int,int),
                                              count_all_paths: bool = False) -> int:
        found_peaks = []
        flood_positions = [trail_start]

        while flood_positions:
            (x0, y0) = flood_positions.pop(0)
            h0 = self.map[y0][x0]
            for (dx, dy) in HoofIt.dx_dy:
                (x1, y1) = (x0 + dx, y0 + dy)
                if not (0 <= x1 < self.width and 0 <= y1 < self.height):
                    continue

                h1 = self.map[y1][x1]
                if h0 == '8' and h1 == '9':
                    if count_all_paths or (x1, y1) not in found_peaks:
                        found_peaks.append((x1, y1))
                else:
                    if int(h1) - int(h0) == 1:
                        flood_positions.append((x1, y1))
        return len(found_peaks)

    def get_answer_1(self) -> int:
        trail_starts = self.find_trail_starts()

        total_count = 0
        for trail_start in trail_starts:
            total_count += self.count_trail_heads_from_start_position(trail_start)

        return total_count

    def get_answer_2(self) -> int:
        trail_starts = self.find_trail_starts()

        total_count = 0
        for trail_start in trail_starts:
            total_count += self.count_trail_heads_from_start_position(trail_start, count_all_paths=True)

        return total_count


test_solution = HoofIt('test.txt')
assert test_solution.get_answer_1() == 36
assert test_solution.get_answer_2() == 81

solution_1 = HoofIt('data.txt')
answer_1 = solution_1.get_answer_1()
print(f'Task 1 Answer: {answer_1}')
answer_2 = solution_1.get_answer_2()
print(f'Task 2 Answer: {answer_2}')
