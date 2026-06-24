# Multi-Target Compatibility Scanning — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Let the doctor scan modelopt PTQ compatibility against any of `transformers`, `torch`, `vllm`, `accelerate` (one `--target`), holding the other libraries at fixed versions, and aggregate all targets into one combined report.

**Architecture:** A `targets.py` registry describes each library (PyPI package, AST import-roots, modelopt allowlist files, pinned co-deps). `contract.py`/`versions.py`/`envman.py`/`cli.py` are parameterized by the selected `Target`; `driver.py`/`prober.py`/`report.py`/`render_compat.py` are unchanged. A new `render_combined.py` aggregates per-target `matrix.json` files into one `index.html` + `index.ipynb`.

**Tech Stack:** Python ≥3.10, stdlib + `packaging`, `uv`, `pytest`.

## Global Constraints

- Python **>= 3.10**, standard library only in `prober.py` (runs in foreign env).
- Default `--target transformers` MUST reproduce current behavior (all existing tests pass unchanged).
- Public contracts that existing tests depend on stay backward compatible: `extract_contract(modelopt_root)`, `fetch_available_versions()`, `EnvRunner(prober_path, ...)`, `build_matrix(records, versions, env_runner, reporter=None)`, `probe_one`/`probe_records`.
- SGLang is excluded (0 modelopt references).
- Co-dep isolation is best-effort; conflicts surface as `ENV_ERROR` (not hidden).

---

### Task 1: Target registry (`targets.py`)

**Files:**
- Create: `src/modelopt_ptq_transformers_doctor/targets.py`
- Test: `tests/test_targets.py`

**Interfaces produced:**
- `@dataclass(frozen=True) Target` with fields `name:str`, `pypi:str`, `import_roots:tuple[str,...]`, `quant_files:tuple[str,...]`, `export_files:tuple[str,...]`, `export_plugin_glob:str|None`, `pinned_deps:tuple[str,...]`, plus property `files -> tuple[str,...]` (quant+export) and `role_of(rel) -> str`.
- `TARGETS: dict[str, Target]` with keys `transformers`, `torch`, `vllm`, `accelerate`.
- Constants `PIN_TORCH`, `PIN_TRANSFORMERS`, `PIN_ACCELERATE`.

- [ ] **Step 1: Failing test** — `tests/test_targets.py`:

```python
from modelopt_ptq_transformers_doctor.targets import TARGETS, Target


def test_four_targets_present():
    assert set(TARGETS) == {"transformers", "torch", "vllm", "accelerate"}


def test_each_target_well_formed():
    for name, t in TARGETS.items():
        assert isinstance(t, Target) and t.name == name
        assert t.pypi and t.import_roots and t.files
        assert all(f.endswith(".py") for f in t.files)


def test_transformers_target_matches_legacy_allowlist():
    from modelopt_ptq_transformers_doctor import allowlist
    t = TARGETS["transformers"]
    assert t.import_roots == ("transformers",)
    assert set(t.quant_files) == set(allowlist.QUANT_FILES)
    assert set(t.export_files) == set(allowlist.EXPORT_FILES)
    assert t.role_of(allowlist.QUANT_FILES[0]) == "quant"


def test_pinned_deps_isolation():
    assert TARGETS["torch"].pinned_deps  # pins transformers/accelerate
    assert TARGETS["vllm"].pinned_deps == ()  # vllm dictates torch
    assert any("torch" in d for d in TARGETS["accelerate"].pinned_deps)
```

- [ ] **Step 2: Run, expect fail** (`ModuleNotFoundError`).

- [ ] **Step 3: Implement** `src/modelopt_ptq_transformers_doctor/targets.py`:

