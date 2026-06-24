# Design: signature-drift detection + richer reference capture

Date: 2026-06-24

## Problem

The doctor currently answers only "does this `transformers` symbol *import*
cleanly?" (`importlib.import_module` + `hasattr`). That is the shallowest
compatibility signal: a symbol can still import while its **signature changed**
(e.g. `eager_attention_forward(...)`, attention interfaces), which breaks
modelopt's monkey-patch / call sites at runtime even though `hasattr` reports
OK. The tool also misses some references: dotted access to lowercase
module-level functions/constants (e.g. `transformers.models.x.modeling_x.eager_attention_forward`)
is dropped by the AST visitor's "uppercase = class-like" filter.

## Goal

Two low-cost, static enhancements at the tool layer:

1. **Richer reference capture** — capture lowercase module-level
   functions/constants accessed via dotted `transformers.*` chains.
2. **Signature-drift detection** — record each OK symbol's signature
   fingerprint per probed version and flag when it changes across the symbol's
   compatible window.

No new dependencies (`inspect` is stdlib, preserving the foreign-env prober
constraint). No behavioral change to existing probing or the matrix shape
beyond added metadata.

## 1. Reference-form capture (`contract.py`)

Relax `_Visitor.visit_Attribute`'s leaf filter for chains rooted at the literal
`transformers` name (`parts[0] == "transformers"`, `len(parts) >= 2`):

- leaf **Uppercase-first** → capture (unchanged behavior).
- leaf **lowercase** → capture **only if every middle part `parts[1:-1]` is
  also lowercase** (a module-path-like chain) **and** the leaf is not a dunder
  (does not start with `__`). Record `module_path = ".".join(parts[:-1])`,
  `symbol = parts[-1]`, then `return` (maximal chain captured).
- otherwise → `generic_visit` (recurse).

Rationale: this captures `transformers.models.x.modeling_x.eager_attention_forward`
(module.function) while still **excluding** `transformers.AutoModelForCausalLM.from_pretrained`
(uppercase class in a middle part → falls through to `generic_visit`, which
still captures `AutoModelForCausalLM` via the inner Attribute node). `from
transformers import <name>` already captures lowercase names and is unchanged.

## 2. Signature fingerprint (`prober.py`, stays stdlib-only)

After a symbol resolves OK, compute a **fingerprint** string:

- callable (function or class) → `str(inspect.signature(obj))` (for a class,
  this is its `__init__`/`__new__` signature);
- if `inspect.signature(obj)` raises (`ValueError`/`TypeError`, e.g. some
  C-builtins) → `"<no-signature>"`;
- non-callable (e.g. the `ALL_ATTENTION_FUNCTIONS` dict) → `type(obj).__name__`.

`probe_records` returns a new `signatures: {key: fingerprint}` map (only for
symbols whose status is `OK`), and `main()` adds `"signatures"` to the JSON it
writes to stdout. `inspect` is stdlib, so the prober remains dependency-free
inside the foreign env.

## 3. Drift detection (`driver.py`)

`EnvRunner.probe_version` passes `signatures` through in its returned dict
(`out.get("signatures", {})`), so it is cached with the rest of the probe
result. `build_matrix` adds, per static symbol:

- `signatures`: `{version: fingerprint}` over cached versions where the symbol
  was OK (mirrors the existing `statuses` second pass);
- `signature_drift`: `None` when 0–1 distinct fingerprints exist among the OK
  versions; otherwise a list of transition points
  `[[version, fingerprint], …]` — the first OK version and each subsequent
  version where the fingerprint differs from the previous one (versions sorted
  ascending by `packaging.version.Version`).

No new probe status constant. `build_matrix`'s signature is unchanged; the new
data rides along inside `matrix["symbols"][key]`.

## 4. Report (`report.py`)

- Per-symbol: append a `⚇` marker to the symbol cell when `signature_drift` is
  truthy.
- Add a **"Signature changes"** section after the matrix table listing each
  drifting symbol and its `version → fingerprint` transitions, e.g.
  `` `transformers…eager_attention_forward`: 4.48.0 `(module, query, ...)` → 4.52.0 `(module, query, ..., **kwargs)` ``.
- `matrix.json` carries `signatures` and `signature_drift` per symbol.
- Update the legend to document `⚇ signature changed within the compatible window`.

## 5. Versioning

Bump `pyproject.toml` `version` `0.1.0 → 0.2.0` (additive feature).

## Testing

- `contract.py`
  - captures `transformers.models.x.modeling_x.eager_attention_forward`
    (module_path/symbol correct);
  - does **not** capture `from_pretrained` from
    `transformers.AutoModelForCausalLM.from_pretrained`, but **does** still
    capture `AutoModelForCausalLM`;
  - skips dunder leaves (`transformers.x.__version__`).
- `prober.py`
  - fingerprint of a plain function = its `str(signature)`;
  - fingerprint of a class = its `__init__` signature string;
  - fingerprint of a non-callable (dict) = `"dict"`;
  - a callable whose `inspect.signature` raises → `"<no-signature>"`;
  - `signatures` only contains OK symbols.
- `driver.py`
  - `signatures` collected per version for an OK symbol;
  - `signature_drift` is `None` when the fingerprint is identical across OK
    versions;
  - `signature_drift` lists transitions when fingerprints differ.
- `report.py`
  - `⚇` marker present for a drifting symbol, absent otherwise;
  - "Signature changes" section renders the transitions.

## Out of scope (YAGNI)

- Call-site compatibility checking (comparing captured signatures against how
  modelopt actually calls each symbol) — a later enhancement; higher
  false-positive risk.
- Runtime smoke probing (quantize → forward → export) — that is the separate
  Tier-2 effort.
- Semantic/behavioral diffing beyond the signature string.
