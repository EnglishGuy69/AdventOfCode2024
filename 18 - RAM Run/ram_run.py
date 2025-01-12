'''
Author: Guy Pickering
Date:

Puzzle:

Part 1
Now that we have the Map and MapSolver classes (see "001- Shared" folder), this is a pretty straightforward problem
to solve. The "flooding" approach to finding the shortest way through a maze works well to identify the shortest path.
Initially I just had the populate_bytes_on_map() function drop the bytes (walls) onto the map. I updated in part 2
to allow us to move forward and backward on the timeline of bytes dropping to more efficiently set up the map at
a specific point.

Part 2
To solve part 2, we want to find the point at which we go from having a path to not having a path. Brute force of
moving through the timeline from 1, 2, 3... is not efficient. This is like a search problem, so we set the bounds of
the possible answers and then bisect that range and test. Each time we find a path, we move the minimum bound up;
each time we do not find a path we move the maximum bound down. Eventually we get to where the minimum and maximum
bounds are adjacent that that tells us that the minimum bound has a path and the maximum bound does not. For the
maximum bound, we want the last byte dropped at that point in the timeline (which is one less than the bound).

'''

from map import MapBase
from map_solver import MapSolver

class RamRun:
    def __init__(self, filename: str, map_width: int, map_height: int):
        self.map = MapBase()
        self.map.populate_empty_map(width=map_width, height=map_height)
        self.map.start = (0,0)
        self.map.end = (map_width-1, map_height-1)
        self.current_nanoseconds = 0

        self.byte_locations = []

        self._load_data(filename)

    def populate_bytes_on_map(self, new_nanoseconds: int):
        if new_nanoseconds > self.current_nanoseconds:
            for n in range(self.current_nanoseconds, new_nanoseconds):
                position = self.byte_locations[n]
                self.map.set_location(position,MapBase.WALL)
            self.current_nanoseconds = new_nanoseconds
        elif new_nanoseconds < self.current_nanoseconds:
            for n in range(new_nanoseconds, self.current_nanoseconds):
                position = self.byte_locations[n]
                self.map.set_location(position,MapBase.PATH)
            self.current_nanoseconds = new_nanoseconds


    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            for row in f:
                (x,y) = [int(n) for n in row.strip().split(',')]
                self.byte_locations.append((x,y))

    def get_answer_1(self, nanoseconds: int) -> int:
        self.populate_bytes_on_map(new_nanoseconds=nanoseconds)
        map_solver = MapSolver(map=self.map)

        shortest_path = map_solver.find_shortest_route_distance()
        return shortest_path

    def get_answer_2(self) -> int:
        min_nanoseconds = min([self.map.width, self.map.height])
        max_nanoseconds = len(self.byte_locations)
        while min_nanoseconds != max_nanoseconds-1:
            current_nanoseconds = int((max_nanoseconds - min_nanoseconds) // 2) + min_nanoseconds
            self.populate_bytes_on_map(current_nanoseconds)
            MapSolver._debug = True
            map_solver = MapSolver(map=self.map)
            route_distance = map_solver.find_shortest_route_distance()
            is_blocked = route_distance < 0
            if is_blocked:
                max_nanoseconds = current_nanoseconds
            else:
                min_nanoseconds = current_nanoseconds

        # self.populate_bytes_on_map(min_nanoseconds)
        # map_solver_1 = MapSolver(self.map)
        # map_solver_1.render()
        # print('')
        # self.populate_bytes_on_map(max_nanoseconds)
        # map_solver_2 = MapSolver(self.map)
        # map_solver_2.render()

        return str(self.byte_locations[max_nanoseconds-1])


test_solution = RamRun('test.txt', map_width=7, map_height=7)
assert test_solution.get_answer_1(nanoseconds=12) == 22
#assert test_solution.get_answer_2() == 0 # update

solution_1 = RamRun('data.txt', 71,71)
answer_1 = solution_1.get_answer_1(nanoseconds=1024)
print(f'Task 1 Answer: {answer_1}')
answer_2 = solution_1.get_answer_2()
print(f'Task 2 Answer: {answer_2}')
