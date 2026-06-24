# Design: multi-target compatibility scanning (torch / vLLM / accelerate)

Date: 2026-06-24

## Problem

The doctor currently builds a compatibility matrix for **modelopt PTQ ×
transformers** only. modelopt also integrates with other libraries (torch,
vLLM, accelerate) through dedicated plugin modules, and those compatibility
surfaces are equally version-fragile. We want the *same* scan workflow and the
*same* report for each of those targets, plus one combined report.

Recon of the installed modelopt source (which files reference each library):

| target | modelopt integration | status |
|---|---|---|
| torch | core dep, 258 files — use the PTQ-relevant subset | ✅ build |
| vLLM | `quantization/plugins/vllm.py` (+ sparsity/export vllm plugins) | ✅ build |
| accelerate | `quantization/plugins/accelerate.py` (+ trainer/core_utils) | ✅ build |
| **SGLang** | **0 files reference sglang** | ❌ excluded (nothing to probe) |

## Goal

1. Generalize the engine so a single `--target` selects which library to probe.
2. Keep each scan's flow and report identical to the transformers one.
3. When probing one target, hold the **other** libraries at fixed known-good
   versions (best-effort isolation) so a failure is attributable to the target.
4. Aggregate all tested targets into **one combined report**.
5. Update the `compat-report` skill (test-first).

Default `--target transformers` preserves all existing behavior and tests.

## 1. Target registry — `src/modelopt_ptq_transformers_doctor/targets.py`

```python
@dataclass(frozen=True)
class Target:
    name: str                       # "torch"
    pypi: str                       # PyPI package to install & vary
    import_roots: tuple[str, ...]   # AST roots to match (e.g. ("torch",))
    quant_files: tuple[str, ...]
    export_files: tuple[str, ...]
    export_plugin_glob: str | None
    pinned_deps: tuple[str, ...]    # fixed co-deps installed alongside the target
```

`TARGETS: dict[str, Target]` with `transformers` (the current allowlist),
`torch`, `vllm`, `accelerate`. The existing `allowlist.py` constants move into /
are referenced by the `transformers` target.

**Pinned co-deps** are exact pip specs from module-level constants
(`PIN_TORCH`, `PIN_TRANSFORMERS`, `PIN_ACCELERATE`) chosen as a mutually
recent-stable set, easy to edit in one place:

| target | varies | `pinned_deps` |
|---|---|---|
| transformers | `transformers` | `(PIN_TORCH,)` |
| torch | `torch` | `(PIN_TRANSFORMERS, PIN_ACCELERATE)` |
| vllm | `vllm` | `()` — vLLM hard-pins its own torch; let its resolver decide |
| accelerate | `accelerate` | `(PIN_TORCH, PIN_TRANSFORMERS)` |

Isolation is **best-effort**: a pinned co-dep that conflicts with an old target
version surfaces as `ENV_ERROR` (🛠) in the grid — visible and honest, not
hidden. This is documented, not worked around.

Allowlists per target (relative to modelopt root):
- **torch**: `quantization/plugins/{huggingface,transformers,attention}.py`,
  `quantization/nn/modules/tensor_quantizer.py`, `quantization/conversion.py`,
  `export/{unified_export_hf,layer_utils}.py`.
- **vllm**: `quantization/plugins/vllm.py`,
  `sparsity/attention_sparsity/plugins/vllm.py`,
  `export/plugins/vllm_fakequant_megatron.py`.
- **accelerate**: `quantization/plugins/accelerate.py`,
  `quantization/plugins/transformers_trainer.py`,
  `quantization/utils/core_utils.py`.

(Allowlist entries that are absent in a given installed modelopt are skipped, so
older modelopt versions degrade gracefully.)

## 2. Engine parameterization

- **`contract.py`**: `_Visitor` and `extract_contract` accept the `Target`
  (its `import_roots` for AST matching and its allowlist file tuples) instead of
  the hardcoded `"transformers"` and module-level allowlist. The import/attribute
  matchers test membership against `import_roots`.
