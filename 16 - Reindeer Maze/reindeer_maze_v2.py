'''
Author: Guy Pickering
Date:

Puzzle:

Part 1
So after trying a number of different approaches, I circled back on this one using the new Map and MapSolver classes.
The original MapSolver only worked on a simple route from start to end (single steps). This problem is harder because
turns cost 1,000 vs. 1 step. To handle this we do a few things:

1: Track the exit paths from each cell (SolverCell), so paths that come in and go out from different directions can
have different scores.

                        1001
               2001  <   ^   > 2001
                         v
                        3001

We also track the lowest path to get to a call.

We perform a 'flood' approach to populating the distance map rather than a recursive path test. This is more efficient
and solves the problem within a few minutes. There is probably a faster approach, but I couldn't find it.

Part 2
OK, so Part 2 was a doozy. Once we have populated the distance map for the problem, we then have to detect all the
cells that are part of shortest paths. I attempted a bunch of different ways, but kept coming back to trying to detect
whether an upstream cell could have been part of the path based on the exit paths stored in each cell (starting at the
end cell). I eventually settled on a reverse navigation (again flood approach). In each case we determine if the
incremental cost to get from the upstream cell to cell we know is part of the path matches the exit path score from the
upstream path to the exit path from the known cell, we add that to the list. e.g.

                    6030              [8031]
                8030    [7030]    10031     -
                    8030               9031

'''

from map import MapWithStartAndEnd, Map, MapBase
from direction_mapper import DirectionMapper
from map_solver import MapSolver
import copy

class Path:
    def __init__(self,
                 path: str='',
                 initial_direction: str = 'E'):
        self.path = path
        self._initial_direction = initial_direction
        self.score = 0

    def add_to_path(self, c: str) -> str:
        self.path += c
        self.score = self._calc_cost()
        return self.path

    def _calc_cost(self) -> int:
        cost = 0
        last_c = self._initial_direction
        for i,current_c in enumerate(self.path):
            cost += 1
            if last_c is not None and current_c != last_c:
                cost += 1000
                if set([last_c,current_c]) in [set(['N','S']),set(['E','W'])]:
                    cost += 1000
            last_c = current_c

        return cost

    def __str__(self):
        return f'{len(self.path)} steps, score: {self.score}'

class SolverCell:
    def __init__(self, position: (int,int), map: Map, map_solver: "ReindeerMapSolver"):
        self.position = position
        self._map = map
        self._map_solver = map_solver

        self.pending_paths = []
                        #   N    E    S    W
        self.exit_paths = {}
        self.cheapest_path: Path|None = None

#        self.allowed_exit_paths = [False,False,False]
        allowed_dx_dy = map.open_dx_dy_around_position(position=position)
        self.allowed_directions = [DirectionMapper.find_direction_compass(dx_dy) for dx_dy in allowed_dx_dy]

    def __str__(self):
        return f'{self.position}{" *" if self.exit_paths else ""}'

    def add_pending_path(self, path: Path):
        self.pending_paths.append(path)
        if self.cheapest_path is None or path.score < self.cheapest_path.score:
            self.cheapest_path = path

    def process_pending_path(self, path: Path):
        allowed_direction: str
        for allowed_direction in self.allowed_directions:
            new_path = copy.deepcopy(path)
            new_path.add_to_path(allowed_direction)
            if allowed_direction not in self.exit_paths or \
                    (allowed_direction in self.exit_paths and
                     self.exit_paths[allowed_direction].score > new_path.score):
                self.exit_paths[allowed_direction] = new_path
                (x,y) = self.position
                (dx,dy) = DirectionMapper.find_dx_dy(allowed_direction)
                (x1,y1) = (x+dx, y+dy)
                cell: "SolverCell" = self._map_solver.distance_map[y1][x1]
                cell.add_pending_path(new_path)
                self._map_solver.add_pending_cell((x1,y1))


class ReindeerMapSolver(MapSolver):
    def __init__(self,
                 map: MapBase,
                 allow_diagonal_movement: bool=False):
        self._pending_positions: [(int, int)] = []
        super().__init__(map=map, allow_diagonal_movement=allow_diagonal_movement)

    def _generate_distance_map(self):
        distance_map = []
        for y in range(0, self.map.height):
            row = []
            for x in range(0, self.map.width):
                row.append(SolverCell(position=(x,y),
                                      map=self.map,
                                      map_solver=self))
            distance_map.append(row)

        return distance_map

    def _populate_distance_map(self, distance_map: [[]]):
        (x0,y0) = self.map.start
        start_cell: SolverCell = distance_map[y0][x0]
        start_cell.add_pending_path(Path(''))
        self._pending_positions.append(self.map.start)

        while self._pending_positions:
            (x,y) = self._pending_positions.pop(0)
            cell:SolverCell = self._distance_map[y][x]
            while cell.pending_paths:
                path = cell.pending_paths.pop(0)
                cell.process_pending_path(path)
            pass
