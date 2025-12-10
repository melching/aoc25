from time import perf_counter
from dataclasses import dataclass
import re
from pathlib import Path
from functools import lru_cache
from collections import defaultdict
from random import shuffle
from scipy.optimize import linprog
import numpy as np

TEST_FIRST = """
[.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}
[...#.] (0,2,3,4) (2,3) (0,4) (0,1,2) (1,2,3,4) {7,5,12,7,2}
[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}
"""


@dataclass
class Button:
    lights: list[int]

    @classmethod
    def from_str(cls, v: str) -> "Button":
        indeces = v.strip(" ()").split(",")
        return Button(lights=[int(i) for i in indeces])


@dataclass
class Configuration:
    lights_target: list[bool]
    buttons: list[Button]
    target_joltage: list[int]

    @classmethod
    def from_str(cls, line: str) -> "Configuration":
        split = line.split(" ")

        # first one is always target lights
        target_lights: list[bool] = [char == "#" for char in split[0].strip("[]")]

        # middle ones are the buttons
        buttons: list[Button] = []
        for button_config in split[1:-1]:
            buttons.append(
                Button(lights=[int(b) for b in button_config.strip("()").split(",")])
            )

        # last one are joltages
        joltage: list[int] = [int(j) for j in split[-1].strip("{}").split(",")]

        return Configuration(
            lights_target=target_lights,
            buttons=buttons,
            target_joltage=joltage,
        )


def parse_input(input: str | Path) -> list[Configuration]:
    if isinstance(input, Path):
        input = input.read_text()

    # for some reason I felt like using dataclasses today,
    # so I implemented `from_str` in them
    return [Configuration.from_str(line) for line in input.splitlines() if line]


def first(input: str | Path) -> int:
    # each machine configuration has 2^n possible combinations, you either press a button or not.
    # You never press a button more than once, as all the other options are just generating
    # the same results as the previous ones.

    # lets see how we can improve the performance nicely, as on quick inspection I saw a problem with
    # like 12 buttons, resulting already in 2^12 = 4.096 combinations (which is not much for modern
    # hardware, but lets see whats comming after).

    # again, this would be sooo much quicker using numpy or if I just used better data formats from the start

    configurations = parse_input(input)

    button_presses: list[int] = []
    for config in configurations:
        # print(f"Checking config {config!r}")
        # lets compute all button combinations once
        # here we want a list of bool where each position in the list corresponds to a button.

        # I could not think of a way that is nicer than just converting to binary
        num_buttons = len(config.buttons)
        all_possible_combinations: list[str] = []
        for i in range(2**num_buttons):
            all_possible_combinations.append(format(i, "b").zfill(num_buttons))

        # now sort by count of ones, to make sure we test the lowest counts first
        all_possible_combinations.sort(key=lambda x: x.count("1"))

        # and now we can finally check, if the combination solves the task.
        for comb in all_possible_combinations:
            one_indeces = [m.start() for m in re.finditer("1", comb)]

            current = [False] * len(config.lights_target)
            # apply all buttons
            for b_idx in one_indeces:
                # apply button
                for light_idx in config.buttons[b_idx].lights:
                    current[light_idx] = not current[light_idx]

            if current == config.lights_target:
                # print(f"Found solutions using {len(one_indeces)} button presses")
                button_presses.append(len(one_indeces))
                break
        else:
            raise RuntimeError("Found no solution?!")

    return sum(button_presses)


def second_solve_scipy(input: str | Path) -> int:
    # I caved and just used scipy. It also took way too long to implement a custom solver.
    # This is a classic linear equation system after all; maybe brute forcing it for the fun of it was
    # always a bad idea.

    # c.f. https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html

    configurations = parse_input(input)
    button_presses: list[int] = []
    for config in configurations:
        A = np.zeros((len(config.target_joltage), len(config.buttons)), dtype=int)
        for b_idx, button in enumerate(config.buttons):
            for l_idx in button.lights:
                A[l_idx, b_idx] = 1

        b = np.array(config.target_joltage, dtype=int)

        # solve using scipy
        res = linprog(c=np.ones(len(config.buttons)), A_eq=A, b_eq=b, integrality=1)

        if not res.success:
            raise RuntimeError("No solution found by scipy?!")

        button_presses.append(res.fun)

    return int(sum(button_presses))


