'''
Author: Guy Pickering
Date: 12-15-2024

Puzzle:

Part 1
A robot '@' moves around a warehouse pushing blocks 'O' and bounded/blocked by walls '#'. If a block is blocked by a
wall (one or more contiguous blocks against a wall), the robot will not move in the specified direction and will
continue on to the next move. Once all moves have been made, the 'score' is calculated by adding up a score for each
box = y*100+x where x and y are the locations in the warehouse (ignoring the walls).

Part 2
In part 2, the scale of the warehouse is doubled width-wise, with each wall block now being '##' and each box
being '[]'. The robot remains a single '@' (or more accurately '@.' when initially placed). The score calculation is the
same, but will include the full width of the block.

Design Notes
Initially, we simply converted the map into positions of the walls, boxes and robot. Each of these is modeled as a
WarehouseObject that is also given access to the map (WarehouseWoes). Each object can answer whether it can be moved
by asking any adjacent objects (in the direction of movement) whether they can move - if a wall is asked, it is 'fixed'
and so cannot move and thus any objects adjacent to it cannot move (in that direction) all the way back to the robot.

In part 2, a single block can touch two blocks if the blocks overlap, e.g.

    [][]
     []
     ^

In this case, we must identify which blocks are adjacent and ask each block if it can move. We achieve this by
calculating each of the positions in a block (and wall) and using them to identify adjacent blocks. We have actually
generalized this approach to support arbitrary width and height block/wall sizes, but only 2x1 are included in the
puzzle.
'''

directions = ['<', '>', '^', 'v']
direction_dx_dy = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def generate_positions(origin: (int, int), w: int, h: int) -> [[(int,int)]]:
    (x0, y0) = origin
    positions = []
    for y in range(0, h):
        row = []
        for x in range(0, w):
            row.append((x0+x, y0+y))

        positions.append(row)

    return positions

class WarehouseObject:
    def __init__(self,
                 position: (int, int),
                 object_width: int,
                 object_height: int,
                 object_type: str,
                 warehouse: "WarehouseWoes"):
        self.origin_position = position
        self.positions = generate_positions(origin=position, w=object_width, h=object_height)
        self.object_type = object_type
        self.warehouse = warehouse
        self.width = object_width
        self.height = object_height
        self.fixed = True if self.object_type == WarehouseWoes.WALL else False

    def _filter_positions(self, filter_column: int|None, filter_row: int|None) -> [(int, int)]:
        positions = []
        for r in range(0, self.height):
            for c in range(0, self.width):
                if (filter_column is None or (filter_column is not None and c == filter_column)) and \
                        (filter_row is None or (filter_row is not None and r == filter_row)):
                    positions.append(self.positions[r][c])

        return positions

    def find_next_positions(self, direction: str) -> [(int, int)]:
        (dx, dy) = direction_dx_dy[directions.index(direction)]

        edge_positions: [(int,int)]
        if direction == '^':
            edge_positions = self._filter_positions(filter_column=None, filter_row=0)
        elif direction == 'v':
            edge_positions = self._filter_positions(filter_column=None, filter_row=self.height-1)
        elif direction == '>':
            edge_positions = self._filter_positions(filter_column=self.width-1, filter_row=None)
        elif direction == '<':
            edge_positions = self._filter_positions(filter_column=0, filter_row=None)

        next_positions = [(x+dx, y+dy) for (x, y) in edge_positions]

        return next_positions

    def find_next_objects(self, direction: str) -> ["WarehouseObject"]:
        next_positions = self.find_next_positions(direction=direction)
        next_objects = []
        for np in next_positions:
            o = self.warehouse.get_object(np)
            if o and o.origin_position not in [next_object.origin_position for next_object in next_objects]:
                next_objects.append(o)

        return next_objects

    def contains_position(self, position: (int,int)):
        for row in self.positions:
            for o in row:
                if o == position:
                    return True

        return False

    def can_move(self, direction: str) -> bool:
        if self.fixed:
            return False

        next_objects = self.find_next_objects(direction=direction)

        o: WarehouseObject
        for o in next_objects:
            if not o.can_move(direction):
                return False

        return True

    def move(self, direction: str) -> bool:
        if self.fixed:
            return False
        else:
            if self.can_move(direction):
                next_objects = self.find_next_objects(direction)
                for o in next_objects:
                    o.move(direction)

                (x, y) = self.origin_position
                (dx, dy) = direction_dx_dy[directions.index(direction)]

                self.origin_position = (x+dx, y+dy)
                self.positions = generate_positions(self.origin_position, self.width, self.height)

            return True

    def symbol(self, x: int, y: int):
        if self.warehouse.width_multiplier == 1:
            return self.object_type
        elif self.object_type == WarehouseWoes.BOX:
            (xx, yy) = self.positions[0][0]
            if xx == x:
                return '['
            else:
                return ']'
        else:
            return self.object_type

    @property
    def score(self) -> int:
        (x,y) = self.origin_position
        return 100*y + x

    def __str__(self):
        return f'{self.object_type} {self.origin_position}'

