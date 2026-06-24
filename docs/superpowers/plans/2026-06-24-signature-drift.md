# Signature-Drift Detection + Richer Reference Capture — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Capture lowercase module-level `transformers` references and detect when an OK symbol's signature changes across its compatible window, surfacing "imports fine but signature drifted" risks.

**Architecture:** The stdlib-only prober gains a signature *fingerprint* per OK symbol; the env runner passes it through; `build_matrix` records per-version fingerprints and derives a drift list; the report renders a marker + a "Signature changes" section. The AST contract visitor is widened to also capture lowercase module-level functions/constants.

**Tech Stack:** Python ≥3.10, standard library only (`ast`, `inspect`), `pytest`, `packaging`.

## Global Constraints

- Python **>= 3.10**.
- **No new third-party dependencies** — `inspect` is stdlib (the prober runs inside a foreign uv env and must stay stdlib-only).
- `prober.probe_one(module_path, symbol)` MUST keep returning a status **string**, and `prober.probe_records(records)` MUST keep returning `{key: status}` (existing tests depend on these contracts).
- `build_matrix(records, versions, env_runner, reporter=None)` signature is unchanged; new data rides inside `matrix["symbols"][key]`.
- Drift semantics: `signature_drift` is `None` for 0–1 distinct fingerprints among OK versions; otherwise a list `[[version, fingerprint], …]` — the first OK version and each subsequent version whose fingerprint differs from the previous (versions sorted ascending by `packaging.version.Version`).
- Fingerprint: callable → `str(inspect.signature(obj))`; `inspect.signature` raises → `"<no-signature>"`; non-callable → `type(obj).__name__`.

---

### Task 1: Capture lowercase module-level references (`contract.py`)

**Files:**
- Modify: `src/modelopt_ptq_transformers_doctor/contract.py` (the `_Visitor.visit_Attribute` method)
- Test: `tests/test_contract.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `extract_from_source(source, file, role)` now also yields records for
  `transformers.<all-lowercase-path>.<lowercase_leaf>` (module-level functions/constants),
  while still excluding `Class.method` chains and dunder leaves.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_contract.py` (the file already imports `extract_from_source`; if not, add `from modelopt_ptq_transformers_doctor.contract import extract_from_source`):

```python
def _keys(src):
    return {r.key for r in extract_from_source(src, "f.py", "quant")}


def test_captures_lowercase_module_level_function():
    src = "import transformers\nx = transformers.models.llama.modeling_llama.eager_attention_forward\n"
    assert "transformers.models.llama.modeling_llama:eager_attention_forward" in _keys(src)


def test_does_not_capture_class_method_but_keeps_class():
    src = "import transformers\ny = transformers.AutoModelForCausalLM.from_pretrained\n"
    keys = _keys(src)
    assert "transformers:AutoModelForCausalLM" in keys
    assert "transformers.AutoModelForCausalLM:from_pretrained" not in keys


def test_skips_dunder_leaf():
    src = "import transformers\nv = transformers.__version__\n"
    assert not any(r.symbol == "__version__" for r in extract_from_source(src, "f.py", "quant"))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_contract.py -k "lowercase or class_method or dunder" -v`
Expected: `test_captures_lowercase_module_level_function` FAILS (key missing); the other two PASS already (current behavior). The failing one proves the gap.

- [ ] **Step 3: Implement the widened capture**

In `src/modelopt_ptq_transformers_doctor/contract.py`, replace the `visit_Attribute` method body:

```python
    def visit_Attribute(self, node: ast.Attribute):
        parts = _dotted_name(node)
        if parts and parts[0] == "transformers" and len(parts) >= 2:
            symbol = parts[-1]
            middle = parts[1:-1]
            is_class_like = symbol[:1].isupper()
            is_module_level = (
                not symbol.startswith("__")
                and all(p[:1].islower() for p in middle)
            )
            if is_class_like or is_module_level:
                module_path = ".".join(parts[:-1])
                self._add(module_path, symbol, node.lineno)
                return  # maximal chain captured; deeper sub-chains are prefixes
        self.generic_visit(node)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_contract.py -v`
Expected: PASS (all existing + 3 new).

- [ ] **Step 5: Commit**

```bash
git add src/modelopt_ptq_transformers_doctor/contract.py tests/test_contract.py
git commit -m "feat: capture lowercase module-level transformers references"
```

---

### Task 2: Signature fingerprint in the prober (`prober.py`)

