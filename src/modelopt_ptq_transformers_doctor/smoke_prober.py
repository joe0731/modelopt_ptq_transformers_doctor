"""Standalone runtime smoke probe, run inside a per-version environment.

Invoked as ``python -m modelopt_ptq_transformers_doctor.smoke_prober`` in a venv
that has ``modelopt`` + ``transformers`` + ``torch`` (and this package) installed.
Reads a JSON request on stdin and writes the smoke result as JSON on stdout::

    in : {"model": "...", "recipe": "FP8_DEFAULT_CFG", "device": "cuda",
          "trust_remote_code": false}
    out: {"reached": "...", "status": "...", "error_type": ..., "error": ...}

It reuses the orchestration + stage builders from :mod:`.smoke`, so the
classification logic stays single-sourced and unit-tested.
"""
import json
import sys

from .smoke import build_real_stages, run_smoke


def main() -> None:
    req = json.load(sys.stdin)
    # modelopt / transformers print to stdout during quantize; quarantine all of
    # it to stderr so this process's stdout is *pure JSON* for the parent.
    real_stdout = sys.stdout
    sys.stdout = sys.stderr
    try:
        stages = build_real_stages(
            req["model"], req["recipe"],
            device=req.get("device", "cuda"),
            trust_remote_code=req.get("trust_remote_code", False),
        )
        result = run_smoke(stages)
    finally:
        sys.stdout = real_stdout
    json.dump(result, real_stdout)


if __name__ == "__main__":
    main()
