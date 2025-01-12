'''
Author: Guy Pickering
Date: 12-09-2024

Puzzle:
The disk map consists of pairs of numbers representing the number of blocks (in a file) and the amount of space, e.g.

    12345   -> 0..111....22222

Each file has an ID, 0, 1, 2. The checksum is the position on the disk multiplied by the ID of the file at
that position. E.g. 0*0, 3x1, 4x1, 5x1, 10x2, 11x2, 12x2, 13x2, 14x2, 15x2.

Part 1
Perform a 'defragmentation' process to move the files from the right as far left as they can go. Splitting of the
file is allowed. Calculate the checksum.

Part 2
Change the defragmentation to only move a file left if there is a space big enough for all the blocks in a file
(with the same ID) to be moved. Otherwise, skip that file and keep going. Calculate the checksum.

'''

class FileIdCounter:
    def __init__(self):
        self.id_counter = 0

    def take_id(self):
        self.id_counter += 1
        return self.id_counter - 1


class DiskFile:
    '''
        A segment of a file, with a length and optionally some space. Each file segment contains the ID for the
        file. This is either generated during load automatically (using the FileIdCounter) or inherited during
        file segment moves.
    '''

    def __init__(self,
                 length: int,
                 space: int,
                 id: int|None = None,
                 id_counter: FileIdCounter | None = None):
        self.length = length
        self.space = space
        if id is not None:
            self.id = id
        else:
            self.id = id_counter.take_id()

    @property
    def total_size(self):
        return self.length + self.space

    def __str__(self):
        return f'<{self.id}>[{self.length}][{self.space}]'


class FileSegments(list):
    def total_length(self):
        return sum([b.length+b.space for b in self])

    def inject_file_segment(self, position: int, from_file: DiskFile) -> int:
        """
        This will attempt to inject a block to accommodate the required length. If there is not enough space, it
        will fill what it can, then return the number of remaining length that could not be filled.

        :param position: The location of the file segment after which to inject some/all of the from_file
        :param from_file: The file segment to move.
        :return: the un-stored length
        """

        prior_file_segment: DiskFile = self[position]

        available_space = prior_file_segment.space
        remaining_length = 0 if available_space >= from_file.length else from_file.length - available_space
        new_file_segment_length = from_file.length - remaining_length
        prior_file_segment_remaining_space = available_space - new_file_segment_length

        # Create a new segment, inheriting the ID of the from_file.
        new_file_segment = DiskFile(length=new_file_segment_length,
                                    space=prior_file_segment_remaining_space,
                                    id=from_file.id)
        self.insert(position+1, new_file_segment)

        # Update the from_file to reflect what has been moved
        from_file.space += from_file.length - remaining_length
        from_file.length = remaining_length
        prior_file_segment.space = 0

        return remaining_length

    def find_next_empty_file_segment_position(self,
                                              last_full_file_segment_pos: int,
                                              min_required_size: int):
        for i in range(last_full_file_segment_pos, len(self)):
            if self[i].space >= min_required_size:
                return i

        return -1

    def find_next_file_segment_to_move_position(self, pos: int, first_empty_file_segment_pos: int) -> int:
        while self[pos].length == 0:
            pos -= 1
            if pos <= first_empty_file_segment_pos:
                return -1

        return pos

    def compact_blocks(self, force_full_files_only: bool = False):
        low_i = 0
        high_i = len(self)-1

        while True:
            next_file_segment_to_move_pos = self.find_next_file_segment_to_move_position(high_i, low_i)
            if next_file_segment_to_move_pos == -1:
                break

            from_file_segment = self[next_file_segment_to_move_pos]

            min_required_size = 1 if not force_full_files_only else from_file_segment.length

            next_empty_file_segment = self.find_next_empty_file_segment_position(last_full_file_segment_pos=low_i,
                                                                                 min_required_size=min_required_size)


            if next_empty_file_segment == -1 or next_empty_file_segment >= next_file_segment_to_move_pos:
                if force_full_files_only:
                    high_i = next_file_segment_to_move_pos-1 # move to the next block
                    if high_i > low_i:
                        continue        # Skip the block and move on
                    else:
                        break           # Run out of blocks to move, quit
                else:
                    break

            from_total_size = from_file_segment.total_size
            remaining_size = self.inject_file_segment(next_empty_file_segment, from_file_segment)
            if remaining_size > 0:
                high_i += 1  # a block was injected, so we have to move right
            else:
                self[high_i].space += from_total_size
                self.pop(high_i+1)  # Remove the moved block

            while self[low_i].space ==0:
                low_i += 1

        # if len(self) < 100:
        #     s = self.as_string()
        #     pass

    def as_string(self):
        s = ''
        for file_segment in self:
            if file_segment.length > 0:
                s += str(file_segment.id)*file_segment.length + '.'*file_segment.space

        return s

    @property
    def checksum(self):
        p = 0
        checksum = 0
        for file_segment in self:
            for i in range(0, file_segment.length):
                checksum += p*file_segment.id
                p += 1

            for i in range(0, file_segment.space):
                p += 1

        return checksum


class DiskFragmenter:
    def __init__(self, filename: str):
        self.file_segments: FileSegments = FileSegments()
        self.id_counter = FileIdCounter()

        self._load_data(filename)

    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            for row in f:
                row = row.strip() + '0'
                self.file_segments.extend([DiskFile(int(row[i]),
                                                    int(row[i+1]),
                                                    id=None,
                                                    id_counter=self.id_counter) for i in range(0, len(row), 2)])

    def get_answer_1(self) -> int:
        self.file_segments.compact_blocks()
        return self.file_segments.checksum

    def get_answer_2(self) -> int:
        self.file_segments.compact_blocks(force_full_files_only=True)
        return self.file_segments.checksum


test_solution = DiskFragmenter('test.txt')
assert test_solution.get_answer_1() == 1928
test2_solution = DiskFragmenter('test.txt')
assert test2_solution.get_answer_2() == 2858

solution_1 = DiskFragmenter('data.txt')
answer_1 = solution_1.get_answer_1()
print(f'Task 1 Answer: {answer_1}')

solution_2 = DiskFragmenter('data.txt')
answer_2 = solution_2.get_answer_2()
print(f'Task 2 Answer: {answer_2}')