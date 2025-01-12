'''
Author: Guy Pickering
Date: 2024-12-13

Puzzle:
The Claw Machine has two buttons and each button moves the claw a certain amount in the X and Y direction. The cost
to push Button A is 3, the cost to push button B is 1. For the input, determine the number of times to push A and B
to get to the prize.

Part 1
Calculate the minimum cost to move to the prize location.

Part 2
The prize location is not correct and should have 1,000,000,000,000 to both the X and Y axes. Re-run the calculation
with the new offset and determine the cost to win the prizes.

Design Notes
This is primarily a math problem. Not sure if people were doing trial and error, but this solution was straightforward
with the correct math. Where we have an example:

    Button A: X+94, Y+34
    Button B: X+22, Y+67
    Prize: X=8400, Y=5400

We convert this to:

    Ax94 + Bx22 = 8,400



'''

class Machine:
    def __init__(self,
                 button_a_movement: (int, int),
                 button_b_movement: (int, int),
                 prize_location: (int, int)):
        self.button_a_movement = button_a_movement
        self.button_b_movement = button_b_movement
        self.prize_location = prize_location
        self.a_cost = 3
        self.b_cost = 1

    def calc_optimal_cost(self, offset=0):
        (ax, ay) = self.button_a_movement
        (bx, by) = self.button_b_movement
        (px, py) = self.prize_location

        (px, py) = (px+offset, py+offset)

        my = ay
        mx = ax

        ax *= my
        bx *= my
        px *= my

        ay *= mx
        by *= mx
        py *= mx

        b = (py-px) / (by-bx)
        a = (px - bx*b) / ax
        if abs(a - int(a)) < 0.001 and abs(b - int(b)) < 0.001:
            return a*self.a_cost + b*self.b_cost
        else:
            return None

    def __str__(self):
        return f'A: {self.button_a_movement}, B: {self.button_b_movement}. Prize: {self.prize_location}'

class ClawContraption:
    def __init__(self, filename: str):
        self.machines = []
        self._load_data(filename)

    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            while True:
                button_a = f.readline().strip()
                button_b = f.readline().strip()
                prize = f.readline().strip()
                _ = f.readline()
                if not button_a:
                    break

                a_dx_dy = [int(x.strip()[2:]) for x in button_a.split(':')[1].strip().split(',')]
                b_dx_dy = [int(x.strip()[2:]) for x in button_b.split(':')[1].strip().split(',')]
                prize_location = [int(x.strip()[2:]) for x in prize.split(':')[1].strip().split(',')]
                self.machines.append(Machine(button_a_movement=a_dx_dy,
                                             button_b_movement=b_dx_dy,
                                             prize_location=prize_location))

    def get_answer_1(self) -> int:
        total_cost = 0
        for machine in self.machines:
            cost = machine.calc_optimal_cost()
            if cost:
                total_cost += cost
        return total_cost

    def get_answer_2(self) -> int:
        total_cost = 0
        for machine in self.machines:
            cost = machine.calc_optimal_cost(offset=10000000000000)
            if cost:
                total_cost += cost
        return total_cost



test_solution = ClawContraption('test.txt')
assert test_solution.get_answer_1() == 480
#assert test_solution.get_answer_2() == 0 # update

solution_1 = ClawContraption('data.txt')
answer_1 = solution_1.get_answer_1()
print(f'Task 1 Answer: {answer_1}')

solution_2 = ClawContraption('data.txt')
answer_2 = solution_2.get_answer_2()
print(f'Task 2 Answer: {answer_2}')