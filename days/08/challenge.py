from pathlib import Path
from time import perf_counter
from dataclasses import dataclass
import math

# This would be so much easier if I only allowed myself to use numpy or scipy.
# Also it helps to read the task clearly in order not to wonder for 10 minutes
# where you went wrong as you implemented something different than wanted.


@dataclass
class Box:
    x: int
    y: int
    z: int

    @classmethod
    def from_list(cls, v: list[int]) -> "Box":
        if not len(v) == 3:
            raise ValueError
        return cls(x=v[0], y=v[1], z=v[2])

    def to_list(self) -> list[int]:
        return [self.x, self.y, self.z]

    @classmethod
    def distance(cls, first: "Box", second: "Box") -> float:
        # could implement distance myself, but math.dist already does euclidean
        # I think this is fair, even though I dont want to use too many external packages
        return math.dist(first.to_list(), second.to_list())


TEST_FIRST = """
162,817,812
57,618,57
906,360,560
592,479,940
352,342,300
466,668,158
542,29,236
431,825,988
739,650,466
52,470,668
216,146,977
819,987,18
117,168,530
805,96,715
346,949,466
970,615,88
941,993,340
862,61,35
984,92,344
425,690,689
"""


def parse_input(input: str | Path) -> list[Box]:
    if isinstance(input, Path):
        input = input.read_text()

    boxes = []
    for row in input.splitlines():
        if not row:
            continue

        coords = row.split(",")
        boxes.append(Box(x=int(coords[0]), y=int(coords[1]), z=int(coords[2])))

    return boxes


def first(input: str | Path, connections: int) -> int:
    # col x row
    boxes = parse_input(input)

    # lets try to use references here to make my life easier later on (with less looped checks)
    circuits: dict[int, list[int]] = {i: [i] for i in range(len(boxes))}

    # calc the distance matrix and put them in a list for sorting
    # this is a list of tuples with each tuple containing a tuple with the indeces and the distance
    distances: list[tuple[float, tuple[int, int]]] = []
    for i, b1 in enumerate(boxes):
        for j, b2 in enumerate(boxes):
            if i == j:
                continue  # no need to compute
            elif i > j:
                continue  # already computed previously
            else:
                distances.append((Box.distance(b1, b2), (i, j)))
    distances.sort(key=lambda x: x[0])

    for _ in range(connections):
        # get smallest distance
        _, (i, j) = distances[0]
        distances.pop(0)

        # check if they are in the same circuit
        if circuits[i] == circuits[j]:
            continue

        # join circuits
        circuits[i] += circuits[j]
        for idx in circuits[i]:
            circuits[idx] = circuits[i]

    # now deduplicate circuits
    unique_circuits: list[set[int]] = []
    for v in circuits.values():
        set_v = set(v)
        if set_v not in unique_circuits:
            unique_circuits.append(set_v)

    sorted_circuit_sizes = sorted([len(v) for v in unique_circuits], reverse=True)
    print(f"Sorted circuit sizes: {sorted_circuit_sizes}")

    return sorted_circuit_sizes[0] * sorted_circuit_sizes[1] * sorted_circuit_sizes[2]


def second(input: str | Path) -> float:
    # col x row
    boxes = parse_input(input)

    # lets try to use references here to make my life easier later on (with less looped checks)
    circuits: dict[int, list[int]] = {i: [i] for i in range(len(boxes))}

    # calc the distance matrix and put them in a list for sorting
    # this is a list of tuples with each tuple containing a tuple with the indeces and the distance
    distances: list[tuple[float, tuple[int, int]]] = []
    for i, b1 in enumerate(boxes):
        for j, b2 in enumerate(boxes):
            if i == j:
                continue  # no need to compute
            elif i > j:
                continue  # already computed previously
            else:
                distances.append((Box.distance(b1, b2), (i, j)))
    distances.sort(key=lambda x: x[0])

    while True:
        # get smallest distance
        _, (i, j) = distances[0]
        distances.pop(0)

        # check if they are in the same circuit
        if circuits[i] == circuits[j]:
            continue

        # join circuits
        circuits[i] += circuits[j]
        for idx in circuits[i]:
            circuits[idx] = circuits[i]

        if len(circuits[i]) == len(boxes):
            return boxes[i].x * boxes[j].x


# first
test_res = first(TEST_FIRST, 10)
print(f"First (Test): {test_res}")
assert test_res == 40

t0 = perf_counter()
prod_res = first(Path("./days/08/input/first"), 1000)
print(f"First (Prod): {prod_res}. Took {perf_counter() - t0} seconds")

# second
test_res = second(TEST_FIRST)
print(f"Second (Test): {test_res}")
assert test_res == 25272

t0 = perf_counter()
prod_res = second(Path("./days/08/input/first"))
print(f"Second (Prod): {prod_res}. Took {perf_counter() - t0} seconds")
