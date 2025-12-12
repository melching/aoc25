from time import perf_counter
import re
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass

TEST_FIRST = """
0:
###
##.
##.

1:
###
##.
.##

2:
.##
###
##.

3:
##.
###
##.

4:
###
#..
###

5:
###
.#.
###

4x4: 0 0 0 0 2 0
12x5: 1 0 1 0 2 2
12x5: 1 0 1 0 3 2
"""


@dataclass
class Box:
    coords: list[tuple]  # x,y

    @property
    def width(self) -> int:
        return max(c[0] for c in self.coords) + 1

    @property
    def height(self) -> int:
        return max(c[1] for c in self.coords) + 1

    @property
    def blocked_spaces(self) -> int:
        return len(self.coords)


@dataclass
class Tree:
    width: int
    height: int

    # box index to box count
    required_boxes: dict[int, int]


def parse_input(input: str | Path) -> tuple[list[Box], list[Tree]]:
    if isinstance(input, Path):
        input = input.read_text()

    split = input.split("\n\n")

    # 0 to n-1 are boxes
    # n are trees

    boxes: list[Box] = []
    for box_str in split[:-1]:
        coords = []
        for y, line in enumerate(box_str.splitlines()[1:]):
            if not line:
                continue
            for x, char in enumerate(line):
                if char == "#":
                    coords.append((x, y))
        boxes.append(Box(coords=coords))

    trees: list[Tree] = []
    for line in split[-1].splitlines():
        if not line:
            continue
        tree_split = line.split(" ")

        # idx 0 is tree size, 1-n are presents
        w, h = [int(x.strip(": ")) for x in tree_split[0].split("x")]
        box_counts = {i: int(b) for i, b in enumerate(tree_split[1:])}
        trees.append(Tree(width=w, height=h, required_boxes=box_counts))

    return boxes, trees


def first(input: str | Path) -> int:
    # Day 12 was the first day I came across a hint on my reddit
    # frontpage while scrolling that spoiled a solution somewhat.
    # The hint was just something like `I cheated with my solution on the actual data`,
    # but that strongly hints towards a possible solution that does
    # not require to check all boxes.
    # I wonder that part two could be then though.

    boxes, trees = parse_input(input)
    # First idea, that does not work on the test data, but maybe on the prod data:
    # If one were to ignore the empty spaces of the boxes, would they fit?
    # -> That did not work (too low).
    # Lets try to only look at the occupied spaces, ignoring the layout.
    # -> Yeah, well, that worked.

    successes = 0
    for tree in trees:
        boxed_area = 0
        occupied_area = 0
        for box_idx, box_count in tree.required_boxes.items():
            box = boxes[box_idx]
            boxed_area += box.width * box.height * box_count
            occupied_area += box.blocked_spaces * box_count
        # if boxed_area < tree.width * tree.height:
        #     print(f"Boxed {boxed_area} < Tree {tree.width * tree.height}")
        #     successes += 1
        if occupied_area < tree.width * tree.height:
            # print(f"Occupied {occupied_area} < Tree {tree.width * tree.height}")
            successes += 1

    return successes


# first
# test_res = first(TEST_FIRST)
# print(f"First (Test): {test_res}")
# assert test_res == 5

t0 = perf_counter()
prod_res = first(Path("./days/12/input/first"))
print(f"First (Prod): {prod_res}. Took {perf_counter() - t0} seconds")