```python
"""Registry of libraries the doctor can probe modelopt PTQ against."""
from __future__ import annotations

from dataclasses import dataclass

from . import allowlist

# Fixed co-dependency pins for isolation (edit here to retune the known-good set).
PIN_TORCH = "torch==2.6.0"
PIN_TRANSFORMERS = "transformers==4.56.0"
PIN_ACCELERATE = "accelerate==1.10.0"


@dataclass(frozen=True)
class Target:
    name: str
    pypi: str
    import_roots: tuple[str, ...]
    quant_files: tuple[str, ...]
    export_files: tuple[str, ...]
    export_plugin_glob: str | None
    pinned_deps: tuple[str, ...]

    @property
    def files(self) -> tuple[str, ...]:
        return self.quant_files + self.export_files

    def role_of(self, rel: str) -> str:
        return "quant" if rel in self.quant_files else "export"


TARGETS: dict[str, Target] = {
    "transformers": Target(
        name="transformers", pypi="transformers", import_roots=("transformers",),
        quant_files=tuple(allowlist.QUANT_FILES), export_files=tuple(allowlist.EXPORT_FILES),
        export_plugin_glob=allowlist.EXPORT_PLUGIN_GLOB, pinned_deps=(PIN_TORCH,),
    ),
    "torch": Target(
        name="torch", pypi="torch", import_roots=("torch",),
        quant_files=(
            "modelopt/torch/quantization/plugins/huggingface.py",
            "modelopt/torch/quantization/plugins/transformers.py",
            "modelopt/torch/quantization/plugins/attention.py",
            "modelopt/torch/quantization/nn/modules/tensor_quantizer.py",
            "modelopt/torch/quantization/conversion.py",
        ),
        export_files=(
            "modelopt/torch/export/unified_export_hf.py",
            "modelopt/torch/export/layer_utils.py",
        ),
        export_plugin_glob=None, pinned_deps=(PIN_TRANSFORMERS, PIN_ACCELERATE),
    ),
    "vllm": Target(
        name="vllm", pypi="vllm", import_roots=("vllm",),
        quant_files=(
            "modelopt/torch/quantization/plugins/vllm.py",
            "modelopt/torch/sparsity/attention_sparsity/plugins/vllm.py",
        ),
        export_files=("modelopt/torch/export/plugins/vllm_fakequant_megatron.py",),
        export_plugin_glob=None, pinned_deps=(),
    ),
    "accelerate": Target(
        name="accelerate", pypi="accelerate", import_roots=("accelerate",),
        quant_files=(
            "modelopt/torch/quantization/plugins/accelerate.py",
            "modelopt/torch/quantization/plugins/transformers_trainer.py",
            "modelopt/torch/quantization/utils/core_utils.py",
        ),
        export_files=(),
        export_plugin_glob=None, pinned_deps=(PIN_TORCH, PIN_TRANSFORMERS),
    ),
}
```

- [ ] **Step 4: Run, expect pass.**
- [ ] **Step 5: Commit** `feat: add multi-target registry (targets.py)`.

---

### Task 2: Parameterize contract extraction (`contract.py`)

**Files:**
- Modify: `src/modelopt_ptq_transformers_doctor/contract.py`
- Test: `tests/test_contract.py`

**Interfaces:**
- Consumes: `Target` (Task 1).
- Produces: `_Visitor(file, role, import_roots=("transformers",))`; `extract_from_source(source, file, role, import_roots=("transformers",))`; `extract_contract(modelopt_root, target=None)` (None → transformers target).

- [ ] **Step 1: Failing tests** — append to `tests/test_contract.py`:

```python
from modelopt_ptq_transformers_doctor.targets import TARGETS


def _keys_for(src, roots):
    from modelopt_ptq_transformers_doctor.contract import extract_from_source
    return {r.key for r in extract_from_source(src, "f.py", "quant", import_roots=roots)}


def test_import_roots_select_target_library():
    src = "import torch\nx = torch.nn.Linear\nfrom transformers import AutoConfig\n"
    torch_keys = _keys_for(src, ("torch",))
    assert any(k.startswith("torch") for k in torch_keys)
    assert not any("transformers" in k for k in torch_keys)
    tf_keys = _keys_for(src, ("transformers",))
    assert "transformers:AutoConfig" in tf_keys
    assert not any(k.startswith("torch") for k in tf_keys)


def test_extract_contract_accepts_target():
    # default still works (transformers); torch target reads torch allowlist
    import modelopt_ptq_transformers_doctor.contract as c
    assert c.extract_contract.__defaults__ is not None  # has a default target arg
```

- [ ] **Step 2: Run focused test, expect fail** (`extract_from_source` has no `import_roots` kwarg).

