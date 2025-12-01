import math
from pathlib import Path

TEST_INPUT_01 = "L68 L30 R48 L5 R60 L55 L1 L99 R14 L82"
TEST_INPUT_02 = "L68 L30 R48 L5 R60 L55 L1 L99 R14 L82 R1000"
# CMD, FR (Full Rotations), NP (New Position)
# L68, 0, 82


def parse_input(input: str | Path, remove_no_ops: bool = False):
    if isinstance(input, str):
        rotations = input.split(" ")
    else:
        rotations = input.read_text().split("\n")

    rotations = [r.strip() for r in rotations]

    if not remove_no_ops:
        return [r for r in rotations if r]
    else:
        return [r for r in rotations if r and int(r[1:]) != 0]


def first(input: str | Path):
    rotations = parse_input(input)

    count = 0
    current = 50
    for rotation in rotations:
        if rotation.startswith("L"):
            current -= int(rotation[1:])
        else:
            current += int(rotation[1:])

        current %= 100
        # print(f"The dial is rotated {rotation} to point at {current}")
        if current == 0:
            count += 1

    return count


def second(input: str | Path):
    rotations = parse_input(input, remove_no_ops=False)

    count = 0
    current = 50
    for rotation in rotations:
        degrees = int(rotation[1:])

        # convert everything to right rotations
        if rotation.startswith("L"):
            new_pos = (100 - current) % 100 + degrees
            zero_hits = math.floor(new_pos / 100)
            count += zero_hits
            current = (current - degrees) % 100
        else:
            new_pos = current + degrees
            zero_hits = math.floor(new_pos / 100)
            count += zero_hits
            current = new_pos % 100

        print(
            f"The dial is rotated {rotation} to point at {current}; during this rotation, it passed 0 {zero_hits} times"
        )

    return count


if __name__ == "__main__":
    ### first challenge
    print("Starting FIRST challenge")
    test_result = first(TEST_INPUT_01)
    print(f"Result of Test: {test_result}")
    assert test_result == 3
    prod_result = first(Path("./days/01/input/first"))
    print(f"Result of Prod: {prod_result}")

    ### second challenge
    print("Starting SECOND challenge")
    test_result = second(TEST_INPUT_02)
    print(f"Result of Test: {test_result}")
    assert test_result == 16

    prod_result = second(Path("./days/01/input/first"))
    print(f"Result of Prod: {prod_result}")  # solution is 6695
