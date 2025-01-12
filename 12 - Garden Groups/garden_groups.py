'''
Author: Guy Pickering
Date:

Puzzle:

Part 1

Part 2

'''
from selectors import SelectSelector

directions = ['N', 'E', 'S', 'W']
dx_dy_list = [(0, -1), (1, 0), (0, 1), (-1, 0)]
start_from = ['W', 'N', 'E', 'S']


class Region:
    def __init__(self, crop: str, points: [(int,int)]):
        self.points = points
        self.map = []
        self.crop = crop
        self.area = len(points)

        (x_min, x_max, y_min, y_max) = Region._boundary(points)

        width = x_max - x_min
        height = y_max - y_min

        for y in range(0, height+1):
            self.map.append('.'*(width+1))

        for point in points:
            (x,y) = point
            row = self.map[y-y_min]
            self.map[y-y_min] = row[:x-x_min] + self.crop + row[x-x_min+1:]

        self.perimeter = self.calculate_perimeter()

    def get_crop(self, point: (int, int)):
        (x, y) = point

        if 0 <= x < self.width and 0 <= y < self.height:
            return self.map[y][x]
        else:
            return None

    def find_start(self) -> (int, int):
        for y in range(0, self.height):
            for x in range(0, self.width):
                if self.map[y][x] != '.':
                    return (x,y)

    def find_next(self, pos: (int, int), direction: str) -> (int, int, str):
        search_i = directions.index(start_from[directions.index(direction)])
        for i in range(0, 4):
            dx_dy = dx_dy_list[(search_i + i) % 4]
            (dx, dy) = dx_dy
            (x, y) = pos
            pos_next = (x + dx, y + dy)
            (x1, y1) = pos_next
            if 0 <= x1 < self.width and 0 <= y1 < self.height and self.map[y1][x1] != '.':
                direction = directions[dx_dy_list.index(dx_dy)]
                return (x1, y1, direction)

        return (x, y, direction)

    def calculate_point_perimeter(self, point: (int, int)) -> int:
        (x, y) = point
        perimeter = 0
        for dx_dy in dx_dy_list:
            (dx, dy) = dx_dy
            (x1, y1) = (x+dx, y+dy)
            crop = self.get_crop((x1, y1))
            if crop is None or crop == '.':
                perimeter += 1

        return perimeter

    def calculate_perimeter(self):
        perimeter = 0
        for y in range(0, self.height):
            for x in range(0, self.width):
                if self.get_crop((x, y)) != '.':
                    perimeter += self.calculate_point_perimeter((x,y))
        return perimeter

        # start_pos = self.find_start()
        # direction = 'E'
        #
        # p = 0
        # pos = start_pos
        # visited = []
        # while pos not in visited:
        #     visited.append(pos)
        #     p += self.calculate_point_perimeter(pos)
        #
        #     (x, y) = pos
        #     (x1, y1, new_direction) = self.find_next(pos, direction)
        #     pos = (x1, y1)
        #     direction = new_direction
        #
        # return p

    def _calculate_sides(self,
                         direction: str):
        range_i = self.height if direction in ['N', 'S'] else self.width
        range_j = self.width if direction in ['N', 'S'] else self.height

        delta = (0, -1) if direction == 'N' else \
                (0, 1) if direction == 'S' else \
                (1, 0) if direction == 'E' else (-1, 0)
        (dx, dy) = delta

        total_sides = 0
        for i in range(0, range_i):
            found_edge = False
            for j in range(0, range_j):
                (x, y) = (j, i) if direction == 'N' else \
                         (i, j) if direction == 'E' else \
                         (j, range_i-i-1) if direction == 'S' else (range_i-i-1, j)

                (x1, y1) = (x+dx, y+dy)

                c0 = self.get_crop((x, y))
                c1 = self.get_crop((x1, y1))
                if (c1 is None or c1 == '.') and (c0 is not None and c0 != '.'):
                    if not found_edge:
                        found_edge = True
                        total_sides += 1
                else:
                    found_edge = False

        return total_sides

    def calculate_sides(self):
        total_sides = 0
        total_sides += self._calculate_sides('S')
        total_sides += self._calculate_sides('N')
        total_sides += self._calculate_sides('E')
        total_sides += self._calculate_sides('W')
        return total_sides

    @staticmethod
    def _boundary(points) -> (int, int, int, int):
        x_min = None
        x_max = None
        y_min = None
        y_max = None

        for point in points:
            (x, y) = point
            x_min = x if x_min is None or x < x_min else x_min
            y_min = y if y_min is None or y < y_min else y_min
            x_max = x if x_max is None or x > x_max else x_max
            y_max = y if y_max is None or y > y_max else y_max

        return (x_min, x_max, y_min, y_max)

    @property
    def width(self):
        if not self.map:
            return 0
        else:
            return len(self.map[0])

    @property
    def height(self):
        return len(self.map)

    def __str__(self):
        return self.crop

class Regions(list):
    def is_in_region(self, point: (int, int)) -> bool:
        for region in self:
            if point in region.points:
                return True

        return False

class GardenGroups:
    def __init__(self, filename: str):
        self.map = []
        self._load_data(filename)

    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            for row in f:
                self.map.append(row.strip())

    @property
    def width(self):
        return len(self.map[0])

    @property
    def height(self):
        return len(self.map)

    def get_crop(self, point: (int, int)):
        (x, y) = point

        if 0 <= x < self.width and 0 <= y < self.height:
            return self.map[y][x]
        else:
            return None

    def extract_points(self, point: (int, int), points: [(int, int)]=None) -> [(int, int)]:
        if points is None:
            points = []

        if point in points:
            return []

        (x, y) = point

        crop = self.get_crop(point)

        points.append(point)

        for dx_dy in dx_dy_list:
            (dx, dy) = dx_dy
            (x1, y1) = (x+dx, y+dy)
            c1 = self.get_crop((x1, y1))
            if c1 is not None and c1 == crop and (x1, y1) not in points:
                points = self.extract_points(point=(x+dx, y+dy),
                                             points=points)

        return points

    def extract_region(self, point: (int, int)) -> Region:
        crop = self.get_crop(point)
        points = self.extract_points(point)
        return Region(crop=crop, points=points)

    def extract_regions(self) -> [Region]:
        regions = Regions()

        for y in range(0, self.height):
            for x in range(0, self.width):
                if regions.is_in_region((x, y)):
                    continue
                else:
                    region = self.extract_region((x, y))
                    regions.append(region)

        return regions

    def get_answer_1(self) -> int:
        regions = self.extract_regions()
        total_cost = 0
        for region in regions:
            area = region.area
            perimeter = region.perimeter
            cost = area*perimeter
            total_cost += cost

        return total_cost


    def get_answer_2(self) -> int:
        regions = self.extract_regions()
        total_cost = 0
        for region in regions:
            area = region.area
            sides = region.calculate_sides()
            cost = area*sides
            total_cost += cost

        return total_cost


test1_solution = GardenGroups('test1.txt')
assert test1_solution.get_answer_1() == 140
assert test1_solution.get_answer_2() == 80

test2_solution = GardenGroups('test2.txt')
assert test2_solution.get_answer_1() == 772

test3_solution = GardenGroups('test3.txt')
assert test3_solution.get_answer_1() == 1930

solution_1 = GardenGroups('data.txt')
answer_1 = solution_1.get_answer_1()
print(f'Task 1 Answer: {answer_1}')

solution_2 = GardenGroups('data.txt')
answer_2 = solution_2.get_answer_2()
print(f'Task 2 Answer: {answer_2}')