from pathlib import Path
import math

TEST_FIRST = "11-22,95-115,998-1012,1188511880-1188511890,222220-222224,1698522-1698528,446443-446449,38593856-38593862,565653-565659,824824821-824824827,2121212118-2121212124"


def parse_input(input: str | Path) -> list[tuple[int, int]]:
    if isinstance(input, Path):
        input = input.read_text()
    ranges: list[tuple[int, int]] = []
    for range in input.split(","):
        values = range.split("-")
        ranges.append((int(values[0]), int(values[1])))

    return ranges


def first_slow(input: str | Path):
    ranges = parse_input(input)

    checked: list[int] = []
    invalid: list[int] = []
    for start, end in ranges:
        print(f"Checking range {start}-{end}")

        for i in range(start, end + 1):
            if i in checked:
                continue
            checked.append(i)

            str_i = str(i)
            str_i_len = len(str_i)
            if str_i_len % 2 != 0:
                continue

            if str_i[: str_i_len // 2] == str_i[str_i_len // 2 :]:
                invalid.append(i)

    return sum(invalid)


def first(input: str | Path) -> int:
    ranges = parse_input(input)

    invalid: set[int] = set()
    for start, end in ranges:
        print(f"Checking range {start}-{end}")

        if len(str(start)) % 2 != 0:
            start = 10 ** len(str(start))

        start_str = str(start)
        current = int(start_str[: math.ceil(len(start_str) / 2)])
        if int(f"{current}{current}") < start:
            current += 1

        while (res := int(f"{current}{current}")) <= end:
            # print(f"Adding {res} in range {start}-{end}")
            current += 1
            invalid.add(res)

    return sum(invalid)


def second(input: str | Path) -> int:
    ranges = parse_input(input)

    invalid: set[int] = set()
    for start, end in ranges:
        for i in range(start, end + 1):
            # now we have to check all divisors
            # e.g. if the len is 8, we need to check lengths 1, 2, 4
            str_i = str(i)
            str_i_len = len(str_i)
            for divisor in range(1, str_i_len // 2 + 1):
                if str_i_len % divisor != 0:
                    continue

                root = str_i[:divisor]
                times = str_i_len // divisor
                if root * times == str_i:
                    invalid.add(i)
                    break

    return sum(invalid)


if __name__ == "__main__":
    test_first = first(TEST_FIRST)
    print(f"Test first: {test_first}")
    assert test_first == 1227775554

    prod_first = first(Path("./days/02/input/first"))
    print(f"Prod first: {prod_first}")

    test_second = second(TEST_FIRST)
    print(f"Test second: {test_second}")
    assert test_second == 4174379265

    prod_second = second(Path("./days/02/input/first"))
    print(f"Prod second: {prod_second}")
