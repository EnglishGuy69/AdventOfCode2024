"""
Author: Guy Pickering

Date: 12-02-2024

Puzzle
======
The data file contains a list of reports with levels separated by spaces.

Part 1:
A report is deemed safe if the levels are all ascending or all descending and the difference between each level
is >= 1 and <= 3.

Part 2:
A "solution damper" means that a report is deemed safe as defined by Part 1, but also if any single level is removed
that would cause the report to be not safe.

Notes: Part 2 is based on a naive approach of simply removing each level in turn and testing if it is safe. It could
be possible to leverage the 'unsafe_diffs' to remove only unsafe fields (or the fields before them), but the testing
would be significantly more involved. Given the volume of data (and okay performance), I chose to go with the simpler
'brute-force' approach.
"""

class RedNosedReports:
    def __init__(self, filename='data.txt'):
        self.reports = []
        self.load_file(filename)

    def load_file(self, filename):
        with open(filename, 'r') as f:
            self.reports = [[int(x) for x in row.strip().split(' ')] for row in f]

    @staticmethod
    def _is_safe(report: [int]):
        diffs = [report[i + 1] - report[i] for i in range(0, len(report) - 1)]

        if diffs[0] > 0:
            unsafe_diffs = [0 if 1 <= x <= 3 else 1 for x in diffs]
        else:
            unsafe_diffs = [0 if -3 <= x <= -1 else 1 for x in diffs]

        return sum(unsafe_diffs) == 0

    def count_safe_reports(self, enable_damper=False):
        safe_count = 0

        for report in self.reports:
            if RedNosedReports._is_safe(report):
                safe_count += 1
            elif enable_damper:
                for i in range(0, len(report)):
                    partial_report = report[0:i] + report[i+1:]
                    if RedNosedReports._is_safe(partial_report):
                        safe_count += 1
                        break

        return safe_count

solution_test = RedNosedReports('test.txt')
assert solution_test.count_safe_reports() == 2
assert solution_test.count_safe_reports(enable_damper=True) == 4

solution = RedNosedReports('data.txt')
part_1_answer = solution.count_safe_reports()
print(f'Part 1: Safe reports = {part_1_answer}')
part_2_answer = solution.count_safe_reports(enable_damper=True)
print(f'Part 2: Safe reports with damper = {part_2_answer}')

