'''
Author: Guy Pickering
Date: 12-14-2024

Puzzle:

Part 1
A set of robots are guarding the rest-room. Each robot has an initial starting position and a velocity and each
iteration robots will move in the direction/speed they are defined. The path of a robot wraps, so robots leaving the
bottom come back in the top, robots leaving the right come back in the left, etc.

After N iterations, we calculate the number of robots in each of the four quadrants (ignoring robots located on the
center-line in either direction). We multiply these four numbers to get the answer.

Part 2
The second part reveals that after an undisclosed number of iteration, an 'easter egg' will reveal a Christmas Tree
and the goal is to identify the number of iterations to reveal it.

Design Notes
Converting each robot to a location (and velocity) and using simple multiplication and modulus operations calculate the
final positions of the robots in part one.

In part two, we have to somehow identify that a Christmas Tree has been
formed. The idea I used was to measure the density of robots in the center of the map (101x103). So I assumed the
tree would be in the middle (this turned out not to be true) and looked for the maximum density of robots in an
area 20x20. I ran for 100,000 and picked the iteration that showed the highest % of robots. This turned out to be the
correct answer. Had this not worked I would have split the map up into 9x9 or 16x16 and measured the

'''

import math

class Robot:
    def __init__(self,
                 position: (int, int),
                 velocity: (int, int)):
        self.position = position
        self.velocity = velocity

    def get_position_when(self, time_secs: int, width: int, height: int):
        (px, py) = self.position
        (dx, dy) = self.velocity

        return ((px+time_secs*dx) % width, (py+time_secs*dy) % height)

    def __str__(self):
        return f'p:{self.position} v:{self.velocity}'

class RestroomRedoubt:
    def __init__(self, filename: str, width: int, height: int):
        self.width=width
        self.height=height
        self.robots = []

        self._load_data(filename)

    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            for row in f:
                p_v = [x for x in row.strip().split(' ')]
                (p, v) = [tuple([int(x) for x in d[2:].split(',')]) for d in p_v]
                self.robots.append(Robot(p, v))

    def get_answer_1(self, at_time_secs) -> int:
        quadrant_count = [0, 0, 0, 0]
        for robot in self.robots:
            (x, y) = robot.get_position_when(at_time_secs, self.width, self.height)
            if x == self.width // 2 or y == self.height // 2:
                continue
            quadrant = int(int((x / int((self.width // 2 + 1)))) + int(2*int((y / (self.height // 2 + 1)))))
            quadrant_count[quadrant] += 1

        return math.prod(quadrant_count)

    def calc_density(self, time_at_secs: int, center: (int, int), target_width: int, target_height: int):
        center = (int(self.width / 2), int(self.height / 2))
        target_width_half = int(target_width / 2)
        target_height_half = int(target_height / 2)
        (cx, cy) = center

        cnt = 0
        for robot in self.robots:
            (rx, ry) = robot.get_position_when(time_secs=time_at_secs, width=self.width, height=self.height)
            if cx-target_width_half <= rx < cx+target_width_half and cy-target_height_half <= ry < cy+target_height_half:
                cnt += 1

        return cnt / (target_width*target_height)


    def get_answer_2(self, search_until_secs: int) -> int:
        center = (int(self.width / 2), int(self.height / 2))
        max_density = None
        max_density_time_secs = None
        for i in range(0, search_until_secs):
            density = self.calc_density(i, center=center, target_width=20, target_height=20)
            if max_density is None or density > max_density:
                max_density = density
                max_density_time_secs = i

        return max_density_time_secs



    def render(self, at_time_secs=0, separate_quadrants=False):
        for y in range(0, self.height):
            if separate_quadrants and y == self.height // 2:
                print('')
                continue
            for x in range(0, self.width):
                if separate_quadrants and x == self.width // 2:
                    print(' ', end='')
                    continue
                c = sum([1 if r.get_position_when(at_time_secs, self.width, self.height) == (x,y) else 0 for r in self.robots])
                print(f'{c if c > 0 else "."}', end='')
            print('')

test_solution = RestroomRedoubt('test.txt', width=11, height=7)
#test_solution.render(100, separate_quadrants=True)
assert test_solution.get_answer_1(at_time_secs=100) == 12
#assert test_solution.get_answer_2() == 0 # update

solution_1 = RestroomRedoubt('data.txt', width=101, height=103)
answer_1 = solution_1.get_answer_1(at_time_secs=100)
print(f'Task 1 Answer: {answer_1}')

answer_2 = solution_1.get_answer_2(search_until_secs=100000)
print(f'Task 2 Answer: {answer_1}')
solution_1.render(answer_2)
