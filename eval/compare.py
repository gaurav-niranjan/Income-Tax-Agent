"""Compare eval runs.

uv run python eval/compare.py                      # rebuild eval/results/README.md and print it
uv run python eval/compare.py diff <run> <run>     # which config settings differ between two runs

A run can be named by its full id (2026-10-18_3f2a9c1b) or a unique prefix of its config hash (3f2a).
"""

import argparse

from runs import config_diff, find_run, write_index


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    diff = sub.add_parser("diff", help="config settings that differ between two runs")
    diff.add_argument("a")
    diff.add_argument("b")
    args = parser.parse_args()

    if args.command == "diff":
        a, b = find_run(args.a)["config"], find_run(args.b)["config"]
        print(f"{'setting':<45} {a['run_id']:<30} {b['run_id']}")
        for key, va, vb in config_diff(a, b):
            if key in ("run_id", "config_hash"):  # already in the header line
                continue
            print(f"{key:<45} {str(va):<30} {vb}")
    else:
        print(write_index().read_text())


if __name__ == "__main__":
    main()
