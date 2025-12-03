from pathlib import Path

TEST_FIRST = """
987654321111111
811111111111119
234234234234278
818181911112111
"""


def parse_input(input: str | Path) -> list[list[int]]:
    if isinstance(input, Path):
        input = input.read_text()

    rows: list[list[int]] = []
    for line in input.splitlines():
        if not line.strip():
            continue
        row = []
        for i in list(line):
            row.append(int(i))
        rows.append(row)

    return rows


def first(input: str | Path) -> int:
    banks = parse_input(input)

    max_joltages: list[int] = []
    for bank in banks:
        first: int = bank[0]
        second: int = bank[1]

        for joltage in bank[2:]:
            if second > first:
                first = second
                second = joltage
            elif joltage > second:
                second = joltage

        comb = first * 10 + second
        max_joltages.append(comb)

    return sum(max_joltages)


def second(input: str | Path) -> int:
    banks = parse_input(input)

    max_joltages: list[int] = []
    for bank in banks:
        batteries = bank[:12]

        for joltage in bank[12:]:
            for i in range(12 - 1):
                if batteries[i] < batteries[i + 1]:
                    batteries.pop(i)
                    batteries.append(joltage)
                    break
            if joltage > batteries[-1]:
                batteries[-1] = joltage

        comb = int("".join([str(b) for b in batteries]))
        print(bank, comb)
        max_joltages.append(comb)

    return sum(max_joltages)


# first
test_res = first(TEST_FIRST)
print(f"First (test): {test_res}")
assert test_res == 357

prod_res = first(Path("./days/03/input/first"))
print(f"Prod first: {prod_res}")

# second
test_res = second(TEST_FIRST)
print(f"Second (test): {test_res}")
assert test_res == 3121910778619

prod_res = second(Path("./days/03/input/first"))
print(f"Second first: {prod_res}")
