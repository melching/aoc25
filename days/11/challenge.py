from time import perf_counter
import re
from pathlib import Path
from collections import defaultdict
from copy import copy, deepcopy

TEST_FIRST = """
aaa: you hhh
you: bbb ccc
bbb: ddd eee
ccc: ddd eee fff
ddd: ggg
eee: out
fff: out
ggg: out
hhh: ccc fff iii
iii: out
"""

TEST_SECOND = """
svr: aaa bbb
aaa: fft
fft: ccc
bbb: tty
tty: ccc
ccc: ddd eee
ddd: hub
hub: fff
eee: dac
dac: fff
fff: ggg hhh
ggg: out
hhh: out
"""

OUT_KEY = "out"


def parse_input(input: str | Path) -> dict[str, set[str]]:
    if isinstance(input, Path):
        input = input.read_text()

    mapping: dict[str, set[str]] = defaultdict(set)
    # mapping is input -> outputs
    for line in input.splitlines():
        if not line:
            continue
        split = line.split(" ")

        # first one needs to be pruned (due to `:`)
        start = split[0][:-1]

        # ends are just normal
        ends = set(split[1:])
        mapping[start] = ends

    for k, outs in mapping.items():
        for v in outs:
            if v == OUT_KEY:
                continue
            assert v in mapping, f"{v!r} is not in mapping {mapping.keys()}"
            assert not k == v

    return mapping


def first(input: str | Path) -> int:
    mapping = parse_input(input)
    START_KEY = "you"

    # I think there is no need (yet?) to build a graph or something like this.
    # For now it should be sufficient just to track the counts per state.
    # Here we start with `you` = 1.

    # Also I assume there are no loops? But I dont think this will hold.

    current = {k: 0 for k in mapping}
    current[OUT_KEY] = 0
    current[START_KEY] = 1

    # need to decide on exit condition
    while current["out"] != sum(current.values()):
        # update the set
        for k, v in current.items():
            if v == 0:
                continue
            if k == OUT_KEY:
                continue
            next_states = mapping[k]

            for next in next_states:
                current[next] += v
            current[k] = 0

    # print(current)
    return current[OUT_KEY]


def second(input: str | Path) -> int:
    mapping = parse_input(input)
    START_KEY = "svr"
    RELEVANT_KEYS = ["dac", "fft"]

    # ah yeah, the second tasks needs me to track the path.
    # I still dont want to make a smart graph solution, lets see how I can track it.
    # Maybe just a second and a third dict? Or just track the special path using
    # a suffix like `aaa.ftt` or `aaa.dac`. In the end I just sum the two possible `out`s.

    current: dict[str, int] = defaultdict(int)
    current[START_KEY] = 1

    def all_on_out() -> bool:
        return sum(current.values()) == sum(
            v for k, v in current.items() if k.startswith(OUT_KEY)
        )

    while not all_on_out():
        next_current_update = defaultdict(int)
        for k, v in current.items():
            if v == 0:
                continue
            if k.startswith(OUT_KEY):
                continue

            split = k.split(".")
            first_key = split[0]
            next_mapping_states = mapping[first_key]

            for next_mapping_state in next_mapping_states:
                if len(split) > 1:
                    next_current_state = ".".join([next_mapping_state] + split[1:])
                else:
                    next_current_state = next_mapping_state

                if first_key in RELEVANT_KEYS:
                    next_current_state += f".{first_key}"

                next_current_update[next_current_state] += v
            next_current_update[k] -= v

        for k, v in next_current_update.items():
            current[k] += v

    # count the states that are interesting
    total = 0
    for k, v in current.items():
        if all(rk in k for rk in RELEVANT_KEYS):
            total += v

    return total


# first
test_res = first(TEST_FIRST)
print(f"First (Test): {test_res}")
assert test_res == 5

t0 = perf_counter()
prod_res = first(Path("./days/11/input/first"))
print(f"First (Prod): {prod_res}. Took {perf_counter() - t0} seconds")

# second
test_res = second(TEST_SECOND)
print(f"Second (Test): {test_res}")
assert test_res == 2

t0 = perf_counter()
prod_res = second(Path("./days/11/input/first"))
print(f"Second (Prod): {prod_res}. Took {perf_counter() - t0} seconds")
