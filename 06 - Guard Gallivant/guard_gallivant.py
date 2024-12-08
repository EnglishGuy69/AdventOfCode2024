'''
Author: Guy Pickering
Date: 12/07/2024

Puzzle
An area contains obstruction '#' and the starting position of a guard '^'. The guard walks until they hit an
obstruction and then turns right. The path continues until the guard walks off the area.

Part 1
Determine the locations on the map that are visited by the guard.

Part 2
By placing one additional obstruction, find ways in which the guard will end up in a loop (never leaving the area),
but you cannot place the obstruction on the guards starting position. Find the number of positions on the map that the
one additional obstruction will result in a loop.

Hint 1: You only need to explore the positions where the original guard goes - unvisited locations would never impact
the guard's route.

Hint 2: I was having performance issues with Part 2. I found that has_step() function was being called 7269 times in
Part 1 taking 0.381 seconds. I used the profiler (python3 -m cProfile -s tottime guard_gallivant.py).
So I looked to optimize this call with a dictionary cache. This reduced the time from 0.381 secs to 0.005 secs,
significantly speeding up the process of creating the guard's route.

'''

from datetime import datetime
from typing import Optional

class LoopFound(BaseException):
    pass

class Cell:
    default_symbol = '.'
    obstruction_symbol = '#'
    temporary_obstruction_symbol = 'O'

    def __init__(self,
                 x: int,
                 y: int,
                 is_obstruction: bool,
                 is_temporary_obstruction=False):
        self.x = x
        self.y = y
        self.is_obstruction = is_obstruction
        self.is_temporary_obstruction = is_temporary_obstruction

    def get_symbol(self):
        '''
        For printing, determine the character to show. This may be overlayed by the guard's route.

        :return: '#' for a permanent obstruction
                 'O' for a temporary obstruction
                 '.' for other positions
        '''
        if self.is_obstruction:
            if self.is_temporary_obstruction:
                return Cell.temporary_obstruction_symbol
            else:
                return Cell.obstruction_symbol
        else:
            return Cell.default_symbol

    def set_temporary_obstruction(self):
        '''
        Used during Part 2 to place a temporary obstruction in the map.

        :return: None
        '''
        self.is_obstruction = True
        self.is_temporary_obstruction = True

    def unset_temporary_obstruction(self):
        '''
        Used during Part 2 to remove a temporary obstruction in the map.

        :return: None
        '''
        self.is_obstruction = False
        self.is_temporary_obstruction = False

    def __str__(self):
        return self.get_symbol()


class GuardPathStep:
    directions = ['N', 'S', 'E', 'W']
    turn_right = ['E', 'W', 'S', 'N']  # defines the direction each direction will transform when turning right.
    deltas = [(0,-1), (0,1), (1,0), (-1,0)]  # dx and dy based on the direction
    path_symbols = ['|', '|', '-', '-']  # for rendering the map

    def __init__(self, x: int, y: int, direction: str):
        self.x = x
        self.y = y
        self.direction = direction

    def get_symbol(self):
        '''
        Returns the '|' or '-' for a path. May be overriden by '+' if multiple steps are on the same x,y location.

        :return: '|' for North/South
                 '-' for East/West
        '''
        return GuardPathStep.path_symbols[GuardPathStep.directions.index(self.direction)]

    def __str__(self):
        return f"{self.x}|{self.y}|{self.direction}"


class GuardPath:
    multi_path_symbol = '+'
    def __init__(self):
        self.path = []
        self.steps_cache = {}  # Cache of 'x|y|d' dictionary items to aid faster lookup

    def add_step(self, step: GuardPathStep):
        self.path.append(step)
        self.steps_cache[str(step)] = True  # Cache a string version of the step for faster lookup

    def get_symbol(self, x: int, y: int) -> str|None:
        '''
        Returns a representation of the path, showing the vertical or horizontal path, or places where the path
        crosses the same location multiple times (shown by '+').

        :param x: X location
        :param y: Y location
        :return: '|', '-' or '+' (if multiple steps overlap the same locations)
        '''
        steps: [GuardPathStep] = [step for step in self.path if (step.x, step.y) == (x,y)]
        if len(steps) > 1:
            return GuardPath.multi_path_symbol
        elif len(steps) == 1:
            return steps[0].get_symbol()
        else:
            return None

    def has_step(self, x: int, y: int, d: str) -> bool:
        '''
        Uses the cached string representation of the path to determine if the specified location (x,y) and direction (d)
        already exist. If they already exist, this implies a loop condition (which can be identified and raised as an
        exception by the caller.

        :param x: X location
        :param y: Y location
        :param d: Direction (N,S,E,W)
        :return: True if the position and direction already exists in the path, otherwise False
        '''
        # Unoptimized version...
        #steps = [s for s in self.path if s.x == x and s.y == y and s.direction == d]
        #return len(steps) > 0

        # Optimized Version...
        return f'{x}|{y}|{d}' in self.steps_cache

    def find_steps_at_position(self, x: int, y):
        steps = [s for s in self.path if s.x == x and s.y == y]
        return steps

    def find_distinct_positions(self):
        positions = [(p.x, p.y) for p in self.path]
        return list(set(positions))