- [ ] **Step 3: Implement.** In `contract.py`:
  - `_Visitor.__init__(self, file, role, import_roots=("transformers",))` stores `self.import_roots = tuple(import_roots)`.
  - In `visit_ImportFrom`, replace the `transformers` literal check with:
    ```python
    if node.module and any(node.module == r or node.module.startswith(r + ".") for r in self.import_roots):
    ```
  - In `visit_Attribute`, replace `parts[0] == "transformers"` with `parts[0] in self.import_roots`.
  - `extract_from_source(source, file, role, import_roots=("transformers",))` passes `import_roots` to `_Visitor`.
  - Rewrite `extract_contract`:
    ```python
    def extract_contract(modelopt_root, target=None):
        from .targets import TARGETS
        target = target or TARGETS["transformers"]
        records = []
        for rel in target.files:
            path = os.path.join(modelopt_root, rel)
            if not os.path.isfile(path):
                continue  # absent in this modelopt version — skip gracefully
            with open(path, encoding="utf-8") as fh:
                records += extract_from_source(fh.read(), rel, target.role_of(rel),
                                               import_roots=target.import_roots)
        if target.export_plugin_glob:
            for path in sorted(glob.glob(os.path.join(modelopt_root, target.export_plugin_glob))):
                rel = os.path.relpath(path, modelopt_root)
                with open(path, encoding="utf-8") as fh:
                    records += extract_from_source(fh.read(), rel, "export",
                                                   import_roots=target.import_roots)
        return records
    ```
  - NOTE behavior change: missing allowlist files are now **skipped** (was: raise `FileNotFoundError`). Update `tests/test_cli.py::test_main_returns_nonzero_when_extraction_fails` is unaffected (it patches `extract_contract` to raise). The `installed-modelopt` import-error path still returns 2. Remove the now-unused `ROLE_OF`/`QUANT_FILES` imports only if unused; keep `allowlist.py` (targets.py imports it).

- [ ] **Step 4: Run `pytest tests/test_contract.py -v`, expect pass** (existing transformers tests still pass: default target unchanged).
- [ ] **Step 5: Commit** `feat: parameterize contract extraction by target import-roots/allowlist`.

---

### Task 3: Parameterize version discovery (`versions.py`)

**Files:**
- Modify: `src/modelopt_ptq_transformers_doctor/versions.py`
- Test: `tests/test_versions.py`

**Interfaces:**
- Produces: `fetch_available_versions(pkg="transformers", opener=urllib.request.urlopen, timeout=30.0)` — builds the PyPI URL from `pkg`.

- [ ] **Step 1: Failing test** — append to `tests/test_versions.py`:

```python
def test_fetch_uses_pkg_in_url():
    seen = {}
    def fake_opener(url, timeout=0):
        seen["url"] = url
        import io, json
        return io.BytesIO(json.dumps({"releases": {"1.0.0": []}}).encode())
    from modelopt_ptq_transformers_doctor.versions import fetch_available_versions
    out = fetch_available_versions(pkg="torch", opener=fake_opener)
    assert "torch" in seen["url"] and out == ["1.0.0"]
```

- [ ] **Step 2: Run, expect fail** (`fetch_available_versions` has no `pkg` kwarg).
- [ ] **Step 3: Implement** — change signature to `fetch_available_versions(pkg="transformers", opener=urllib.request.urlopen, url=None, timeout=30.0)`; if `url is None`, `url = f"https://pypi.org/pypi/{pkg}/json"`. Keep the rest identical. (Existing call `fetch_available_versions()` still works — default pkg.) The fake opener returns a context-manager-less stream, so wrap the read defensively: support both `with opener(...) as r:` — keep current `with` usage; the test's `io.BytesIO` supports the context manager protocol.
- [ ] **Step 4: Run `pytest tests/test_versions.py -v`, expect pass.**
- [ ] **Step 5: Commit** `feat: parameterize version discovery by PyPI package`.

---

### Task 4: Parameterize the probe package (`envman.py`)

**Files:**
- Modify: `src/modelopt_ptq_transformers_doctor/envman.py`
- Test: `tests/test_envman.py`

**Interfaces:**
- Produces: `EnvRunner(prober_path, pkg="transformers", extra_deps=("torch",), uv="uv", runner=subprocess.run)`; `probe_version` installs `f"{self.pkg}=={version}"` + `extra_deps`.

- [ ] **Step 1: Failing test** — append to `tests/test_envman.py`:

```python
def test_probe_installs_target_pkg_and_pinned_deps():
    cmds = []
    def fake_run(cmd, **kw):
        cmds.append(cmd)
        import types, json as _j
        is_probe = any("prober" in str(c) for c in cmd)
        if is_probe:
            return types.SimpleNamespace(returncode=0, stdout=_j.dumps(
                {"transformers_version": None, "statuses": {}, "signatures": {}}), stderr="")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")
    from modelopt_ptq_transformers_doctor.envman import EnvRunner
    r = EnvRunner(PROBER, pkg="vllm", extra_deps=("transformers==4.56.0",), runner=fake_run)
    r.probe_version("0.9.0", RECORDS)
    install = next(c for c in cmds if "install" in c)
    assert "vllm==0.9.0" in install and "transformers==4.56.0" in install
```

