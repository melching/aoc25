from pathlib import Path
from enum import Enum
from collections import defaultdict
import math
import re


class Operation(Enum):
    ADDITION = 1
    MUTLIPLICATION = 2

    @classmethod
    def from_str(cls, s: str) -> "Operation":
        if s == "+":
            return cls.ADDITION
        if s == "*":
            return cls.MUTLIPLICATION
        raise ValueError


def execute(numbers: list[int], op: Operation) -> int:
    if op == Operation.ADDITION:
        return sum(numbers)
    else:
        return math.prod(numbers)


TEST_FIRST = """
123 328  51 64 
 45 64  387 23 
  6 98  215 314
*   +   *   +  
"""


# return a list with tuples
# the tuples contain the list of the numbers and a single operator
def parse_input(input: str | Path) -> list[tuple[list[int], Operation]]:
    if isinstance(input, Path):
        input = input.read_text()

    cols: dict[int, list[int]] = defaultdict(list)

    lines = [line for line in input.splitlines() if line]

    # make ops first
    ops = [Operation.from_str(o) for o in lines[-1].split(" ") if o]

    for line in lines[:-1]:
        numbers = [int(n) for n in line.split(" ") if n]
        for i, n in enumerate(numbers):
            cols[i].append(n)

    return list(zip(cols.values(), ops))


def first(input: str | Path) -> int:
    # col x row
    cols_and_ops = parse_input(input)

    return sum([execute(col, op) for col, op in cols_and_ops])


# instead of adjusting the inital parsing method i just wrote a new one in this method
def second(input: str | Path) -> int:
    if isinstance(input, Path):
        input = input.read_text()

    lines = [line for line in input.splitlines() if line]

    # the last line gives me an easy way to get the col widths
    col_widths: list[int] = []
    ops: list[Operation] = []
    matches = re.findall(r"[\+\*]{1} +", lines[-1])
    if matches is None:
        raise ValueError("Unexpected Input")

    for match in matches:
        if not isinstance(match, str):
            raise ValueError("Unexpected Input")

        if match.startswith("*"):
            ops.append(Operation.MUTLIPLICATION)
        else:
            ops.append(Operation.ADDITION)

        col_widths.append(len(match) - 1)  # -1 due to space between cols

    # in the last one we substracted too much, so we add one again
    col_widths[-1] += 1

    # one dict for col, one dict for pos in col, list for numbers of pos in col
    numbers: dict[int, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))
    for line in lines[:-1]:
        cur_idx = 0
        for i, col_width in enumerate(col_widths):
            for c in range(col_width):
                numbers[i][c].append(line[cur_idx + c + i])
            cur_idx += col_width

    total = 0
    assert len(numbers) == len(ops)
    for col, op in zip(numbers.values(), ops):
        new_numbers = [int("".join(cv)) for cv in col.values()]
        total += execute(new_numbers, op)

    return total


# first
test_res = first(TEST_FIRST)
print(f"First (Test): {test_res}")
assert test_res == 4277556

prod_res = first(Path("./days/06/input/first"))
print(f"First (Prod): {prod_res}")

# second
test_res = second(TEST_FIRST)
print(f"Second (Test): {test_res}")
assert test_res == 3263827

prod_res = second(Path("./days/06/input/first"))
print(f"Second (Prod): {prod_res}")