def second_solve_for_x(input: str | Path) -> int:
    # maybe you should just try to solve by reducing the space even harder?
    # The idea: get all combinations that solve for each light individually.
    # Then combine those combinations to get the final solution.
    # This should reduce the search space quite a bit.

    # The trick is to only consider buttons, that actually toggle the light we want to solve for.
    # As pressing buttons that do not affect the light is just wasted presses and does not need to be considered initially.

    # lets say you have three buttons that toggle light 0 and you need to press the light 0 three times
    # These are the combinations that work for light 0:
    # 3 * A + 0 * B + 0 * C
    # 2 * A + 1 * B + 0 * C
    # 2 * A + 0 * B + 1 * C
    # 1 * A + 2 * B + 0 * C
    # 1 * A + 1 * B + 1 * C
    # 1 * A + 0 * B + 2 * C
    # 0 * A + 3 * B + 0 * C
    # 0 * A + 2 * B + 1 * C
    # 0 * A + 1 * B + 2 * C
    # 0 * A + 0 * B + 3 * C
    # is this ((3+1)(3+2))/2 = 4*5 / 2 = 10 combinations?

    # for two lights this would be:
    # 2 * A + 0 * B + 0 * C
    # 1 * A + 1 * B + 0 * C
    # 1 * A + 0 * B + 1 * C
    # 0 * A + 2 * B + 0 * C
    # 0 * A + 1 * B + 1 * C
    # 0 * A + 0 * B + 2 * C
    # is this ((2+1)(2+2))/2 = 3*4/2 = 6 combinations?

    # Note: That I did not implement this. I did not want to spend more time on this day.

    raise NotImplementedError()


