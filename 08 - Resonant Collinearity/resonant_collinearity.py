"""
Author: Guy Pickering

Date: 12-08-2024

   #.......
   ........
   ..O.....
   ........
   ....O...
   ........
   ......#.

   a1_x = x1 - (x2-x1)
   a1_y = y1 - (y2-y1)
   a2_x = x2 + (x2-x1)
   a2_y = y2 + (y2-y1)

Design Notes:

"""

import copy

def unique(l: list):
    return list(set(l))

class AntennaMesh:
    """
    AntennaMesh represents all the antenna positions within the map that share the same frequency (i.e. have the same
    symbol). The find_antinodes() function returns the positions of all the locations where the pairs of antennas
    'interfere'. During Part 1, there is only one location (per end). But in Part 2, there can be multiples due to
    the 'harmonics'. The include_harmonics parameter allows the class to be used for both parts.
    """
    def __init__(self, frequency: str):
        self.frequency = frequency
        self.locations = []

    def add_location(self, x: int, y: int):
        self.locations.append((x,y))

    @staticmethod
    def _find_harmonics(x1: int,
                        y1: int,
                        x2: int,
                        y2: int,
                        width: int,
                        height: int,
                        include_harmonics: bool=False):
        antinodes = []
        found_antinode = True

        m = 1
        while found_antinode:  # Keep looping while antinodes remain within the bounds of the map.
            found_antinode = False

            for direction in range(0, 2):  # 0, 1
                if direction:
                    (ax, ay) = (x1-m*(x2-x1), y1-m*(y2-y1))
                else:
                    (ax, ay) = (x2 + m*(x2-x1), y2 + m*(y2-y1))

                if 0 <= ax < width and 0 <= ay < height:
                    antinodes.append((ax, ay))
                    found_antinode = True  # if at least one antinode is within the map, keep looking for harmonics...

            if not include_harmonics: # If harmonics are not required (Part 1), simply skip the loop.
                break

            m += 1

        return unique(antinodes)

    def find_antinodes(self,
                       width: int,
                       height: int,
                       include_harmonics: bool=False) -> [(int,int)]:
        """
        Will list all the locations that antinodes are generated from pairs of antenna positions. Either one antinode
        at each end of the pair (assuming they are not too close to the edge of the map, or aninodes periodically if
        the 'include_harmonics' flag is set (per Part 2 of the puzzle).

        :param width: Width of the map
        :param height: Height of the map
        :param include_harmonics: If True will generate multiple antinodes (each end) vs. just one (per end)
        :return: A list of (x,y) locations of the antinodes
        """

        antinodes = []
        locations = copy.copy(self.locations)
        while locations:
            (x1, y1) = locations.pop()
            if include_harmonics and len(locations) > 0:
                antinodes.append((x1, y1))

            for (x2, y2) in locations:
                antinodes.extend(AntennaMesh._find_harmonics(x1=x1,
                                                             y1=y1,
                                                             x2=x2,
                                                             y2=y2,
                                                             width=width,
                                                             height=height,
                                                             include_harmonics=include_harmonics))
                if include_harmonics:
                    antinodes.append((x2, y2))

        return unique(antinodes)

    def __contains__(self, item):
        return item in self.locations

    def __str__(self):
        return self.frequency + f' ({len(self.locations)})'

class AntennaMeshList(list):
    def __contains__(self, item) -> bool:
        for a in self:
            if a.frequency == item:
                return True
        return False

    def get_antenna_mesh(self, frequency) -> AntennaMesh:
        return next(am for am in self if am.frequency == frequency)


class ResonantCollinearity:
    default_symbol = '.'
    antinode_symbol = '#'

    def __init__(self, filename: str, debug: bool=False):
        self.map = []
        self.meshes = AntennaMeshList()
        self._load_data(filename)
        self._debug = debug

    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            for y, row in enumerate(f):
                map_row = ''
                for x, c in enumerate(row.strip()):
                    if c != ResonantCollinearity.default_symbol:
                        if not c in self.meshes:
                            self.meshes.append(AntennaMesh(c))
                        am = self.meshes.get_antenna_mesh(c)
                        am.add_location(x, y)
                    map_row += c
                self.map.append(map_row)

    @property
    def width(self):
        return len(self.map[0])

    @property
    def height(self):
        return len(self.map)

    def _get_answer(self, include_harmonics=False):
        antinodes = []
        mesh: AntennaMesh
        for mesh in self.meshes:
            antinodes.extend(mesh.find_antinodes(self.width, self.height, include_harmonics=include_harmonics))

        antinodes = unique(antinodes)

        if self._debug:
            s = self.as_string(antinodes)
            print(s)
            print('')

        return len(antinodes)

    def get_answer_1(self) -> int:
        return self._get_answer(include_harmonics=False)

    def get_answer_2(self) -> int:
        return self._get_answer(include_harmonics=True)

    def as_string(self, antinodes: [(int, int)]):
        s = ''
        for y in range(0, self.height):
            for x in range(0, self.width):
                if (x,y) in antinodes:
                    s += ResonantCollinearity.antinode_symbol
                else:
                    s += self.map[y][x]
            s += '\n'
        return s

test_solution = ResonantCollinearity('test.txt')
assert test_solution.get_answer_1() == 14

test2_solution = ResonantCollinearity('test2.txt')
assert test2_solution.get_answer_2() == 9

solution_1 = ResonantCollinearity('data.txt')
answer_1 = solution_1.get_answer_1()
print(f'Task 1 Answer: {answer_1}')

solution_2 = ResonantCollinearity('data.txt')
answer_2 = solution_2.get_answer_2()
print(f'Task 2 Answer: {answer_2}')