#        self.render()

    def _is_populated(self, o: SolverCell):
        return len(o.exit_paths) > 0

    def add_pending_cell(self, position: (int,int)):
        self._pending_positions.append(position)

    def calc_score_delta_from_directions(self, direction_1: str, direction_2: str):
        score = 1
        if direction_1 != direction_2:
            score += 1000

            opposite_direction = DirectionMapper.opposite(direction_1)
            if opposite_direction == direction_2:
                score += 1000

        return score

    def trace_back_paths(self):
        cells = []
        (x,y) = self.map.end
        end_cell:SolverCell = self.distance_map[y][x]
        cells.append(end_cell.position)

        outstanding_cells: [(SolverCell,str)] = []
        incoming_positions = self._find_next_positions(self.map.end, follow_all_paths=True)
        cell: SolverCell
        for position in incoming_positions:
            (cx,cy) = position
            cell = self.distance_map[cy][cx]
            direction = DirectionMapper.find_direction_compass_between_points(cell.position, self.map.end)
            path: Path = cell.exit_paths[direction]
            if path.score == end_cell.cheapest_path.score:
                outstanding_cells.append((cell,direction, path.score))
                cells.append(cell.position)

        while outstanding_cells:
            (cell, direction, score) = outstanding_cells.pop(0)
            exit_score = cell.exit_paths[direction].score
            if exit_score != score:
                continue

            incoming_positions = self._find_next_positions(cell.position, follow_all_paths=True)
            for position in incoming_positions:
                outgoing_direction = DirectionMapper.find_direction_compass_between_points(position, cell.position)
                score_delta = self.calc_score_delta_from_directions(outgoing_direction, direction)
                (cx, cy) = position
                possible_cell:SolverCell = self.distance_map[cy][cx]
                exit_path: Path = possible_cell.exit_paths[outgoing_direction]
                if exit_path.score + score_delta == exit_score:
                    if possible_cell.position not in cells:
                        cells.append(possible_cell.position)
                        outstanding_cells.append((possible_cell, outgoing_direction, exit_path.score))
        return cells


class ReindeerMaze:
    def __init__(self, filename: str):
        self.map = MapWithStartAndEnd(filename)

    def _score_route(self, path: [()]):
        score = len(path)-1
        last_direction = 'E'
        for i in range(1, len(path)):
            (p1, d1) = path[i-1]
            (p2, d2) = path[i]
            direction = DirectionMapper.find_direction_compass_between_points(p1,p2)
            if direction != last_direction:
                score += 1000
                last_direction = direction

        return score


    def get_answer_1(self) -> int:
        solver = ReindeerMapSolver(self.map)
        (x,y) = self.map.end
        shortest_path = solver.distance_map[y][x].cheapest_path.score
        return shortest_path

        # solver = MapSolver(map=self.map)
        # solver.purge_dead_ends()
        # all_routes = solver.find_all_routes()
        # lowest_score = None
        # lowest_route = None
        # for route in all_routes:
        #     score = self._score_route(route)
        #     if lowest_score is None or score < lowest_score:
        #         lowest_score = score
        #         lowest_route = route
        # print(f'SCORE: {lowest_score}')
        # solver.render(overlay_route=[p for (p,d) in lowest_route])
        # print('')
        # return lowest_score

    def get_answer_2(self) -> int:
        solver = ReindeerMapSolver(self.map)
        (x,y) = self.map.end
        cells = solver.trace_back_paths()
        return len(cells)


test_solution = ReindeerMaze('test.txt')
assert test_solution.get_answer_1() == 7036
assert test_solution.get_answer_2() == 45

test2_solution = ReindeerMaze('test2.txt')
assert test2_solution.get_answer_1() == 11048
assert test2_solution.get_answer_2() == 64

solution_1 = ReindeerMaze('data.txt')
# answer_1 = solution_1.get_answer_1()
# print(f'Task 1 Answer: {answer_1}')
answer_2 = solution_1.get_answer_2()
print(f'Task 2 Answer: {answer_2}')
