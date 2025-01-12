'''
Author: Guy Pickering
Date:

Puzzle:

Part 1

Part 2

'''

from map import Map, MapWithStartAndEnd
from map_solver import MapSolver

class RaceCondition(MapWithStartAndEnd):
    def __init__(self, filename: str):
        super().__init__(filename)

    def calc_saving(self,
                    route_step_1: ((int, int),int),
                    route_step_2: ((int,int), int)) -> int:
        """
        The saving will be the difference in x and y distance between point one and point two. I.e. it takes time to
        complete the shortcut.

        :param route_step_1: ((x1,y1),d) - position + distance for point 1
        :param route_step_2: ((x2,y2),d) - position + distance for point 2
        :return: saving in picoseconds
        """
        ((x1,y1), d1) = route_step_1
        ((x2,y2), d2) = route_step_2

        return d2 - d1 - abs(x2-x1) - abs(y2-y1)

    def find_shortcuts_v2(self,
                          route: [((int, int), int)],  # ((x,y),distance)
                          max_shortcut: int = 2,
                          min_saving: int = 100):
        len_route = len(route)
        num_shortcuts = 0

        shortcuts = []
        for r1 in range(0, len_route):
            for r2 in range(r1+1, len_route):
                step_1 = route[r1]
                step_2 = route[r2]
                ((x1,y1),d1) = step_1
                ((x2,y2),d2) = step_2

                if abs(x2-x1) + abs(y2-y1) > max_shortcut:
                    continue



                if self.calc_saving(route_step_1=step_1,
                                    route_step_2=step_2) >= min_saving:
                    shortcuts.append((step_1, step_2))
                    num_shortcuts += 1

        return num_shortcuts


    def find_shortcuts(self,
                       map_solver: MapSolver,
                       route: [((int,int), int)],
                       max_shortcut: int=2,
                       min_saving: int=100):
        dx_dy = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        route_positions = [p for (p, d) in route]

        savings = {}
        found_shortcuts = 0
        for (position, distance) in route:
            (x, y) = position
            distance = map_solver.distance_map[y][x]

            for (dx, dy) in dx_dy:
                for n in range(2, max_shortcut+1):
                    (x1, y1) = (x + n*dx, y + n*dy)
                    if (x1, y1) in route_positions:
                        shortcut_distance = map_solver.distance_map[y1][x1]
                        shortcut_amount = shortcut_distance - distance - n
                        if shortcut_amount >= min_saving:
                            if shortcut_amount in savings:
                                savings[shortcut_amount] += 1
                            else:
                                savings[shortcut_amount] = 1
                            found_shortcuts += 1
                            # print(f'Saving of {shortcut_amount}')
                            # map_solver.render(overlay_shortcut=[(x+nn*dx,y+nn*dy) for nn in range(0, n+1)])
                            # pass

        return found_shortcuts




    def get_answer_1(self, max_shortcut: int, min_saving: int) -> int:
        map_solver = MapSolver(self)
        map_solver.purge_dead_ends()
        routes = map_solver.find_all_shortest_routes()
        #map_solver.render()
        num_shortcuts = self.find_shortcuts_v2(route=routes[0],
                                               max_shortcut=max_shortcut,
                                               min_saving=min_saving)

        return num_shortcuts

    def get_answer_2(self) -> int:
        return 0


test_solution = RaceCondition('test.txt')
assert test_solution.get_answer_1(max_shortcut=2, min_saving=2) == 44
#assert test_solution.get_answer_2() == 0 # update

solution_1 = RaceCondition('data.txt')
answer_1 = solution_1.get_answer_1(max_shortcut=2, min_saving=100)
print(f'Task 1 Answer: {answer_1}')
answer_2 = solution_1.get_answer_1(max_shortcut=20, min_saving=100)
print(f'Task 2 Answer: {answer_2}')