**Files:**
- Modify: `src/modelopt_ptq_transformers_doctor/prober.py`
- Test: `tests/test_prober.py`

**Interfaces:**
- Consumes: nothing new.
- Produces:
  - `prober.fingerprint(obj) -> str`
  - `prober.probe_signatures(records) -> {key: fingerprint}` (OK, non-dynamic symbols only)
  - `main()` JSON output gains a `"signatures"` key.
- `probe_one` and `probe_records` are unchanged.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_prober.py`:

```python
def test_fingerprint_function_is_signature_string():
    assert prober.fingerprint(lambda x, y=1: None) == "(x, y=1)"


def test_fingerprint_class_uses_init_signature():
    class C:
        def __init__(self, a, b=2):
            pass
    assert prober.fingerprint(C) == "(a, b=2)"


def test_fingerprint_non_callable_is_type_name():
    assert prober.fingerprint({}) == "dict"
    assert prober.fingerprint([1]) == "list"


def test_fingerprint_falls_back_when_signature_unavailable(monkeypatch):
    def boom(_obj):
        raise ValueError("no signature")
    monkeypatch.setattr(prober.inspect, "signature", boom)
    assert prober.fingerprint(lambda: None) == "<no-signature>"


def test_probe_signatures_only_ok_non_dynamic():
    import inspect as _inspect
    import json as _json
    recs = [
        {"module_path": "json", "symbol": "dumps", "dynamic": False},
        {"module_path": "json", "symbol": "nope_xyz", "dynamic": False},
        {"module_path": "", "symbol": "mod_type", "dynamic": True},
    ]
    sigs = prober.probe_signatures(recs)
    assert sigs == {"json:dumps": str(_inspect.signature(_json.dumps))}