- [ ] **Step 2: Run, expect fail** (`EnvRunner` has no `pkg` kwarg / installs `transformers==`).
- [ ] **Step 3: Implement** — add `pkg="transformers"` param to `EnvRunner.__init__` (store `self.pkg`); in `probe_version` change `pkgs = [f"transformers=={version}", *self.extra_deps]` to `pkgs = [f"{self.pkg}=={version}", *self.extra_deps]`.
- [ ] **Step 4: Run `pytest tests/test_envman.py -v`, expect pass** (existing tests use default `pkg`).
- [ ] **Step 5: Commit** `feat: parameterize EnvRunner probe package`.

---

### Task 5: `--target` CLI wiring (`cli.py`)

**Files:**
- Modify: `src/modelopt_ptq_transformers_doctor/cli.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `TARGETS` (Task 1), parameterized contract/versions/envman (Tasks 2-4).
- Produces: `scan --target {transformers,torch,vllm,accelerate}` (default `transformers`); output dir defaults to `<out>/<target>` when `--out` is left default.

- [ ] **Step 1: Failing tests** — append to `tests/test_cli.py`:

```python
def test_parser_accepts_target():
    p = cli.build_arg_parser()
    ns = p.parse_args(["scan", "--target", "torch"])
    assert ns.target == "torch"
    assert p.parse_args(["scan"]).target == "transformers"


def test_target_routes_pkg_and_outdir(tmp_path, monkeypatch):
    from modelopt_ptq_transformers_doctor.targets import TARGETS
    monkeypatch.setattr(cli, "installed_modelopt_root", lambda: "/x")
    captured = {}
    def fake_extract(root, target=None):
        captured["target"] = target
        return []
    monkeypatch.setattr(cli, "extract_contract", fake_extract)
    monkeypatch.setattr(cli, "fetch_available_versions", lambda pkg="transformers": ["1.0.0"])
    monkeypatch.setattr(cli, "select_versions", lambda a, mn, mx: ["1.0.0"])
    class FakeRunner:
        def __init__(self, *a, **k): captured["pkg"] = k.get("pkg")
        def probe_version(self, v, recs): return {"status": "OK", "installed": v, "statuses": {}, "signatures": {}}
    monkeypatch.setattr(cli, "EnvRunner", FakeRunner)
    monkeypatch.setattr(cli, "build_matrix", lambda *a, **k: {"versions_probed": ["1.0.0"], "symbols": {}, "dynamic": [], "env_errors": {}})
    out = tmp_path / "rep"
    rc = cli.main(["scan", "--target", "torch", "--out", str(out)])
    assert rc == 0
    assert captured["target"] is TARGETS["torch"]
    assert captured["pkg"] == "torch"
```

- [ ] **Step 2: Run, expect fail** (`ns.target` missing).
- [ ] **Step 3: Implement.** In `cli.py`:
  - import: `from .targets import TARGETS`.
  - parser: `scan.add_argument("--target", choices=sorted(TARGETS), default="transformers", help="library to probe modelopt against")`.
  - in `_run_scan`: `target = TARGETS[args.target]`; `records = extract_contract(modelopt_root, target)`; `available = fetch_available_versions(pkg=target.pypi)`; error messages and the "no versions" message use `target.name`; `runner = EnvRunner(prober.__file__, pkg=target.pypi, extra_deps=target.pinned_deps)`; output dir: `out = args.out if args.out != "doctor-report" else os.path.join("doctor-report", target.name)` — keep simple: when user passes `--out`, honor it as-is; else default `doctor-report/<target>`. (Add `import os`.)
  - Keep help text generic ("…across library versions").

- [ ] **Step 4: Run `pytest tests/test_cli.py -v`, expect pass.**
- [ ] **Step 5: Commit** `feat: add --target to doctor scan (transformers/torch/vllm/accelerate)`.

---

### Task 6: Combined report (`report/render_combined.py`)

**Files:**
- Create: `report/render_combined.py`
- Test: `tests/test_render_combined.py`

**Interfaces:**
- Consumes: `report/render_compat.py` section builders (`_per_symbol_table`, `_support_grid`, `_drift_section`, `_never_section`, `_dynamic_section`, `summary`, `fetch_full_range`, `_css`, `esc`) — import them.
- Produces CLI: `python report/render_combined.py REPORTDIR --modelopt-version X [--generated D]` → writes `REPORTDIR/index.html` + `REPORTDIR/index.ipynb`. It discovers `REPORTDIR/<target>/matrix.json` for each known target.

- [ ] **Step 1: Failing test** — `tests/test_render_combined.py`:

```python
import json, sys, importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "report"))
rc = importlib.import_module("render_combined")


def _matrix(probed, key):
    return {"versions_probed": probed, "symbols": {key: {"file": "f.py", "line": 1,
            "guarded": False, "role": "quant", "compatible_ranges": [[probed[0], probed[-1]]],
            "statuses": {v: "OK" for v in probed}, "signatures": {}, "signature_drift": None}},
            "dynamic": [], "env_errors": {}}