- **`versions.py`**: `fetch_available_versions(pypi_pkg=...)` — the PyPI URL is
  built from the target's `pypi`. `select_versions` unchanged.
- **`envman.py`**: `EnvRunner(prober, extra_deps=...)` already installs
  `<pkg>==<version>` + `extra_deps`; the target's `pinned_deps` are passed as
  `extra_deps`. The varied package name comes from `target.pypi`.
- **`driver.py`, `prober.py`, `report.py`, `render_compat.py`**: unchanged
  (already target-agnostic).
- **`cli.py`**: add `--target {transformers,torch,vllm,accelerate}` (default
  `transformers`). The chosen target drives contract extraction, version
  discovery, and the probe env. Output dir defaults to
  `report/modelopt<XX>/<target>/`.

`build_matrix`'s signature and the matrix schema are unchanged.

## 3. Output layout

```
report/modelopt<XX>/
  transformers/{matrix.json, REPORT.md, compatibility.html, compatibility.ipynb}
  torch/{...}
  vllm/{...}
  accelerate/{...}
  index.html        # combined report
  index.ipynb       # combined report (results-only)
```

(The existing `report/modelopt044/*` files move under `report/modelopt044/transformers/`.)

## 4. Combined report — `report/render_combined.py`

Reads every `<target>/matrix.json` under a report dir and emits one
`index.html` + `index.ipynb`:
- **Overview**: one summary card-row per target (target, library version range,
  versions probed, #symbols, #with-window, #drift, #env-errors).
- **Per-target sections**: each reuses `render_compat`'s section builders
  (`_per_symbol_table`, `_support_grid`, `_drift_section`, …) and the shared
  `assets/compat.css`, under an `<h2>` per library with anchor links from the
  overview.
- Standalone (CSS inlined), same blue-data + amber design system.

`render_compat.py` is lightly adjusted so its section builders are importable by
`render_combined.py` (they already are module-level functions after the refactor).

## 5. Skill update (test-first)

Update `compat-report` SKILL.md (both `.claude/` and `.codex/`) to document
`--target` and the combined report. Per the writing-skills Iron Law: run a
baseline subagent on a multi-target task without the update (watch it miss
`--target` / pinned-deps / combined report), apply the edit, verify a subagent
with the update complies.

## 6. Execution

After the code lands and unit tests pass, run the scans for `torch`, `vllm`,
`accelerate` against the installed modelopt (reuse the existing transformers
matrix), in the background. Default version ranges per target are chosen to be
modelopt-era-appropriate and are overridable via `--min`/`--max`. vLLM is
expected to be slow and to produce several `ENV_ERROR` cells — acceptable and
shown honestly. Then generate the combined report.

## Testing

- `targets.py`: `TARGETS` contains the four targets; each `Target` has
  non-empty `import_roots` and allowlist; `transformers` target reproduces the
  current allowlist.
- `contract.py`: extracting with the `torch` target captures `torch.*`
  references and not `transformers.*` (and vice-versa); import-root matching
  honors the target.
- `versions.py`: `fetch_available_versions` builds the URL from the target pkg
  (test via injected opener returning a fake PyPI payload).
- `envman.py`: `probe_version` installs `<target.pypi>==<v>` plus `pinned_deps`
  (assert the install command via the fake runner).
- `cli.py`: `--target torch` selects the torch target and routes output to
  `report/.../torch/` (monkeypatched seams, no real install).
- `render_combined.py`: given two fake target matrices, the combined HTML
  contains both library sections + an overview row each; ipynb has 0 code cells.

## Out of scope (YAGNI)

- SGLang (no modelopt integration).
- Runtime smoke-probing (separate Tier-2 effort).
- Auto-selecting "known-good" pinned versions (they are fixed constants;
  conflicts surface as ENV_ERROR).