def second_dicts(input: str | Path) -> int:
    # now we have a completely different problem. The previous limit on button presses
    # is no longer valid here.
    # The only limit I can think of for now is to check how many times each button can be presses max
    # (as we still cannot substract) to limit the set of possibilities.
    # Of course, stopping early is always nice to reduce time.

    # I used itertools here, as it would be far to annoying otherwise. But still no fancy math and such!

    # I feel like I cannot get around building a nicely pruned tree here :/ .

    # New idea: only store the joltage->presses in a dict
    # might be faster and does not require custom data object

    configurations = parse_input(input)

    button_presses: list[int] = []
    for config in configurations:
        print("Starting new config")

        # lets check for each button, how many times it could be pressed individually, before breaking the limit
        max_presses_per_isolated_button: list[tuple[int, int]] = [
            (b_idx, min([config.target_joltage[l_idx] for l_idx in btn.lights]))
            for b_idx, btn in enumerate(config.buttons)
        ]
        # sort by max presses, to try smaller ones first
        max_presses_per_isolated_button.sort(key=lambda x: x[1])

        # maybe sort the most complex buttons first? (most lights)
        max_presses_per_isolated_button.sort(
            key=lambda x: len(config.buttons[x[0]].lights), reverse=True
        )

        # or maybe use the largest buttons first that share lights with each other?
        # maybe we can reduce the search space faster that way.
        # or just shuffle randomly and hope for the best?
        shuffle(max_presses_per_isolated_button)

        @lru_cache(maxsize=None)
        def add_joltages(j1: tuple[int, ...], j2: tuple[int, ...]) -> tuple[int, ...]:
            # maybe zip is slower than indexing? who knows
            # return tuple(v1 + v2 for v1, v2 in zip(j1, j2))
            return tuple(j1[i] + j2[i] for i in range(len(j1)))

        def compare(j1: tuple[int, ...], j2: tuple[int, ...]) -> int:
            """
            0 if we can just continue and have not reached the goal
            -1 if we violate the goal
            1 if we reached the goal
            """
            if j1 == j2:
                return 1

            if any(j1[i] > j2[i] for i in range(len(j1))):
                return -1

            return 0

        @lru_cache(maxsize=None)
        def exceeds_target(j1: tuple[int, ...], j2: tuple[int, ...]) -> bool:
            return any(j1[i] > j2[i] for i in range(len(j1)))

        @lru_cache(maxsize=None)
        def button_to_joltage(btn_idx: int, presses: int) -> tuple[int, ...]:
            joltage = [0] * len(config.target_joltage)
            for l_idx in config.buttons[btn_idx].lights:
                joltage[l_idx] = presses
            return tuple(joltage)

        target_joltage_tuple = tuple(config.target_joltage)
        joltage_to_presses: dict[tuple[int, ...], int] = {
            tuple([0] * len(config.target_joltage)): 0
        }

        ranges = [(k, range(1, v + 1)) for k, v in max_presses_per_isolated_button]

        for btn_idx, btn_range in ranges:
            t0 = perf_counter()
            print(f"Started range {btn_range} for button {btn_idx}")
            print(f"Currently known entries: {len(joltage_to_presses)}")

            new_entries: dict[tuple[int, ...], list[int]] = defaultdict(list)
            bad_entries = set()
            for btn_presses in btn_range:
                joltage = button_to_joltage(btn_idx, btn_presses)
                # i think its fair to assume that a single press never matches or exceeds the target
                new_entries[joltage].append(btn_presses)

                for known_joltage, known_presses in joltage_to_presses.items():
                    if known_joltage in bad_entries:
                        # if one of the paths does not work for x presses, it will also not work for x+1 presses
                        continue

                    new_joltage = add_joltages(joltage, known_joltage)
                    if exceeds_target(new_joltage, target_joltage_tuple):
                        bad_entries.add(known_joltage)
                        continue
                    else:
                        new_presses = btn_presses + known_presses
                        new_entries[new_joltage].append(new_presses)

            # clean up new entries and apply the better ones to main
            for nj, np in new_entries.items():
                min_presses = min(np)
                if nj not in joltage_to_presses or min_presses < joltage_to_presses[nj]:
                    joltage_to_presses[nj] = min_presses

                if target_joltage_tuple in joltage_to_presses:
                    print(
                        f"Found solution early! Solution has {joltage_to_presses[target_joltage_tuple]} presses"
                    )
                    break

            print(f"Finished range in {perf_counter() - t0} seconds")

        assert target_joltage_tuple in joltage_to_presses
        button_presses.append(joltage_to_presses[target_joltage_tuple])

    print(button_presses)
    return sum(button_presses)