class GuardGallivant:
    guard_symbols = ['^', 'v', '>', '<']  # The examples only include '^', but assume all directions are possible.

    def __init__(self, filename: str, debug=False):
        self.map: [[Cell]] = []
        self.guard_start_position: (int,int) = None
        self.guard_start_direction: str|None = None
        self._load_data(filename)
        self._debug = debug

    @property
    def width(self):
        return len(self.map[0])

    @property
    def height(self):
        return len(self.map)

    def _load_data(self, filename: str):
        '''
        Loads the map from the data file. The data file contains '.' for empty space, '#' for an obstruction
        and '^' for the guard's starting location, e.g.

        .....
        .#...
        ...^.
        .....

        :param filename: Location of the data file
        :return: None
        '''
        with open(filename, 'r') as f:
            for y,row in enumerate(f):
                map_row = [Cell(x,y,c == Cell.obstruction_symbol) for x,c in enumerate(row.strip())]

                # Look for the guard (typically '^')
                guards = [(x, c) for x, c in enumerate(row.strip()) if c in GuardGallivant.guard_symbols]
                assert len(guards) <= 1  # Assume a maximum of one guard per row
                if len(guards) > 0:
                    assert self.guard_start_position is None  # Assume a maximum of one guard per map
                    self.guard_start_position = (guards[0][0],y)
                    self.guard_start_direction = GuardPathStep.directions[GuardGallivant.guard_symbols.index(guards[0][1])]

                self.map.append(map_row)

    def get_symbol(self, x: int, y: int, guard_path: GuardPath|None=None) -> str:
        '''

        :param x: X Location
        :param y: Y Location
        :param guard_path: Optional guard path. If provided, the guard path overlays the map.
        :return: '.', '#', '|', '-', '+'
        '''

        guard_starting_symbol = GuardGallivant.guard_symbols[GuardPathStep.directions.index(self.guard_start_direction)] if (x,y) == self.guard_start_position else None
        path_symbol = guard_path.get_symbol(x, y) if guard_path else None
        return guard_starting_symbol or path_symbol or self.map[y][x].get_symbol()

    def is_on_map(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_blocked(self, x: int, y: int, d: str) -> bool:
        '''
        Determines if the guard's next step is blocked or not.
        :param x: X location
        :param y: Y location
        :param d: Direction (N, S, E, W)
        :return: True if the next location in the specified direction is (a) still on the map, and (b) contains an
                 obstruction.
        '''
        (dx, dy) = GuardPathStep.deltas[GuardPathStep.directions.index(d)]
        (x1, y1) = (x+dx, y+dy)
        return self.is_on_map(x1, y1) and self.map[y1][x1].is_obstruction

    def _generate_guard_path(self) -> GuardPath:
        '''
        Follows the path of the guard, turning right if an obstruction is found until the guard leaves the map or
        ends up in the starting location and direction (indicating a loop), in which case, a LoopFound exception is
        generated. We could take a parameter to not raise the exception if the route (including loops) are required.

        :return: A GuardPath object containing the path of the guard. If a loop is detected, then a LoopFound exception
                 is raised.
        '''

        guard_path = GuardPath()
        (x,y) = self.guard_start_position
        d = self.guard_start_direction

        while self.is_on_map(x, y):
            if guard_path.has_step(x, y, d):
                raise LoopFound()
            else:
                guard_path.add_step(GuardPathStep(x=x, y=y, direction=d))

            if self.is_blocked(x, y, d):
                d = GuardPathStep.turn_right[GuardPathStep.directions.index(d)]
            else:
                (dx, dy) = GuardPathStep.deltas[GuardPathStep.directions.index(d)]
                (x, y) = (x+dx, y+dy)

        return guard_path

    def get_answer_1(self) -> int:
        t0 = datetime.now()
        guard_path = self._generate_guard_path()
        t1 = datetime.now()

        if self._debug:
            print(f'Duration: {(t1 - t0).microseconds / 1000000} seconds')
            s = self.as_string(guard_path=guard_path)
            print(s)

        return len(guard_path.find_distinct_positions())

    def get_answer_2(self) -> int:
        guard_path = self._generate_guard_path()
        distinct_positions = guard_path.find_distinct_positions()

        # Remove the start position from the possible locations for the obstruction, as this is not allowed
        distinct_positions.pop(distinct_positions.index(self.guard_start_position))

        loop_count = 0
        for i, (x,y) in enumerate(distinct_positions):
            print(f'Checking {i} of {len(distinct_positions)} {int(100*i/len(distinct_positions))}% ...', end='\r')
            self.map[y][x].set_temporary_obstruction()

            try:
                _ = self._generate_guard_path()
            except LoopFound:
                loop_count += 1

            self.map[y][x].unset_temporary_obstruction()

        return loop_count


    def as_string(self, guard_path: GuardPath|None=None) -> str:
        return '\n'.join([''.join([self.get_symbol(x,y,guard_path) for x in range(0, self.width)]) for y in range(0, self.height)])

    def __str__(self):
        return self.as_string()


test_solution = GuardGallivant('test.txt')
assert test_solution.get_answer_1() == 41
assert test_solution.get_answer_2() == 6

solution_1 = GuardGallivant('data.txt')
answer_1 = solution_1.get_answer_1()
print(f'Task 1 Answer: {answer_1}')

solution_2 = GuardGallivant('data.txt')
answer_2 = solution_2.get_answer_2()
print(f'Task 2 Answer: {answer_2}')