class WarehouseWoes:
    WALL = '#'
    BOX = 'O'
    ROBOT = '@'

    def __init__(self,
                 filename: str,
                 width_multiplier: int=1,
                 height_multiplier: int=1,
                 debug:bool=False):
        self.debug = debug
        self.map = []
        self.walls = []
        self.boxes = []
        self.robot = None
        self.instructions = ''
        self.width_multiplier = width_multiplier
        self.height_multiplier = height_multiplier
        self.object_sizes = {'#': (width_multiplier, height_multiplier), 'O': (width_multiplier, height_multiplier), '@': (1, 1)}
        self._load_data(filename)

    def _find_positions(self, s: str, y: int, token: str):
        x_list = [x for x, c in enumerate(s) if c == token]
        return [(x*self.width_multiplier, y*self.height_multiplier) for x in x_list]

    @property
    def width(self):
        return len(self.map[0])*self.width_multiplier

    @property
    def height(self):
        return len(self.map)*self.height_multiplier

    def get_object(self, position: (int, int)) -> WarehouseObject|None:
        (x,y) = position

        if 0 <= x <= self.width and 0 <= y < self.height:
            if self.robot.origin_position == position:
                return self.robot

            wall = [o for o in self.walls if o.contains_position(position)]
            if wall:
                return wall[0]

            box = [o for o in self.boxes if o.contains_position(position)]
            if box:
                return box[0]

            return None
        else:
            return None

    def _create_objects(self, s: str, y: int, object_type: str) -> [WarehouseObject]:
        objects = []
        positions = self._find_positions(s, y, object_type)

        (object_width, object_height) = self.object_sizes[object_type]

        for position in positions:
            objects.append(WarehouseObject(position=position,
                                           object_width=object_width,
                                           object_height=object_height,
                                           object_type=object_type,
                                           warehouse=self))

        return objects

    def reset_objects(self):
        self.walls = []
        self.boxes = []
        for y in range(0, self.height):
            self.walls.extend(self._create_objects(self.map[y], y, WarehouseWoes.WALL))
            self.boxes.extend(self._create_objects(self.map[y], y, WarehouseWoes.BOX))
            robots = self._create_objects(self.map[y], y, WarehouseWoes.ROBOT)
            if robots: self.robot = robots[0]

    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            for y, row in enumerate(f):
                if row.strip() == '':
                    break
                else:
                    self.map.append(row.strip())

            for row in f:
                self.instructions += row.strip()

        self.reset_objects()

    def _calc_score(self):
        return sum(o.score for o in self.boxes)

    def render(self):
        for y in range(0, self.height):
            for x in range(0, self.width):
                o = self.get_object((x, y))
                print(f'{o.symbol(x,y) if o else "."}', end='')
            print('')

    def get_answer_1(self) -> int:
        if self.debug: self.render()
        if self.debug: print('')
        for direction in self.instructions:
            if self.debug: print(f'Move: {direction}')
            self.robot.move(direction)
            if self.debug: self.render()
            if self.debug: print('')
            pass

        score = self._calc_score()

        self.reset_objects()

        return score

    def get_answer_2(self) -> int:
        return 0


test_solution = WarehouseWoes('test.txt')
assert test_solution.get_answer_1() == 10092

test2_solution = WarehouseWoes('test.txt', width_multiplier=2, height_multiplier=1)
test2_solution.render()
assert test2_solution.get_answer_1() == 9021

solution_1 = WarehouseWoes('data.txt')
answer_1 = solution_1.get_answer_1()
print(f'Task 1 Answer: {answer_1}')

solution_2 = WarehouseWoes('data.txt', width_multiplier=2)
answer_2 = solution_2.get_answer_1()
print(f'Task 2 Answer: {answer_2}')
