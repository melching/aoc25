from time import perf_counter
from dataclasses import dataclass
import re
from pathlib import Path
from functools import lru_cache

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


def second(input: str | Path) -> int:
    # now we have a completely different problem. The previous limit on button presses
    # is no longer valid here.
    # The only limit I can think of for now is to check how many times each button can be presses max
    # (as we still cannot substract) to limit the set of possibilities.
    # Of course, stopping early is always nice to reduce time.

    # I used itertools here, as it would be far to annoying otherwise. But still no fancy math and such!

    # I feel like I cannot get around building a nicely pruned tree here :/ .

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
        max_presses_per_isolated_button.sort(key=lambda x: x[1])

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

                bad_paths = set()
                for p, path in enumerate(paths):
                    if p in bad_paths:
                        continue
                    added_joltage = add_joltages(joltage, path.joltage)
                    cmped = compare(added_joltage)
                    presses = btn_presses + path.press_count
                    if cmped < 0:
                        bad_paths.add(p)
                        continue
                    elif cmped == 1:
                        # print(
                        #     f"Found solution of lenth {presses} for btn {btn_idx} with {btn_presses} presses and chain\n{path.printable()}"
                        # )
                        # print(config.target_joltage, added_joltage)

                        # no need to add a node here, as the new nodes are all invalid if they depend on this
                        if presses < shortest_known_path:
                            shortest_known_path = presses
                        continue
                    else:
                        # check if we already now a node like this but with a shorter path
                        if any(
                            added_joltage == config.target_joltage
                            and n.press_count <= presses
                            for n in paths
                        ):
                            print("Found smaller path in chache, skipping")
                            continue
                        if any(
                            added_joltage == config.target_joltage
                            and n.press_count > presses
                            for n in paths
                        ):
                            print("Found smaller path in chache, should be replacing")

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
test_res = second(TEST_FIRST)
print(f"Second (Test): {test_res}")
assert test_res == 33

t0 = perf_counter()
prod_res = second(Path("./days/10/input/first"))
print(f"Second (Prod): {prod_res}. Took {perf_counter() - t0} seconds")
