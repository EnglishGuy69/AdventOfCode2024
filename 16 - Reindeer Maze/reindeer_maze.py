'''
Author: Guy Pickering
Date:

Puzzle:

Part 1

Part 2

Design Notes
============
Each cell has four position where the path can be:

        ^
    <       >
        v

We will initialize each cell with the Reindeer's path _out_ of the cell. In each case, we determine the path and score
and only consider moving that direction if the score would be less than the existing path. Once all paths have been
evaluated, we go to the end cell and look at the cells around to find the lowest path coming into the cell.

Step 1:
Create a path for exiting each location (<, >, ^, v). If the path out is empty or the path out has a higher score,
store the path and save the reindeer.

Step 3:
If no paths were saved, Return.
Otherwise, for each path:
  if target is 'E', store end_reindeer (if lowest score) and return
  if target is not 'E', recurse.


'''

import copy
import os
import sys

DIRECTIONS = ['^','>','v','<']
DX_DY = [(0,-1),(1,0),(0,1),(-1,0)]

class Cell:
    WALL = '#'

    def __init__(self, position: (int, int), cell_type: str):
        self.cell_type = cell_type
        self.position = position
        #                      ^      >     v    <
        self.scores: [int] = [None, None, None, None]

    def get_score(self, direction: str):
        return self.scores[DIRECTIONS.index(direction)]

    def update(self, direction: str, base_score: int) -> [(int,(int,int),str)]:  # [(score,(x,y),direction)]
        new_scores = []
        for d in range(0, 4):  # ^ > v <
            direction_index = DIRECTIONS.index(direction)
            direction_diff = abs(direction_index-d)
            if direction_diff == 3: direction_diff = 1
            new_score = base_score + direction_diff * 1000 + 1
            new_scores.append(new_score)

        new_positions_directions_scores = []
        for i in range(0, 4):
            if self.scores[i] is None or new_scores[i] < self.scores[i]:
                self.scores[i] = new_scores[i]
                (dx, dy) = DX_DY[i]
                (x0, y0) = self.position
                new_positions_directions_scores.append((new_scores[i], (x0+dx, y0+dy), DIRECTIONS[i]))

        return new_positions_directions_scores

    @property
    def path_count(self):
        return sum([1 if p else 0 for p in self.paths])

    def __str__(self):
        return f'{self.cell_type}'

    def render(self):
        width = len(str(self.scores[3] or '-')) + len(str(self.scores[1] or '-')) + 2
        s = ''
        s += f'{str(self.scores[0] or "-"): ^{width}}\n'
        s += f'{self.scores[3] or "-"}  {self.scores[1] or "-"}\n'
        s += f'{str(self.scores[2] or "-"): ^{width}}'
        print(s)


class ReindeerMaze:
    DIRECTIONS = ['^','>','v','<']
    DX_DY = [(0,-1),(1,0),(0,1),(-1,0)]

    def __init__(self,
                 filename: str,
                 debug=False,
                 render_path_count=False,
                 render_frequency=1):
        self.debug = debug
        self.render_path_count = render_path_count
        self.render_frequency = render_frequency

        self.map = []

        self.start: (int, int) = None
        self.end: (int, int) = None
        self._load_data(filename)

        self.visited = []
        self.render_count = 0

    @property
    def width(self):
        return len(self.map[0])

    @property
    def height(self):
        return len(self.map)

    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            for y,s in enumerate(f):
                row = []
                for x,c in enumerate(s.strip()):
                    row.append(Cell((x,y), c))
                self.map.append(row)

                start = [x for x,c in enumerate(s.strip()) if c == 'S']
                if start:
                    self.start = (start[0], y)

                end = [x for x,c in enumerate(s.strip()) if c == 'E']
                if end:
                    self.end = (end[0], y)

    # def find_min_source_cells(self, position: (int, int)):
    #     (x0, y0) = position
    #
    #     positions_scores = []  # (position, score)
    #     for i in range(0, 4):
    #         (dx, dy) = DX_DY[i]
    #         prior_position = (x0 + dx, y0 + dy)
    #         (x,y) = prior_position
    #         if not self.is_valid_cell(prior_position):
    #             continue
    #
    #         cell = self.map[y][x]
    #         direction = DIRECTIONS[i]
    #         contra_direction_pos = (i+2) % 4
    #         contra_direction = DIRECTIONS[contra_direction_pos]
    #         score = cell.scores[contra_direction]
    #         positions_score

    # def render(self, position: (int, int)):
    #     (x,y) = position
    #
    #     for dx_dy in DX_DY:
    #         (dx, dy) = dx_dy
    #         (x1, y1) =


    def get_next_positions(self, position: (int, int)):
        (x0, y0) = position

        next_positions = []
        for (dx, dy) in ReindeerMaze.DX_DY:
            (x, y) = (x0+dx, y0+dy)
            if 0 <= x < self.width and 0 <= y < self.height and self.map[y][x] != Cell.WALL:
                next_positions.append((x,y))

        return next_positions

    def is_valid_cell(self, position: (int, int)):
        (x,y) = position
        is_valid = 0 <= x < self.width and 0 <= y < self.height and self.map[y][x].cell_type != Cell.WALL
        return is_valid

    def follow_path_v2(self):
        positions = [(0, self.start,'>')]
        while positions:
            (score, position, direction) = positions.pop(0)
            (x,y) = position
            cell: Cell = self.map[y][x]
            new_positions_directions_scores = cell.update(direction=direction, base_score=score)
            new_positions_directions_scores = [(s,(x,y),d) for (s,(x,y),d) in new_positions_directions_scores if self.is_valid_cell((x,y))]
            if new_positions_directions_scores:
                positions.extend(new_positions_directions_scores)

    @property
    def minimum_path_score(self) -> int:
        (x,y) = self.end
        cell: Cell = self.map[y][x]
        return min(cell.scores) - 1

    def get_answer_1(self) -> int:
        self.follow_path_v2()
        return self.minimum_path_score

    def get_answer_2(self) -> int:
        return 0


test_solution = ReindeerMaze('test.txt')
assert test_solution.get_answer_1() == 7036

test2_solution = ReindeerMaze('test2.txt')
#test2_solution = ReindeerMaze('test2.txt', debug=True, render_path_count=True)
assert test2_solution.get_answer_1() == 11048

solution_1 = ReindeerMaze('data.txt') # , debug=True, render_frequency=1000)
answer_1 = solution_1.get_answer_1()
print(f'Task 1 Answer: {answer_1}')
