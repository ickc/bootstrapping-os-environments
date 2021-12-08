#!/usr/bin/env python

"""similar to ``sort``, but each line might starts
with ``#`` and the sort order will ignore that.
"""

import argparse
import sys

import pandas as pd

__version__ = "0.1"


def main(args):
    texts = pd.DataFrame([line.strip() for line in args.input], columns=["line"])
    texts["key"] = texts.line.map(lambda line: line[1:].strip() if line[0] == "#" else line)
    texts.sort_values("key", inplace=True)
    if args.inplace:
        in_path = args.input.name
        args.input.close()
        args.output = open(in_path, "w")
    args.output.writelines("\n".join(texts.line.values))
    args.output.write("\n")


def cli():
    parser = argparse.ArgumentParser(description="Sort order ignoring initial #.")

    parser.add_argument("input", type=argparse.FileType("r"), default=sys.stdin)
    parser.add_argument("-o", "--output", type=argparse.FileType("w"), default=sys.stdout)
    parser.add_argument("-i", "--inplace", action="store_true")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main(cli())
