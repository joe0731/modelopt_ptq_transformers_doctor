---
name: compat-report
description: Use when asked for a modelopt↔transformers compatibility report for a specific nvidia-modelopt version — e.g. "which transformers releases does modelopt 0.45 PTQ support", "scan modelopt X", or (re)generating the styled HTML / notebook / matrix under report/. For the modelopt_ptq_transformers_doctor repo.
---

# compat-report

## Overview

Produce the modelopt PTQ ↔ transformers compatibility report for ONE
`nvidia-modelopt` version. The `doctor` tool **statically AST-scans the
installed modelopt — it never imports it** — and probes each transformers
release in a throwaway `uv` virtualenv. So the target modelopt only needs its
source on disk (no torch), but real `transformers`+`torch` installs happen
per probed version.

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

3. **Scan up to the newest transformers so the upper bound is real.** The
   compatible window is **clamped to the scanned range**, so a low `--max`
   understates it. Put `--min` near/below the expected window and `--max` at the
   latest release:
   ```bash
   /tmp/doctor-<ver>/bin/doctor scan --min 4.46.0 --max 5.12.1 --out report/modelopt<XX>/
   ```
   Output dir convention: `report/modelopt<major><minor>/` (e.g. `report/modelopt045/`).
   Writes `matrix.json` + `REPORT.md`. It is slow (per-version installs); run in
   the background and poll the log.

4. **Render the styled artifacts** (system `python3` is fine — it has
   `packaging`; this step also fetches the full in-range PyPI list to mark
   N/A versions):
   ```bash
   python3 report/render_compat.py report/modelopt<XX>/matrix.json \
     --modelopt-version <ver> --outdir report/modelopt<XX>/ --generated <YYYY-MM-DD>
   ```
   Produces `compatibility.html` (styled) and `compatibility.ipynb` (results-only).

## Report invariants (keep when editing `report/render_compat.py`)

- **Window is inferred** from a bisection *sample* — show probed vs **N/A**
  versions explicitly; N/A = not tested, and is never coloured as compatible.
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
