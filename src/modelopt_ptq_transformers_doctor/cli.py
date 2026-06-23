"""Command-line entry point: doctor scan ..."""

from __future__ import annotations

import argparse
import sys

from . import prober
from .contract import extract_contract, installed_modelopt_root
from .driver import build_matrix
from .envman import EnvRunner
from .progress import ProgressReporter, NullProgress
from .report import write_report
from .versions import fetch_available_versions, select_versions


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="doctor",
                                     description="modelopt PTQ ↔ transformers compatibility matrix")
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan",
                          help="scan the installed modelopt across transformers versions")
    scan.add_argument("--min", default=None, help="minimum transformers version (inclusive)")
    scan.add_argument("--max", default=None, help="maximum transformers version (inclusive)")
    scan.add_argument("--pypi", action="store_true",
                      help="use the full stable PyPI release list as the search space")
    scan.add_argument("--out", default="doctor-report", help="output directory")
    scan.add_argument("--no-progress", action="store_true",
                      help="disable the live progress bar / ETA output")
    return parser


def _run_scan(args) -> int:
    try:
        modelopt_root = installed_modelopt_root()
    except ModuleNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    try:
        records = extract_contract(modelopt_root)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    available = fetch_available_versions()
    if args.pypi and not (args.min or args.max):
        versions = available
    else:
        versions = select_versions(available, args.min, args.max)
    if not versions:
        print("error: no transformers versions selected for the given range", file=sys.stderr)
        return 3

    runner = EnvRunner(prober.__file__)
    reporter = NullProgress() if args.no_progress else ProgressReporter(stream=sys.stderr)
    matrix = build_matrix(records, versions, runner, reporter=reporter)
    json_path, md_path = write_report(matrix, args.out)
    print(f"wrote {json_path}\nwrote {md_path}")
    return 0


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    if args.command == "scan":
        return _run_scan(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
