#!/usr/bin/env python3

import argparse

from main import parse_and_run

parser = argparse.ArgumentParser()

parser.add_argument("script", type=str, nargs="?", default=None, help="script to run")


def run_script(script_file: str):
    with open(script_file, "r") as fd:
        contents = fd.read()
    return parse_and_run(contents)


def run_repl():
    while True:
        try:
            inp = input("> ")
        except EOFError:
            return 0

        parse_and_run(inp)  # ignore result since it's just the error flag


def main(args):
    if args.script is None:
        print("running repl")
        run_repl()
    else:
        print(f"running script {args.script}")
        run_script(args.script)


if __name__ == "__main__":
    main(parser.parse_args())