def second_path(input: str | Path) -> int:
    # This tries to solve the problem by building a tree of possibilities.
    # We try to reduce all the possible cases by trying to prune impossible paths early.

    # was way too slow, left for posterity. comments in other functions might contain additional information.

    @dataclass
    class Node:
        button_index: int
        press_count: int
        joltage: list[int]

        follower: "Node | None"

        # def len(self) -> int:
        #     if not self.follower:
        #         return 1
        #     else:
        #         return 1 + self.follower.len()

        def printable(self) -> str:
            base = f"Idx (btn): {self.button_index}, count: {self.press_count}, joltage: {self.joltage}"
            if not self.follower:
                return base
            else:
                return f"{base}\n->\n{self.follower.printable()}"

    configurations = parse_input(input)

    button_presses: list[int] = []
    for config in configurations:
        print("Starting new config")

        # lets check for each button, how many times it could be pressed individually, before breaking the limit
        max_presses_per_isolated_button: list[tuple[int, int]] = [
            (b_idx, min([config.target_joltage[l_idx] for l_idx in btn.lights]))
            for b_idx, btn in enumerate(config.buttons)
        ]
        # sort by max presses, to try smaller ones first
        # max_presses_per_isolated_button.sort(key=lambda x: x[1])

        # maybe sort the most complex buttons first? (most lights)
        max_presses_per_isolated_button.sort(
            key=lambda x: len(config.buttons[x[0]].lights), reverse=True
        )

        def add_joltages(j1: list[int], j2: list[int]) -> list[int]:
            return [v1 + v2 for v1, v2 in zip(j1, j2)]

        def compare(j: list[int]) -> int:
            """
            0 if we can just continue and have not reached the goal
            -1 if we violate the goal
            1 if we reached the goal
            """
            if j == config.target_joltage:
                return 1

            if any(j[i] > config.target_joltage[i] for i in range(len(j))):
                return -1

            return 0

        paths: list[Node] = []
        shortest_known_path: int = 123**123

        ranges = [(k, range(1, v + 1)) for k, v in max_presses_per_isolated_button]

        for btn_idx, btn_range in ranges:
            print(f"Started range {btn_range} for button {btn_idx}")
            print(f"Currently known nodes: {len(paths)}")
            print(f"Currently known shortest path: {shortest_known_path}")

            new_paths: list[Node] = []
            bad_paths = set()

            for btn_presses in btn_range:
                joltage = [0] * len(config.target_joltage)
                for l_idx in config.buttons[btn_idx].lights:
                    joltage[l_idx] += btn_presses

                cmped = compare(joltage)
                if cmped == 1:
                    # print(f"Found solution of lenth {btn_presses} using no chain")
                    if btn_presses < shortest_known_path:
                        shortest_known_path = btn_presses
                    break
                else:
                    new_paths.append(
                        Node(
                            button_index=btn_idx,
                            press_count=btn_presses,
                            joltage=joltage,
                            follower=None,
                        )
                    )

                for p, path in enumerate(paths):
                    if p in bad_paths:
                        # if one of the paths does not work for x presses, it will also not work for x+1 presses
                        continue
                    added_joltage = add_joltages(joltage, path.joltage)
                    cmped = compare(added_joltage)
                    presses = btn_presses + path.press_count
                    if cmped < 0:
                        bad_paths.add(p)
                        continue
                    elif cmped == 1:
                        print(
                            f"Found solution of lenth {presses} for btn {btn_idx} with {btn_presses} presses and chain\n{path.printable()}"
                        )

                        # no need to add a node here, as the new nodes are all invalid if they depend on this
                        if presses < shortest_known_path:
                            shortest_known_path = presses
                        continue
                    else:
                        # removed, was too expensive
                        # check if we already now a node like this but with a shorter path
                        # if any(
                        #     added_joltage == config.target_joltage
                        #     and n.press_count <= presses
                        #     for n in paths
                        # ):
                        #     print("Found smaller path in chache, skipping")
                        #     continue
                        # if any(
                        #     added_joltage == config.target_joltage
                        #     and n.press_count > presses
                        #     for n in paths
                        # ):
                        #     print("Found smaller path in chache, should be replacing")

                        new_paths.append(
                            Node(
                                button_index=btn_idx,
                                press_count=presses,
                                joltage=added_joltage,
                                follower=path,
                            )
                        )
            paths += new_paths

        button_presses.append(shortest_known_path)

    print(button_presses)
    return sum(button_presses)


# first
test_res = first(TEST_FIRST)
print(f"First (Test): {test_res}")
assert test_res == 7

t0 = perf_counter()
prod_res = first(Path("./days/10/input/first"))
print(f"First (Prod): {prod_res}. Took {perf_counter() - t0} seconds")

# second
test_res = second_solve_scipy(TEST_FIRST)
print(f"Second (Test): {test_res}")
assert test_res == 33

t0 = perf_counter()
prod_res = second_solve_scipy(Path("./days/10/input/first"))
print(f"Second (Prod): {prod_res}. Took {perf_counter() - t0} seconds")
