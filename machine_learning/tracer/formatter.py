#!/usr/bin/env python3

import sys
from collections import defaultdict

def main(input_file):
    data = defaultdict(list)

    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue

            col0, col1, col2 = line.split(":")
            data[(col2, col0)].append(col1)

    for key, values in data.items():
        filename = f"{key[0]}:{key[1]}.log"
        with open(filename, "w") as out:
            out.write(" ".join(values))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <input_file>")
        sys.exit(1)

    main(sys.argv[1])
