from pathlib import Path
from enum import Enum


class Field(Enum):
    EMPTY = 1
    ROLL = 2


TEST_FIRST = """
..@@.@@@@.
@@@.@.@.@@
@@@@@.@.@@
@.@@@@..@.
@@.@@@@.@@
.@@@@@@@.@
.@.@.@.@@@
@.@@@.@@@@
.@@@@@@@@.
@.@.@@@.@.
"""


def parse_input(input: str | Path) -> list[list[Field]]:
    if isinstance(input, Path):
        input = input.read_text()

    rows: list[list[Field]] = []
    for line in input.splitlines():
        if not line.strip():
            continue
        row = []
        for i in list(line):
            if (i) == ".":
                row.append(Field.EMPTY)
            else:
                row.append(Field.ROLL)

        rows.append(row)

    return rows


def first(input: str | Path) -> int:
    # col x row
    field = parse_input(input)

    y_len = len(field)
    x_len = len(field[0])

    total = 0
    for x in range(x_len):
        for y in range(y_len):
            if field[y][x] == Field.EMPTY:
                continue

            rolls = 0
            for offset_x in range(-1, 2):
                for offset_y in range(-1, 2):
                    if x + offset_x < 0 or x + offset_x >= x_len:
                        continue
                    if y + offset_y < 0 or y + offset_y >= y_len:
                        continue

                    if field[y + offset_y][x + offset_x] == Field.ROLL:
                        rolls += 1

            if rolls - 1 < 4:
                # print(f"Found one: {x=}, {y=}")
                total += 1

    return total


def second(input: str | Path) -> int:
    field = parse_input(input)
    y_len = len(field)
    x_len = len(field[0])

    removed = 0

    y = 0
    while y < y_len:
        x = 0
        while x < x_len:
            if field[y][x] == Field.EMPTY:
                x += 1
                continue

            rolls = 0
            for offset_x in range(-1, 2):
                for offset_y in range(-1, 2):
                    if x + offset_x < 0 or x + offset_x >= x_len:
                        continue
                    if y + offset_y < 0 or y + offset_y >= y_len:
                        continue

                    if field[y + offset_y][x + offset_x] == Field.ROLL:
                        rolls += 1

            if rolls - 1 < 4:
                removed += 1
                field[y][x] = Field.EMPTY
                x = max(x - 1, 0)
                y = max(y - 1, 0)
            else:
                x += 1
        y += 1

    return removed


# first
test_res = first(TEST_FIRST)
print(f"First (Test): {test_res}")
assert test_res == 13

prod_res = first(Path("./days/04/input/first"))
print(f"First (Prod): {prod_res}")

# second
test_res = second(TEST_FIRST)
print(f"Second (Test): {test_res}")
assert test_res == 43

prod_res = second(Path("./days/04/input/first"))
print(f"Second (Prod): {prod_res}")
