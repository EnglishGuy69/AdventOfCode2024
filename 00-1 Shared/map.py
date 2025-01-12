
from direction_mapper import DirectionMapper

class MapBase:
    WALL = '#'
    PATH = '.'

    def __init__(self):
        self.map = []
        self.start = None
        self.end = None

    def populate_empty_map(self, width: int, height: int):
        for y in range(0, height):
            self.map.append('.'*width)

    def can_move_here(self, position: (int, int)):
        (x,y) = position
        return 0 <= x < self.width and 0 <= y < self.height and self.map[y][x] != Map.WALL

    def open_positions_around_position(self, position: (int, int), allow_diagonal=False) -> [(int,int)]:
        (x,y) = position
        dx_dy = [(-1,-1), (0,-1), (1,-1),
                 (-1,0),          (1,0),
                 (-1,1),  (0, 1), (1, 1)]

        open_positions = []
        for (dx, dy) in dx_dy:
            if not allow_diagonal and abs(dx)+abs(dy) == 2:  #skip diagonals if not allowed
                continue

            if self.can_move_here((x+dx, y+dy)):
                open_positions.append((x+dx,y+dy))

        return open_positions

    def open_dx_dy_around_position(self, position: (int, int), allow_diagonal=False) -> [str]:
        (x,y) = position
        dx_dy = [(-1,-1), (0,-1), (1,-1),
                 (-1,0),          (1,0),
                 (-1,1),  (0, 1), (1, 1)]

        open_dx_dy = []
        for (dx, dy) in dx_dy:
            if not allow_diagonal and abs(dx)+abs(dy) == 2:  #skip diagonals if not allowed
                continue

            if self.can_move_here((x+dx, y+dy)):
                open_dx_dy.append((dx,dy))

        return open_dx_dy

    def is_valid(self, position: (int,int)):
        (x,y) = position
        return 0 <= x < self.width and 0 <= y < self.height

    def find_locations(self, c: str) -> [(int,int)]:
        locations = [(x,y) for x in range(0, self.width) for y in range(0, self.height)]
        locations = [(x,y) for (x,y) in locations if self.map[y][x] == c]
        return locations

    def set_location(self, position: (int,int), c: str):
        (x, y) = position
        if not self.is_valid(position):
            raise ValueError(f'({x},{y}) is not on the map!')

        self.map[y] = str(self.map[y][:x]) + c + str(self.map[y][x+1:])

    @property
    def width(self) -> int:
        return len(self.map[0])

    @property
    def height(self) -> int:
        return len(self.map)

    def render(self):
        for row in self.map:
            print(row)

    def __str__(self):
        return f'{self.width}x{self.height} map'

class Map(MapBase):
    def __init__(self, filename: str):
        super().__init__()
        self._load_data(filename)

    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            for row in f:
                self.process_row(row.strip())

    def process_row(self, row: str):
        self.map.append(row)


class MapWithStartAndEnd(Map):
    def __init__(self, filename: str, start_text: str='S', end_text: str='E'):
        self._start_text = start_text
        self._end_text = end_text

        super().__init__(filename)

    def process_row(self, row: str):
        super().process_row(row)
        y = len(self.map)-1
        start_x = row.find(self._start_text)
        end_x = row.find(self._end_text)

        if start_x >= 0:
            self.start = (start_x, y)

        if end_x >= 0:
            self.end = (end_x, y)

if __name__ == '__main__':
    map = MapWithStartAndEnd('test_map.txt')
    assert map.start == (1, 3)
    assert map.end == (5, 7)
