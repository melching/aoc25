from pathlib import Path
from time import perf_counter
from copy import deepcopy

TEST_FIRST = """
7,1
11,1
11,7
9,7
9,5
2,5
2,3
7,3
"""


def parse_input(input: str | Path) -> list[tuple[int, int]]:
    if isinstance(input, Path):
        input = input.read_text()

    tiles: list[tuple[int, int]] = []
    for row in input.splitlines():
        if not row:
            continue

        coords = row.split(",")
        tiles.append((int(coords[1]), int(coords[0])))

    return tiles


def first(input: str | Path) -> int:
    # first one should be solvable by just computing all areas
    tiles = parse_input(input)

    areas: list[tuple[int, tuple[int, int], tuple[int, int]]] = []
    for i, t1 in enumerate(tiles):
        for j, t2 in enumerate(tiles):
            if i > j:
                continue
            if i == j:
                continue
            x_diff = abs(t1[1] - t2[1])
            y_diff = abs(t1[0] - t2[0])
            area = (x_diff + 1) * (y_diff + 1)
            areas.append((area, t1, t2))

    max_area = max(areas, key=lambda x: x[0])
    return max_area[0]


def second(input: str | Path) -> int:
    # honestly, I struggled with this more than I should have.
    # In the end I made the assumption, that there are no edges next to each other
    # (that could also possibly lead to holes in the polygon).
    # For this data these hold, for other data these dont. At this point one might just use shapely or numpy
    # as it will be too tedious in `raw` python.

    red_tiles = parse_input(input)

    circled_red_tiles = deepcopy(red_tiles)
    circled_red_tiles.append(red_tiles[0])  # close the loop

    edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for i in range(len(circled_red_tiles) - 1):
        t1 = circled_red_tiles[i]
        t2 = circled_red_tiles[(i + 1)]
        edges.append((t1, t2))

    def rectangle_intersects_edges(
        min_y: int, min_x: int, max_y: int, max_x: int
    ) -> bool:
        for edge_start, edge_end in edges:
            edge_min_y = min(edge_start[0], edge_end[0])
            edge_max_y = max(edge_start[0], edge_end[0])
            edge_min_x = min(edge_start[1], edge_end[1])
            edge_max_x = max(edge_start[1], edge_end[1])

            # basic AABB check
            if (
                min_x < edge_max_x
                and max_x > edge_min_x
                and min_y < edge_max_y
                and max_y > edge_min_y
            ):
                return True

        return False

    areas: list[tuple[int, tuple[int, int], tuple[int, int]]] = []
    for i, t1 in enumerate(red_tiles):
        for j, t2 in enumerate(red_tiles):
            if i > j:
                continue
            if i == j:
                continue

            min_y = min(t1[0], t2[0])
            max_y = max(t1[0], t2[0])
            min_x = min(t1[1], t2[1])
            max_x = max(t1[1], t2[1])

            if rectangle_intersects_edges(min_y, min_x, max_y, max_x):
                continue

            x_diff = abs(t1[1] - t2[1])
            y_diff = abs(t1[0] - t2[0])
            area = (x_diff + 1) * (y_diff + 1)
            areas.append((area, t1, t2))

    max_area = max(areas, key=lambda x: x[0])
    return max_area[0]


# first
test_res = first(TEST_FIRST)
print(f"First (Test): {test_res}")
assert test_res == 50

t0 = perf_counter()
prod_res = first(Path("./days/09/input/first"))
print(f"First (Prod): {prod_res}. Took {perf_counter() - t0} seconds")

# second
test_res = second(TEST_FIRST)
print(f"Second (Test): {test_res}")
assert test_res == 24

t0 = perf_counter()
prod_res = second(Path("./days/09/input/first"))
print(f"Second (Prod): {prod_res}. Took {perf_counter() - t0} seconds")
