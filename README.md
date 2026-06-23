# modelopt-ptq-transformers-doctor

Builds a **compatibility matrix** between [NVIDIA TensorRT Model Optimizer
(modelopt)](https://github.com/NVIDIA/TensorRT-Model-Optimizer) PTQ and the
`transformers` library, by statically extracting the set of `transformers`
symbols that modelopt PTQ depends on and probing each one against a range of
`transformers` releases.

For every dependency symbol it reports the contiguous version window in which
that symbol imports cleanly, so you can answer "which `transformers` versions
does this modelopt checkout actually work with?"

## How it works

1. **Extract** — static AST scan of a modelopt source checkout collects the
   `transformers.*` imports / attribute accesses that PTQ quant & export code
   relies on (`contract.py`, file list in `allowlist.py`).
2. **Discover** — stable `transformers` releases are fetched from PyPI
   (`versions.py`), optionally filtered to a `--min`/`--max` range.
3. **Probe** — for each candidate version a throwaway [`uv`](https://docs.astral.sh/uv/)
   virtualenv is created, `transformers==<version>` (plus `torch`) is installed,
   and a stdlib-only prober imports each symbol inside that env (`envman.py`,
   `prober.py`). A binary search finds each symbol's compatible window
   (`version_bisect.py`).
4. **Report** — results are written as JSON + Markdown (`report.py`).

> **Trust boundary:** this tool creates virtualenvs and **installs and imports
> third-party packages** (`transformers`, `torch`) to probe them. Importing a
> package executes its code. Run it only against versions/sources you trust.

## Requirements

- Python **>= 3.10**
- The [`uv`](https://docs.astral.sh/uv/) executable on `PATH` (used to create
  the per-version probe environments)
- Network access to PyPI (for version discovery and installs)

## Install

```bash
pip install git+https://github.com/joe0731/modelopt_ptq_transformers_doctor
```

Or from a checkout:

```bash
pip install .
```

## Usage

```bash
# Probe a version range against a local modelopt checkout
doctor scan --modelopt /path/to/modelopt --min 4.45.0 --max 4.52.0 --out doctor-report

# Use the full stable PyPI release list as the search space
doctor scan --modelopt /path/to/modelopt --pypi --out doctor-report
```

Options:

| flag | meaning |
|---|---|
| `--modelopt PATH` | path to the modelopt source checkout (required) |
| `--min VERSION` | minimum `transformers` version, inclusive |
| `--max VERSION` | maximum `transformers` version, inclusive |
| `--pypi` | use the full stable PyPI release list (only when no `--min`/`--max`) |
| `--out DIR` | output directory (default: `doctor-report`) |

Output:

- `doctor-report/matrix.json` — machine-readable matrix
- `doctor-report/REPORT.md` — human-readable matrix; the **compatible** column
  is the authoritative per-symbol version window

## Development

```bash
pip install -e .
pip install pytest
pytest
```

## License

MIT — see [LICENSE](LICENSE).
