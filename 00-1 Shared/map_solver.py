from map import Map, MapBase, MapWithStartAndEnd
import copy
from typing import Optional, Tuple


class MapSolver:
    _debug = False

    def __init__(self, map: MapBase,
                 allow_diagonal_movement=False):
        self._map = map
        self.allow_diagonal_movement = allow_diagonal_movement
        self._distance_map = self._generate_distance_map()
        self._populate_distance_map(self.distance_map)

    @property
    def map(self):
        return self._map

    @property
    def distance_map(self) -> [[int]]:
        return self._distance_map

    def _generate_distance_map(self) -> [[]]:
        distance_map = []
        for y in range(0, self._map.height):
            distance_row = []
            for x in range(0, self._map.width):
                distance_row.append(-1)
            distance_map.append(distance_row)

        return distance_map

    def allow_movement_to(self, to_position: (int, int)):
        """
        This function may be overridden by more complex solver classes

        :param to_position: The position we are trying to move to.
        :return: True if allowed to move to the location
        """
        return True

    def coverage(self):
        valid_spaces = 0
        visited_spaces = 0
        for y in range(0, self.map.height):
            for x in range(0, self.map.width):
                if self.map.map[y][x] != Map.WALL:
                    valid_spaces += 1
                    if self._distance_map[y][x] != -1:
                        visited_spaces += 1
        return 100.0 * visited_spaces / valid_spaces

    def _populate_distance_map(self, distance_map: [[int]]):
        distance = 0
        positions = [self._map.start]
        (end_x, end_y) = self._map.end
        n = 0
        while distance_map[end_y][end_x] < 0 and positions:
            n += 1
            if MapSolver._debug:
                if n % 10000 == 0:
                    print(f'Progress: {self.coverage()}%', end='\n')
            next_positions = []
            for pos in positions:
                if not self.allow_movement_to(pos): continue

                (x,y) = pos
                if distance_map[y][x] == -1 or distance_map[y][x] > distance:
                    distance_map[y][x] = distance
                    next_positions.extend(self._map.open_positions_around_position(position=pos,
                                                                                   allow_diagonal=self.allow_diagonal_movement))

            distance += 1
            positions = next_positions

        return distance_map

    def is_dead_end(self, position: (int,int)) -> bool:
        (x,y) = position
        current_distance = self._distance_map[y][x]
        possible_next_steps = self._map.open_positions_around_position(position=position, allow_diagonal=self.allow_diagonal_movement)
        possible_next_steps = [(x1, y1) for (x1, y1) in possible_next_steps if
                               self._distance_map[y1][x1] > current_distance]
        return len(possible_next_steps) == 0

    def find_dead_ends(self):
        dead_ends:[(int,int)] = []
        for y in range(0, self._map.height):
            for x in range(0, self._map.width):
                if self._map.map[y][x] == Map.WALL:
                    continue

                if (x,y) == self._map.end:  # don't count the end location as a dead-end.
                    continue

                if self.is_dead_end((x,y)):
                    dead_ends.append((x,y))

        return dead_ends

    def _purge_dead_ends(self, dead_end_position: (int,int)):
        (x,y) = dead_end_position
        self._distance_map[y][x] = -1

        possible_dead_ends = self._map.open_positions_around_position(dead_end_position)
        possible_dead_ends = [(x1,y1) for (x1,y1) in possible_dead_ends if self._distance_map[y1][x1] >= 0]
        for possible_dead_end in possible_dead_ends:
            if self.is_dead_end(possible_dead_end):
                self._purge_dead_ends(possible_dead_end)

    def purge_dead_ends(self):
        dead_ends = self.find_dead_ends()

        for dead_end in dead_ends:
            self._purge_dead_ends(dead_end_position=dead_end)

    def find_shortest_route_distance(self, allow_diagonal=False) -> int:
        (end_x, end_y) = self._map.end
        return self._distance_map[end_y][end_x]

    def _find_next_positions(self,
                             position: (int,int),
                             exclude_positions: Optional[Tuple[int,int]] = None,
                             follow_all_paths=False):

        (x0,y0) = position

        current_distance = self._distance_map[y0][x0]

        possible_next_positions = self._map.open_positions_around_position(position=position,
                                                                           allow_diagonal=self.allow_diagonal_movement)

        next_positions = []
        for next_pos in possible_next_positions:
            if exclude_positions and next_pos in exclude_positions:
                continue

            (next_x,next_y) = next_pos
            next_distance = self._distance_map[next_y][next_x]
            if follow_all_paths or next_distance == current_distance + 1:
                next_positions.append(next_pos)

        return next_positions

    def get_distance(self, position: (int, int)) -> int:
        (x,y) = position
        return self.distance_map[y][x]

                                                          # (x,y), distance
    def _create_route_step(self, position: (int, int)) -> ((int,int),int):
        return position, self.get_distance(position)

    def find_all_shortest_routes(self,
                                 start_position: Optional[Tuple[int, int]] = None,  #  x,   y,   d
                                 end_position: Optional[Tuple[int, int]] = None) -> [[((int, int), int)]]:
        if start_position is None: start_position = self._map.start
        if end_position is None: end_position = self._map.end

        if start_position == end_position:
            return []

        current_route = []  # this part of the recursion will start with only a section of non-branching steps
        position = start_position
        while True:
            if position == end_position:        # if we hit the end, simply return this non-branching section
                current_route.append(self._create_route_step(position))
                return [current_route]

            next_positions = self._find_next_positions(position)  # Look for the next possible steps
            assert len(next_positions) != 0                       # We do not expect dead-ends!!!

            if len(next_positions) == 1:                          # No branch: simply extend the non-branching section
                current_route.append(self._create_route_step(position))
                position = next_positions[0]
            else:                                                 # Branch: recurse to locate all subsequent route
                current_route.append(self._create_route_step(position))
                routes = []                                       # combinations, store them and return them
                for next_position in next_positions:
                    additional_routes = self.find_all_shortest_routes(next_position, end_position)
                    for additional_route in additional_routes:
                        routes.append(current_route + additional_route)
                return routes

    def find_all_routes(self,
                        start_position: Optional[Tuple[int, int]] = None,  #  x,   y,   d
                        end_position: Optional[Tuple[int, int]] = None,
                        visited_positions: Optional[Tuple[int,int]] = None) -> [[((int, int), int)]]:
        if start_position is None: start_position = self._map.start
        if end_position is None: end_position = self._map.end
        if visited_positions is None: visited_positions = []

        if start_position == end_position:
            return []

        current_route = []  # this part of the recursion will start with only a section of non-branching steps
        position = start_position
        while True:
            visited_positions.append(position)

            if position == end_position:        # if we hit the end, simply return this non-branching section
                current_route.append(self._create_route_step(position))
                return [current_route]

            next_positions = self._find_next_positions(position, # Look for the next possible steps
                                                       exclude_positions=visited_positions,
                                                       follow_all_paths=True)
            if len(next_positions) == 0:  # dead-end, return empty routes
                return []

            if len(next_positions) == 1:                          # No branch: simply extend the non-branching section
                current_route.append(self._create_route_step(position))
                position = next_positions[0]
            else:                                                 # Branch: recurse to locate all subsequent route
                current_route.append(self._create_route_step(position))
                routes = []                                       # combinations, store them and return them
                for next_position in next_positions:
                    additional_routes = self.find_all_routes(next_position,
                                                             end_position,
                                                             copy.copy(visited_positions))
                    for additional_route in additional_routes:
                        routes.append(current_route + additional_route)
                return routes

    def _max_number_width(self):
        return max([max([len(str(d)) for d in row]) for row in self._distance_map])

    def _is_populated(self, o: int):
        return o >= 0

    def render(self,
               overlay_route: Optional[Tuple[int,int]] = None,
               overlay_shortcut: Optional[list[Tuple[int,int]]] = None,
               top_left: Optional[Tuple[int,int]] = None,
               bottom_right: Optional[Tuple[int,int]] = None):
        distance_map = self._distance_map
        max_number_width = self._max_number_width()

        if overlay_route and isinstance(overlay_route[0][0],tuple):
            overlay_route = [p for (p,d)  in overlay_route]
        if overlay_shortcut and isinstance(overlay_shortcut[0][0],tuple):
            overlay_shortcut = [p for (p,d)  in overlay_shortcut]

        x_min = 0
        x_max = self.map.width
        y_min = 0
        y_max = self.map.height

        if top_left:
            (x_min, y_min) = top_left

        if bottom_right:
            (x_max, y_max) = bottom_right

        shortcut_locations = [position for (position, distance) in overlay_shortcut] if overlay_shortcut else []
        for y in range(y_min, y_max):
            for x in range(x_min, x_max):
                if self._map.map[y][x] == Map.WALL:
                    print(f'{Map.WALL * (max_number_width + 2)} ', end='')
                elif overlay_route and (x, y) in overlay_route:
                    print(f'{"O" * (max_number_width + 2)} ', end='')
                elif not self._is_populated(self._distance_map[y][x]):
                    print(f'{"X"*(max_number_width+2)} ', end='')
                elif overlay_shortcut and (x,y) in shortcut_locations:
                    print(f'{"*"*(max_number_width+2)} ', end='')
                else:
                    print(f'[{str(distance_map[y][x]): >{max_number_width}}] ',end='')
            print('')


if __name__ == '__main__':
    # map = MapWithStartAndEnd('test_map.txt')
    # solver = MapSolver(map)
    # solver.find_shortest_route()

    map = MapWithStartAndEnd('test_map_2.txt')
    solver = MapSolver(map)
    solver.render()
    solver.purge_dead_ends()
    print('')
    solver.render()
    shortest_routes = solver.find_all_shortest_routes()
    assert len(shortest_routes) == 4
    for route in shortest_routes:
        print('')
        solver.render(overlay_route=route)
    solver.find_shortest_route_distance()

    print('=================== All Routes ====================')
    all_routes = solver.find_all_routes()
    assert len(all_routes) == 8
    for route in all_routes:
        print('')
        solver.render(overlay_route=route)
    solver.find_shortest_route_distance()