def test_combined_has_section_per_target(tmp_path):
    (tmp_path / "torch").mkdir(); (tmp_path / "accelerate").mkdir()
    (tmp_path / "torch" / "matrix.json").write_text(json.dumps(_matrix(["2.6.0"], "torch:Tensor")))
    (tmp_path / "accelerate" / "matrix.json").write_text(json.dumps(_matrix(["1.10.0"], "accelerate:Accelerator")))
    rc.build_combined(str(tmp_path), "0.44.0", "2026-06-24")
    html = (tmp_path / "index.html").read_text()
    assert "torch" in html and "accelerate" in html and "Overview" in html
    nb = json.loads((tmp_path / "index.ipynb").read_text())
    assert sum(1 for c in nb["cells"] if c["cell_type"] == "code") == 0
```

- [ ] **Step 2: Run, expect fail** (module/`build_combined` missing).
- [ ] **Step 3: Implement** `report/render_combined.py`:
  - `import render_compat as R` (same dir).
  - `KNOWN_TARGETS = ["transformers", "torch", "vllm", "accelerate"]`.
  - `build_combined(report_dir, modelopt_version, generated)`: for each known target with a `matrix.json`, load it, compute `R.fetch_full_range(...)` (offline-safe fallback to probed) and `R.summary`. Build an overview table (one row per target: target, version range, #probed, symbols, with_window, drift, env_errors) and per-target `<section>` reusing `R._per_symbol_table(...)`, `R._support_grid(...)`, `R._drift_section(...)`, `R._never_section(...)`. Wrap in the same `<!DOCTYPE>`/`<style>{R._css()}</style>` scaffold (factor a small local scaffold or call into a shared helper). Write `index.html`. For `index.ipynb`, emit markdown-only cells: an overview table + per-target compatibility tables (reuse the notebook table-building logic by importing helpers, or rebuild minimal markdown tables here).
  - `main()` argparse: `report_dir`, `--modelopt-version`, `--outdir` (default = report_dir), `--generated`.
- [ ] **Step 4: Run `pytest tests/test_render_combined.py -v`, expect pass.**
- [ ] **Step 5: Commit** `feat: add combined multi-target report (render_combined.py)`.

---

### Task 7: Full suite + version bump

- [ ] **Step 1:** Run `pytest -q` — all pass.
- [ ] **Step 2:** Bump `pyproject.toml` version `0.2.0` → `0.3.0`.
- [ ] **Step 3:** Commit `chore: bump version to 0.3.0 (multi-target scanning)`.

---

## Post-implementation (controller-run, not subagent tasks)

1. **Run scans** (background, against installed modelopt): for `torch`, `vllm`, `accelerate` (transformers already scanned) into `report/modelopt046/<target>/` (the installed modelopt is 0.46.0.dev86 — use `modelopt046`; re-scan transformers there too for a consistent set). Default ranges: torch `2.0.0`→latest, vllm `0.6.0`→latest, accelerate `1.0.0`→latest; bound as needed. vLLM expected slow + several ENV_ERROR.
2. **Per-target render**: `python3 report/render_compat.py report/modelopt046/<target>/matrix.json --modelopt-version 0.46.0.dev86 --outdir report/modelopt046/<target>/`.
3. **Combined report**: `python3 report/render_combined.py report/modelopt046 --modelopt-version 0.46.0.dev86`.
4. **Skill update (test-first)**: update `compat-report` SKILL.md (`.claude/` + `.codex/`) for `--target` + combined report; RED baseline → edit → GREEN verify.
5. **README**: document `--target`, the combined report, and SGLang exclusion (EN + CN).
6. **Finish branch**: merge, tag `v0.3.0`, push.

## Self-Review

**Spec coverage:** targets registry → T1; engine parameterization → T2 (contract), T3 (versions), T4 (envman), T5 (cli); output layout `<out>/<target>` → T5; combined report → T6; co-dep pinning → T1 (`pinned_deps`) + T4 (installed); skill update + scans + README + finish → Post-implementation. SGLang exclusion → T1 (absent) + README.

**Placeholder scan:** none — each step has concrete code/commands.

**Type consistency:** `Target` fields/`files`/`role_of` used consistently across T1/T2/T5; `extract_contract(root, target=None)`, `fetch_available_versions(pkg=...)`, `EnvRunner(..., pkg=...)` signatures match between definition and CLI use; `render_combined.build_combined(report_dir, modelopt_version, generated)` matches its test.
