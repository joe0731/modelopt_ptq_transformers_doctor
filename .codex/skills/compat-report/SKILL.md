---
name: compat-report
description: Use when asked for a modelopt compatibility report against a library — transformers, torch, vllm, or accelerate — e.g. "which transformers/torch/vllm releases does modelopt PTQ support", "scan modelopt X", a multi-library / combined compatibility report, or (re)generating the styled HTML / notebook / matrix under report/. For the modelopt_ptq_transformers_doctor repo.
---

# compat-report

## Overview

Produce the modelopt PTQ compatibility report against a chosen library — one of
`transformers` (default), `torch`, `vllm`, `accelerate` — selected with
`--target`. The `doctor` tool **statically AST-scans the installed modelopt — it
never imports it** — and probes each release of the target library in a
throwaway `uv` virtualenv. So the target modelopt only needs its source on disk
(no torch), but real installs of the target library happen per probed version.
**SGLang is unsupported** (modelopt has no sglang integration — nothing to probe).

## Prerequisites

- `uv` on `PATH`, network access (PyPI installs are real), Python ≥3.10.

## Workflow

1. **Install the target modelopt with `--no-deps`** (only AST-scanned, so torch
   must NOT be pulled), using the **PyPI `==` pin** — not `git@tag`, and never a
   plain `pip install .` (that drags in modelopt HEAD):
   ```bash
   uv venv /tmp/doctor-<ver>
   PY=/tmp/doctor-<ver>/bin/python
   uv pip install --python "$PY" --no-deps packaging "nvidia-modelopt==<ver>"
   uv pip install --python "$PY" --no-deps -e .       # the doctor tool itself
   ```

2. **Verify without importing modelopt** (importing it would load torch; use
   `find_spec` via the contract extractor):
   ```bash
   "$PY" -c "from modelopt_ptq_transformers_doctor.contract import installed_modelopt_root, extract_contract as e; print(len(e(installed_modelopt_root())), 'symbols')"
   ```

3. **Scan each target up to its newest release so the upper bound is real.** The
   compatible ranges are **clamped to the scanned range**, so a low `--max`
   understates later break/fix behaviour. The default scan strategy is
   `risk-adaptive` for quick iteration; use `--strategy full` for release/report
   artifacts that should validate every selected version. Use `--target`
   (default `transformers`) and route each target to its own subdir
   `report/modelopt<XX>/<target>/`:
   ```bash
   DR=/tmp/doctor-<ver>/bin/doctor
   $DR scan --target transformers --strategy full --min 4.46.0 --max 5.12.1 --out report/modelopt<XX>/transformers
   $DR scan --target accelerate   --strategy full --min 1.0.0  --max 1.10.0 --out report/modelopt<XX>/accelerate
   $DR scan --target torch        --strategy full --min 2.1.0  --max 2.8.0  --out report/modelopt<XX>/torch
   $DR scan --target vllm         --strategy full --min 0.6.0  --max 0.11.0 --out report/modelopt<XX>/vllm
   ```
   Each writes `matrix.json` + `REPORT.md`. Slow (per-version installs) — run in
   the background and poll the log; vLLM is heaviest and will produce some
   `ENV_ERROR` cells (acceptable, shown honestly). When probing one target the
   **other libraries are pinned to fixed versions** for isolation (best-effort;
   vLLM dictates its own torch).

4. **Render each target's styled artifacts** (system `python3` is fine — it has
   `packaging`; uses the target package recorded in `matrix.json` to mark N/A):
   ```bash
   for t in transformers accelerate torch vllm; do
     python3 report/render_compat.py report/modelopt<XX>/$t/matrix.json \
       --modelopt-version <ver> --outdir report/modelopt<XX>/$t --generated <YYYY-MM-DD>
   done
   ```
   Produces per-target `compatibility.html` + `compatibility.ipynb`.

5. **Combine into one report** organized by library:
   ```bash
   python3 report/render_combined.py report/modelopt<XX> \
     --modelopt-version <ver> --generated <YYYY-MM-DD>
   ```
   Writes `report/modelopt<XX>/index.html` + `index.ipynb` (overview + a section
   per library).

## Report invariants (keep when editing `report/render_compat.py`)

- **Ranges are validated from directly probed versions** — show probed vs **N/A**
  versions explicitly; N/A = not tested, and is never coloured as compatible.
  State whether the scan used `risk-adaptive` or `full`.
- Support grid: one column per **feature (minor) version**, colour-graded, with
  **full symbol names**.
- Signature drift rendered as readable `+ / − / ~` per-parameter diffs.
- Visual design follows the **ui-ux-pro-max** skill (blue+amber palette, Fira
  fonts, WCAG ≥4.5:1 contrast, focus states).

## Common mistakes

| Mistake | Do instead |
|---|---|
| `pip install nvidia-modelopt` with deps / `git+...@vX` | `uv pip install --no-deps nvidia-modelopt==X` |
| `import modelopt` to read the version | `find_spec` / `extract_contract` (no import → no torch) |
| Low `--max`, then read the window as the true ceiling | scan `--max` at the newest release |
| Editing the report and dropping the probed-vs-N/A distinction | preserve the invariants above |

## Notes

- `matrix.json` is the source of truth; `REPORT.md` is the tool's native plain
  report; `compatibility.html` / `.ipynb` are the presentation artifacts.
- `report/modelopt044/` is a worked example to mirror.

## Related commands (beyond the static scan)

The scan above is the **static API layer**. Two more layers exist for questions
the scan can't answer (see `AGENTS.md` for the full boundary):

- `doctor capabilities [--out caps.json]` — **static export-capability
  screening**: flags MoE experts modelopt quantizes but the export path may not
  support ("quantizes but won't export", e.g. NemotronH). A screening signal,
  not a verdict.

- `doctor model-coverage [--modelopt-root PATH] [--transformers-root PATH] [--out coverage.json]`
  — **static model-family coverage inventory**: lists transformers `models/*`
  families and marks explicit ModelOpt PTQ symbols vs attention/MoE/linear-like
  structural candidates. A screening signal, not a verdict.
- `doctor smoke --model <id> --recipe FP8_DEFAULT_CFG --device cuda` and
  `doctor smoke-matrix --model <id> --modelopt nvidia-modelopt==X --target <lib> --min A --max B`
  — **runtime verdict**: actually run load → quantize → export (single, or per
  version) and report the failing stage. Needs modelopt + transformers + torch
  installed; real recipes need a GPU.
