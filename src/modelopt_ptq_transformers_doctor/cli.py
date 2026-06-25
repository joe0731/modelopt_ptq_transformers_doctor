"""Command-line entry point: doctor scan ..."""

from __future__ import annotations

import argparse
import os
import sys

from . import prober
from .capabilities import screen_modelopt, format_report
from .contract import extract_contract, installed_modelopt_root
from .driver import build_matrix
from .envman import EnvRunner, SmokeEnvRunner
from .progress import ProgressReporter, NullProgress
from .report import write_report
from .smoke import (build_real_stages, build_smoke_matrix, format_result,
                    format_smoke_matrix_md, run_smoke)
from .targets import TARGETS
from .versions import fetch_available_versions, select_versions


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="doctor",
                                     description="modelopt PTQ ↔ library compatibility matrix")
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan",
                          help="scan the installed modelopt across a target library's versions")
    scan.add_argument("--min", default=None, help="minimum target version (inclusive)")
    scan.add_argument("--max", default=None, help="maximum target version (inclusive)")
    scan.add_argument("--pypi", action="store_true",
                      help="use the full stable PyPI release list as the search space")
    scan.add_argument("--out", default=None, help="output directory (default: doctor-report/<target>)")
    scan.add_argument("--no-progress", action="store_true",
                      help="disable the live progress bar / ETA output")
    scan.add_argument("--target", choices=sorted(TARGETS), default="transformers",
                      help="target package to probe (default: transformers)")

    cap = sub.add_parser(
        "capabilities",
        help="screen modelopt PTQ export-capability gaps (static screening — verify candidates at runtime)")
    cap.add_argument("--out", default=None, help="also write the screening report as JSON to this path")

    smoke = sub.add_parser(
        "smoke",
        help="runtime smoke probe: load → quantize → export one model; report the failing stage")
    smoke.add_argument("--model", required=True, help="HF model id or local path")
    smoke.add_argument("--recipe", default="FP8_DEFAULT_CFG",
                       help="modelopt.torch.quantization config name (e.g. FP8_DEFAULT_CFG, NVFP4_DEFAULT_CFG)")
    smoke.add_argument("--device", default="cuda", help="cuda or cpu (default: cuda)")
    smoke.add_argument("--trust-remote-code", action="store_true",
                       help="allow custom model code from the checkpoint")
    smoke.add_argument("--out", default=None, help="also write the smoke result as JSON to this path")

    sm = sub.add_parser(
        "smoke-matrix",
        help="run the smoke probe (load→quantize→export) across target versions in isolated envs")
    sm.add_argument("--model", required=True, help="HF model id or local path")
    sm.add_argument("--modelopt", required=True, help="modelopt pip spec, e.g. nvidia-modelopt==0.44.0")
    sm.add_argument("--target", choices=sorted(TARGETS), default="transformers",
                    help="library to vary across versions (default: transformers)")
    sm.add_argument("--recipe", default="FP8_DEFAULT_CFG", help="modelopt.torch.quantization config name")
    sm.add_argument("--min", default=None, help="minimum target version (inclusive)")
    sm.add_argument("--max", default=None, help="maximum target version (inclusive)")
    sm.add_argument("--pypi", action="store_true", help="use the full stable PyPI release list")
    sm.add_argument("--device", default="cuda", help="cuda or cpu (default: cuda)")
    sm.add_argument("--trust-remote-code", action="store_true")
    sm.add_argument("--out", default=None, help="output directory (default: doctor-report/smoke-<target>)")
    return parser


def _run_scan(args) -> int:
    target = TARGETS[args.target]

    try:
        modelopt_root = installed_modelopt_root()
    except ModuleNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    try:
        records = extract_contract(modelopt_root, target=target)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    available = fetch_available_versions(pkg=target.pypi)
    if args.pypi and not (args.min or args.max):
        versions = available
    else:
        versions = select_versions(available, args.min, args.max)
    if not versions:
        print(f"error: no {target.name} versions selected for the given range", file=sys.stderr)
        return 3

    runner = EnvRunner(prober.__file__, pkg=target.pypi, extra_deps=target.pinned_deps)
    reporter = NullProgress() if args.no_progress else ProgressReporter(stream=sys.stderr)
    matrix = build_matrix(records, versions, runner, reporter=reporter)
    matrix["target"] = target.name
    matrix["pypi"] = target.pypi

    out_dir = args.out if args.out is not None else os.path.join("doctor-report", target.name)
    json_path, md_path = write_report(matrix, out_dir)
    print(f"wrote {json_path}\nwrote {md_path}")
    return 0


def _run_capabilities(args) -> int:
    try:
        modelopt_root = installed_modelopt_root()
    except ModuleNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    report = screen_modelopt(modelopt_root)
    print(format_report(report))
    if args.out:
        import json
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
        print(f"\nwrote {args.out}", file=sys.stderr)
    return 0


def _run_smoke(args) -> int:
    stages = build_real_stages(args.model, args.recipe, device=args.device,
                               trust_remote_code=args.trust_remote_code)
    result = run_smoke(stages)
    print(format_result(args.model, args.recipe, result))
    if args.out:
        import json
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"model": args.model, "recipe": args.recipe, **result}, fh,
                      indent=2, ensure_ascii=False)
        print(f"wrote {args.out}", file=sys.stderr)
    return 0


def _run_smoke_matrix(args) -> int:
    import json

    target = TARGETS[args.target]
    available = fetch_available_versions(pkg=target.pypi)
    if args.pypi and not (args.min or args.max):
        versions = available
    else:
        versions = select_versions(available, args.min, args.max)
    if not versions:
        print(f"error: no {target.name} versions selected for the given range", file=sys.stderr)
        return 3

    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    runner = SmokeEnvRunner(modelopt_spec=args.modelopt, repo_path=repo_root, target_pkg=target.pypi)
    matrix = build_smoke_matrix(versions, lambda v: runner.smoke_version(
        v, model=args.model, recipe=args.recipe, device=args.device,
        trust_remote_code=args.trust_remote_code))

    meta = {"model": args.model, "recipe": args.recipe, "target": target.name,
            "modelopt": args.modelopt, "device": args.device}
    out_dir = args.out if args.out is not None else os.path.join("doctor-report", f"smoke-{target.name}")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "smoke_matrix.json"), "w", encoding="utf-8") as fh:
        json.dump({**meta, "results": matrix}, fh, indent=2, ensure_ascii=False)
    with open(os.path.join(out_dir, "SMOKE.md"), "w", encoding="utf-8") as fh:
        fh.write(format_smoke_matrix_md(meta, matrix))
    for v, r in matrix.items():
        print(f"  {v}: {r['status']} ({r.get('reached', '')})")
    print(f"wrote {out_dir}/smoke_matrix.json\nwrote {out_dir}/SMOKE.md")
    return 0


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    if args.command == "scan":
        return _run_scan(args)
    if args.command == "capabilities":
        return _run_capabilities(args)
    if args.command == "smoke":
        return _run_smoke(args)
    if args.command == "smoke-matrix":
        return _run_smoke_matrix(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
