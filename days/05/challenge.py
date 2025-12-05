from pathlib import Path


TEST_FIRST = """
3-5
10-14
16-20
12-18

1
5
8
11
17
32
"""


# return two lists
# first list contains start and stop tuples of fresh id ranges
# second contains ids of ingredients to check
def parse_input(input: str | Path) -> tuple[list[tuple[int, int]], list[int]]:
    if isinstance(input, Path):
        input = input.read_text()

    separated = input.split("\n\n")

    # fresh ids
    ranges: list[tuple[int, int]] = []
    for range in separated[0].splitlines():
        if not range:
            continue
        split = range.split("-")
        start, stop = int(split[0]), int(split[1])
        ranges.append((start, stop))

    # ids to check
    ids_to_check = [int(i) for i in separated[1].splitlines() if i]

    return ranges, ids_to_check


def first(input: str | Path) -> int:
    # col x row
    ranges, ids_to_check = parse_input(input)

    def is_in_ranges(v: int) -> bool:
        for start, end in ranges:
            if v in range(start, end + 1):
                return True
        return False

    return sum([is_in_ranges(v) for v in ids_to_check])


def second(input: str | Path) -> int:
    # col x row
    ranges, _ = parse_input(input)

    starts: list[int] = []
    ends: list[int] = []
    for start, end in ranges:
        starts.append(start)
        ends.append(end)

    sorted_starts = sorted(starts)
    sorted_ends = sorted(ends)

    total = 0
    while len(sorted_starts) > 1:
        if sorted_ends[0] >= sorted_starts[1]:
            sorted_starts.pop(1)
            sorted_ends.pop(0)
        else:
            range_len = len(range(sorted_starts[0], sorted_ends[0] + 1))
            total += range_len
            sorted_starts.pop(0)
            sorted_ends.pop(0)

    total += len(range(sorted_starts[0], sorted_ends[0] + 1))

    return total


# first
test_res = first(TEST_FIRST)
print(f"First (Test): {test_res}")
assert test_res == 3

prod_res = first(Path("./days/05/input/first"))
print(f"First (Prod): {prod_res}")

# second
test_res = second(TEST_FIRST)
print(f"Second (Test): {test_res}")
assert test_res == 14

prod_res = second(Path("./days/05/input/first"))
print(f"Second (Prod): {prod_res}")
