
class DirectionMapper:
    directions_carets: [str] = ['^','>','v','<']
    directions_compass: [str] = ['N','E','S','W']
    dx_dy: [(int,int)] = [(0,-1),(1,0),(0,1),(-1,0)]

    @staticmethod
    def find_dx_dy(c: str):
        if c in DirectionMapper.directions_carets:
            return DirectionMapper.dx_dy[DirectionMapper.directions_carets.index(c.lower())]
        elif c in DirectionMapper.directions_compass:
            return DirectionMapper.dx_dy[DirectionMapper.directions_compass.index(c.upper())]
        else:
            raise ValueError(f'Unknown direction {c}, please use either ^,>,v,< or N,E,S,W')

    @staticmethod
    def find_direction_caret(dx_dy:(int,int)) -> str:
        return DirectionMapper.directions_carets[DirectionMapper.dx_dy.index(dx_dy)]

    @staticmethod
    def find_direction_compass(dx_dy:(int,int)) -> str:
        return DirectionMapper.directions_compass[DirectionMapper.dx_dy.index(dx_dy)]

    @staticmethod
    def _get_dx_dy_from_points(p1: (int,int), p2:(int,int)):
        (x1,y1) = p1
        (x2,y2) = p2
        dx_dy = (x2-x1, y2-y1)
        if dx_dy not in DirectionMapper.dx_dy:
            raise ValueError(f'{str(p1)} and {str(p2)} are not next to each other!')

        return dx_dy

    @staticmethod
    def find_direction_caret_between_points(p1: (int,int), p2:(int,int)) -> str:
        dx_dy = DirectionMapper._get_dx_dy_from_points(p1, p2)
        return DirectionMapper.find_direction_caret(dx_dy)

    @staticmethod
    def find_direction_compass_between_points(p1: (int,int), p2:(int,int)) -> str:
        dx_dy = DirectionMapper._get_dx_dy_from_points(p1, p2)
        return DirectionMapper.find_direction_compass(dx_dy)

    @staticmethod
    def opposite(direction: str):
        opposites = {'N': 'S',
                     'S': 'N',
                     'E':' W',
                     'W': 'E',
                     '^': 'v',
                     'v': '^',
                     '>': '<',
                     '<': '>'}

        return opposites[direction]
