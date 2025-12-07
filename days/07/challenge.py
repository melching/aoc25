from pathlib import Path
from enum import Enum
from collections import defaultdict


class Kind(Enum):
    EMPTY = 1
    START = 2
    SPLITTER = 3
    BEAM = 4

    @classmethod
    def from_str(cls, s: str) -> "Kind":
        match s:
            case ".":
                return cls.EMPTY
            case "S":
                return cls.START
            case "^":
                return cls.SPLITTER
            case "|":
                return cls.BEAM
            case _:
                raise ValueError("Unknown type")


TEST_FIRST = """
.......S.......
...............
.......^.......
...............
......^.^......
...............
.....^.^.^.....
...............
....^.^...^....
...............
...^.^...^.^...
...............
..^...^.....^..
...............
.^.^.^.^.^...^.
...............
"""


def parse_input(input: str | Path) -> list[list[Kind]]:
    if isinstance(input, Path):
        input = input.read_text()

    field: list[list[Kind]] = []

    for line in [line for line in input.splitlines() if line]:
        row = [Kind.from_str(char) for char in line]
        field.append(row)

    return field


def first(input: str | Path) -> int:
    # col x row
    field = parse_input(input)

    split_count = 0
    for y, row in enumerate(field[:-1]):
        for x, k in enumerate(row):
            if k in [Kind.START, Kind.BEAM]:
                if field[y + 1][x] == Kind.EMPTY:
                    field[y + 1][x] = Kind.BEAM
                elif field[y + 1][x] == Kind.SPLITTER:
                    split_count += 1
                    for side_x in [x - 1, x + 1]:
                        if side_x < 0 or side_x >= len(row):
                            continue
                        if field[y + 1][side_x] == Kind.EMPTY:
                            field[y + 1][side_x] = Kind.BEAM

    return split_count


def second(input: str | Path) -> int:
    # col x row
    field = parse_input(input)

    timelines_on_pos: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for y, row in enumerate(field[:-1]):
        for x, k in enumerate(row):
            if k in [Kind.START, Kind.BEAM]:
                current_timelines = 1 if k == Kind.START else timelines_on_pos[y][x]

                if field[y + 1][x] in [Kind.EMPTY, Kind.BEAM]:
                    field[y + 1][x] = Kind.BEAM
                    timelines_on_pos[y + 1][x] += current_timelines

                elif field[y + 1][x] == Kind.SPLITTER:
                    for side_x in [x - 1, x + 1]:
                        if field[y + 1][side_x] in [Kind.EMPTY, Kind.BEAM]:
                            field[y + 1][side_x] = Kind.BEAM
                            timelines_on_pos[y + 1][side_x] += current_timelines

    return sum(timelines_on_pos[len(field) - 1].values())


# first
test_res = first(TEST_FIRST)
print(f"First (Test): {test_res}")
assert test_res == 21

prod_res = first(Path("./days/07/input/first"))
print(f"First (Prod): {prod_res}")

# second
test_res = second(TEST_FIRST)
print(f"Second (Test): {test_res}")
assert test_res == 40

prod_res = second(Path("./days/07/input/first"))
print(f"Second (Prod): {prod_res}")