def test_main_subprocess_includes_signatures():
    payload = json.dumps({"records": [{"module_path": "json", "symbol": "dumps",
                                       "dynamic": False}]})
    proc = subprocess.run([sys.executable, str(PROBER)], input=payload,
                          capture_output=True, text=True, check=True)
    out = json.loads(proc.stdout)
    assert "json:dumps" in out["signatures"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_prober.py -k "fingerprint or probe_signatures or includes_signatures" -v`
Expected: FAIL with `AttributeError: module ... has no attribute 'fingerprint'`.

- [ ] **Step 3: Implement**

In `src/modelopt_ptq_transformers_doctor/prober.py`, add `import inspect` to the imports at the top (so the module exposes `prober.inspect`), then add:

```python
def fingerprint(obj):
    """A stable string identity for drift detection: a callable's signature,
    or the type name for non-callables; '<no-signature>' when unavailable."""
    if callable(obj):
        try:
            return str(inspect.signature(obj))
        except (ValueError, TypeError):
            return "<no-signature>"
    return type(obj).__name__


def probe_signatures(records):
    sigs = {}
    for r in records:
        if r.get("dynamic"):
            continue
        module_path, symbol = r["module_path"], r["symbol"]
        if probe_one(module_path, symbol) != OK:
            continue
        try:
            mod = importlib.import_module(module_path)
        except Exception:
            continue
        obj = mod if symbol is None else getattr(mod, symbol)
        sigs["{}:{}".format(module_path, symbol)] = fingerprint(obj)
    return sigs
```

Then update `main()` to include signatures:

```python
def main():
    payload = json.load(sys.stdin)
    records = payload["records"]
    out = {
        "transformers_version": _transformers_version(),
        "statuses": probe_records(records),
        "signatures": probe_signatures(records),
    }
    json.dump(out, sys.stdout)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_prober.py -v`
Expected: PASS (all existing + 6 new).

- [ ] **Step 5: Commit**

```bash
git add src/modelopt_ptq_transformers_doctor/prober.py tests/test_prober.py
git commit -m "feat: capture per-symbol signature fingerprints in the prober"
```

---

### Task 3: Pass signatures through and detect drift (`envman.py` + `driver.py`)

**Files:**
- Modify: `src/modelopt_ptq_transformers_doctor/envman.py` (the OK return of `probe_version`)
- Modify: `src/modelopt_ptq_transformers_doctor/driver.py`
- Test: `tests/test_driver.py`

**Interfaces:**
- Consumes: probe results may contain a `"signatures": {key: fingerprint}` dict (Task 2).
- Produces:
  - `EnvRunner.probe_version(...)` OK result includes `"signatures"`.
  - `driver._signature_drift(sigs: dict) -> list | None`.
  - `build_matrix` adds `signatures` (`{version: fingerprint}`) and `signature_drift` (`list | None`) to each `matrix["symbols"][key]`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_driver.py`:

```python
class SigRunner:
    """OK on every version; returns a fingerprint per version (by minor)."""

    def __init__(self, sig_by_minor):
        self.sig_by_minor = sig_by_minor

    def probe_version(self, version, records):
        minor = int(version.split(".")[1])
        keys = [f"{r['module_path']}:{r['symbol']}" for r in records]
        return {
            "status": "OK", "installed": version,
            "statuses": {k: "OK" for k in keys},
            "signatures": {k: self.sig_by_minor[minor] for k in keys},
        }


def test_signatures_collected_and_no_drift_when_stable():
    runner = SigRunner({m: "(a)" for m in range(48, 53)})
    m = build_matrix([_rec()], VERSIONS, runner)
    info = m["symbols"]["transformers.models.x.modeling_x:XAttn"]
    assert info["signatures"]["4.48.0"] == "(a)"
    assert info["signature_drift"] is None


def test_signature_drift_detected_when_fingerprint_changes():
    runner = SigRunner({48: "(a)", 49: "(a)", 50: "(a, b)", 51: "(a, b)", 52: "(a, b)"})
    m = build_matrix([_rec()], VERSIONS, runner)
    info = m["symbols"]["transformers.models.x.modeling_x:XAttn"]
    assert info["signature_drift"] == [["4.48.0", "(a)"], ["4.50.0", "(a, b)"]]


def test_missing_signatures_key_defaults_empty():
    # FakeRunner returns no "signatures" key -> no crash, empty map, no drift.
    m = build_matrix([_rec()], VERSIONS, FakeRunner(present_from=48))
    info = m["symbols"]["transformers.models.x.modeling_x:XAttn"]
    assert info["signatures"] == {} and info["signature_drift"] is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_driver.py -k "signature or drift" -v`
Expected: FAIL with `KeyError: 'signatures'` (build_matrix does not yet add the field).

- [ ] **Step 3a: Pass signatures through in `envman.py`**

In `src/modelopt_ptq_transformers_doctor/envman.py`, change the final OK return of `probe_version` to include signatures:

```python
            return {"status": "OK", "installed": out.get("transformers_version"),
                    "statuses": out.get("statuses", {}),
                    "signatures": out.get("signatures", {})}
```

- [ ] **Step 3b: Add drift helper + collection in `driver.py`**

In `src/modelopt_ptq_transformers_doctor/driver.py`, add a module-level helper (after the imports, before `build_matrix`):

```python
def _signature_drift(sigs: dict) -> list | None:
    """Transition points [[version, fingerprint], ...] when >1 distinct
    fingerprints appear across the version->fingerprint map; else None."""
    transitions: list = []
    prev = object()
    for v in sorted(sigs, key=Version):
        fp = sigs[v]
        if fp != prev:
            transitions.append([v, fp])
            prev = fp
    return transitions if len(transitions) > 1 else None
```

Then, immediately after the existing "Second pass" loop that fills
`info["statuses"]` (and before the `matrix["dynamic"] = ...` line), add a
signatures pass:

```python
    for r in static:
        info = matrix["symbols"][r.key]
        sigs = {}
        for v, res in cache.items():
            if res["status"] == OK:
                fp = res.get("signatures", {}).get(r.key)
                if fp is not None:
                    sigs[v] = fp
        info["signatures"] = sigs
        info["signature_drift"] = _signature_drift(sigs)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_driver.py tests/test_envman.py -v`
Expected: PASS (all existing + 3 new driver tests; envman tests unaffected).

- [ ] **Step 5: Commit**

```bash
git add src/modelopt_ptq_transformers_doctor/envman.py src/modelopt_ptq_transformers_doctor/driver.py tests/test_driver.py
git commit -m "feat: thread signatures through and detect per-symbol drift"
```

---

### Task 4: Render drift in the report (`report.py`)

**Files:**
- Modify: `src/modelopt_ptq_transformers_doctor/report.py` (`render_markdown`)
- Test: `tests/test_report.py`

**Interfaces:**
- Consumes: `matrix["symbols"][key]` may now carry `signature_drift` (`list | None`).
- Produces: a `⚇` marker on drifting symbol rows and a "## Signature changes" section.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_report.py`:

```python
DRIFT_MATRIX = {
    "versions_probed": ["4.48.0", "4.50.0"],
    "symbols": {
        "transformers.m:Foo": {
            "file": "hf.py", "line": 1, "guarded": False, "role": "quant",
            "compatible_ranges": [("4.48.0", "4.50.0")],
            "statuses": {"4.48.0": "OK", "4.50.0": "OK"},
            "signatures": {"4.48.0": "(a)", "4.50.0": "(a, b)"},
            "signature_drift": [["4.48.0", "(a)"], ["4.50.0", "(a, b)"]],
        },
    },
    "dynamic": [],
    "env_errors": {},
}


def test_drift_marker_and_section_render():
    md = render_markdown(DRIFT_MATRIX)
    assert "⚇" in md
    assert "## Signature changes" in md
    assert "4.48.0 `(a)`" in md and "4.50.0 `(a, b)`" in md


def test_no_drift_marker_when_absent():
    md = render_markdown(MATRIX)  # MATRIX symbol has no signature_drift
    assert "⚇" not in md
    assert "## Signature changes" not in md
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_report.py -k "drift" -v`
Expected: FAIL (`⚇` / section not produced).

- [ ] **Step 3: Implement**

In `src/modelopt_ptq_transformers_doctor/report.py`, update the symbol-row loop in `render_markdown` to add the drift marker:

```python
    for key, info in sorted(matrix["symbols"].items()):
        cells = [_MARK.get(info["statuses"].get(v, ""), "·") for v in versions]
        guard = " 🛡" if info["guarded"] else ""
        drift = " ⚇" if info.get("signature_drift") else ""
        lines.append(f"| `{key}`{guard}{drift} | {info['role']} | "
                     f"{_range_str(info['compatible_ranges'])} | " + " | ".join(cells) + " |")
```

Then, after the dynamic-registrations block and before the legend line, add a
Signature-changes section:

```python
    drifts = [(k, info) for k, info in sorted(matrix["symbols"].items())
              if info.get("signature_drift")]
    if drifts:
        lines += ["", "## Signature changes (within compatible window)", ""]
        for k, info in drifts:
            trail = " → ".join(f"{v} `{fp}`" for v, fp in info["signature_drift"])
            lines.append(f"- `{k}`: {trail}")
```

Finally, extend the legend line to document the marker:

```python
    lines += ["", "Legend: ✅ OK · ⚠️ symbol missing · ❌ module missing · "
              "🛠 env error · 💥 probe error · 🛡 import is try/except-guarded · "
              "⚇ signature changed within compatible window", ""]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_report.py -v`
Expected: PASS (all existing + 2 new).

- [ ] **Step 5: Commit**

```bash
git add src/modelopt_ptq_transformers_doctor/report.py tests/test_report.py
git commit -m "feat: render signature-drift marker and section in the report"
```

---

### Task 5: Version bump + full-suite verification

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Bump the version**

In `pyproject.toml`, change `version = "0.1.0"` to `version = "0.2.0"`.

- [ ] **Step 2: Run the full suite**

Run: `pytest -q`
Expected: PASS (all tests green).

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: bump version to 0.2.0 (signature-drift detection)"
```

---

## Self-Review

**Spec coverage:**
- Reference-form capture → Task 1.
- Signature fingerprint (callable/class/non-callable/`<no-signature>`) → Task 2.
- `signatures` passthrough → Task 3 (envman).
- `signatures` per version + `signature_drift` semantics → Task 3 (driver) + tests.
- `⚇` marker + "Signature changes" section + legend + JSON carry → Task 4 (JSON carry is automatic — `write_report` dumps the whole matrix dict, which now includes the fields).
- Version bump 0.1.0 → 0.2.0 → Task 5.
- No new deps; prober stdlib-only → `inspect` only (Task 2).
- `probe_one`/`probe_records`/`build_matrix` contracts unchanged → Tasks 2/3 add new functions/fields, do not alter existing ones.

**Placeholder scan:** none — every code/test step contains complete code.

**Type consistency:** `fingerprint`/`probe_signatures` (Task 2) match their use in `main()` and in the drift tests; `_signature_drift` returns `list | None` consistently used by `report.py` (`info.get("signature_drift")`); the `signatures`/`signature_drift` field names are identical across Tasks 3 and 4; the drift list shape `[[version, fingerprint], …]` matches between the driver test, the report test, and the report rendering (`for v, fp in info["signature_drift"]`).
