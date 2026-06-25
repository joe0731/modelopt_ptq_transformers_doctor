# AGENTS.md — modelopt-ptq-transformers-doctor

> Canonical agent guide for this repository. `CLAUDE.md` is kept **identical** to
> this file; edit both together. Deeper design docs live in `docs/superpowers/`.

## 1. Purpose

This project is a **compatibility doctor** for the **NVIDIA TensorRT Model
Optimizer (`nvidia-modelopt`) post-training-quantization (PTQ) pipeline** and the
third-party libraries it depends on — **`transformers`, `torch`, `vllm`,
`accelerate`**.

The problem it solves: modelopt's PTQ pipeline calls specific APIs of these
libraries across its whole flow —

1. **init / module replacement** — modelopt swaps `nn.Module`s for quantized
   variants (`QuantModuleRegistry`, the `plugins/huggingface.py` attention & MoE
   integrations), which reference concrete `transformers`/`torch` symbols
   (e.g. `Llama4TextExperts`, `ALL_ATTENTION_FUNCTIONS`, `nn.Linear`);
2. **quantization / recipe matching** — `mtq.quantize`, calibration, and the
   named recipe configs;
3. **export** — `export_hf_checkpoint`, the supported-architecture/experts
   handling, scale extraction, `model.save_pretrained`.

Those APIs **drift across library versions** (symbols move or vanish, signatures
change, config schemas change, new architectures appear). Users hit import
errors, signature mismatches, missing config attributes, or "quantizes but won't
export" failures.

**Goal:** *without actually running models*, statically determine which versions
of each library modelopt's PTQ code is **API-compatible** with — across the whole
init → quantize → export pipeline — and surface API inconsistencies / missing-API
problems early. A separate **runtime verdict layer** (`doctor smoke`) covers what
static analysis cannot reach.

## 2. What it produces

For a chosen `--target` library, a **compatibility matrix**: per modelopt-PTQ
dependency symbol, the contiguous version window where it imports cleanly, plus
**signature drift** within that window, plus dynamic (runtime-registered)
dependencies it can't statically check. Output as `matrix.json`, `REPORT.md`, a
styled standalone `compatibility.html`, and a results-only `compatibility.ipynb`;
multiple targets aggregate into one combined `index.html`/`index.ipynb`.

## 3. Architecture (module map)

| Module | Responsibility |
|---|---|
| `contract.py` | Locate installed modelopt via `find_spec` (never imports it); AST-extract the `<target>.*` symbols its allowlisted PTQ files depend on. |
| `targets.py` | Registry of probe targets (`transformers`/`torch`/`vllm`/`accelerate`): PyPI package, AST import-roots, modelopt allowlist files, pinned co-deps. |
| `allowlist.py` | The transformers target's modelopt source-file list (quant + export). |
| `versions.py` | Discover stable releases of a target from PyPI; select a `--min`/`--max` range. |
| `envman.py` + `prober.py` | Per-version throwaway `uv` venv; **stdlib-only** prober imports each symbol and checks `hasattr` + `inspect.signature`. |
| `version_bisect.py` | Binary-search each symbol's contiguous compatible window. |
| `driver.py` | `build_matrix`: orchestrate, cache probes per version, detect signature drift, drive progress. |
| `progress.py` | `ProgressReporter`/`NullProgress` (stderr bar + ETA + probe estimate). |
| `report.py` | `matrix.json` + `REPORT.md`. |
| `report/render_compat.py` | Styled `compatibility.html` + results-only `.ipynb` (CSS in `report/assets/compat.css`). |
| `report/render_combined.py` | One combined multi-target `index.html`/`.ipynb`. |
| `capabilities.py` | Static **export-capability screening** (`doctor capabilities`). |
| `smoke.py` | Runtime **load → quantize → export** verdict (`doctor smoke`). |
| `cli.py` | `doctor scan` / `doctor capabilities` / `doctor smoke`. |

## 4. What it catches — and what it does NOT (the boundary)

This boundary is a **hard rule**: never overstate a static result as a verdict.

- **`doctor scan` (static, import/API level)** — catches: missing modules,
  moved import paths, changed callable **signatures** (signature drift). Flags
  `register({var:...})` dynamic deps as *runtime-discovered, unchecked*. The
  compatible window is **inferred from a bisection sample** — reports must show
  probed vs **N/A** (untested) versions and never colour untested as compatible.
- **`doctor capabilities` (static screening)** — flags MoE expert types modelopt
  *quantizes* but that the HF export path doesn't explicitly support and that
  don't statically match a structural fallback. This is a **screening signal,
  not a verdict** (export support is a runtime predicate: named cases + fused /
  iterable fallbacks). Candidates mean "verify at runtime".
- **Static layers CANNOT catch**: runtime instance-attribute access (e.g.
  `config.moe_latent_size`), behavioral changes, whether export actually
  succeeds, or recipe-specific runtime errors. "Imports OK + signature OK" ≠
  "runs OK".
- **`doctor smoke` (runtime verdict)** — runs the real pipeline and reports the
  failing **stage** (`LOAD`/`QUANTIZE`/`EXPORT_ERROR` + message). This is the
  only layer that *proves* compatibility; real recipes need a GPU.

Positioning: static layers are **bulk pre-screening**; smoke is the **verdict**.

## 5. Rules & boundaries (constraints every change must honor)

- **Never import modelopt or the target library into the tool's own process.**
  Locate with `find_spec`, parse with AST, and probe inside throwaway `uv`
  environments. (Importing executes code and pulls torch.)
- **`prober.py` MUST stay standard-library only** — it runs inside a foreign env.
- **Backward compatibility:** `--target` defaults to `transformers` and must
  reproduce prior behavior. Keep these signatures stable:
  `extract_contract(root, target=None)`, `fetch_available_versions(pkg=...)`,
  `EnvRunner(prober, pkg=..., extra_deps=...)`, `build_matrix(records, versions,
  env_runner, reporter=None)`, `prober.probe_one`/`probe_records`.
- **Co-dependency isolation is best-effort.** When probing one target, the others
  are pinned to fixed versions (`targets.py:PIN_*`); conflicts surface as
  `ENV_ERROR` (🛠) — **shown honestly, never hidden**.
- **SGLang is unsupported** — modelopt has no sglang integration (nothing to
  probe). Don't add it.
- **Trust boundary:** scans install and import third-party packages in throwaway
  envs. Run only against versions/sources you trust.
- **Reports never lie about coverage:** state the window is inferred, list the
  versions actually probed, mark untested as N/A, label screening as screening.
- **Tests are deterministic and offline** — inject the PyPI opener
  (`versions.py`) and the subprocess runner (`envman.py`); never hit the network
  or run `uv` in unit tests.

## 6. Development workflow

- **Stack:** Python ≥ 3.10, standard library + `packaging`; `uv` on `PATH` for
  scans; `pytest`. `pip install -e . && pip install pytest && pytest` — **all
  tests must pass** before any commit.
- **TDD always.** This repo is built with the `superpowers` flow:
  brainstorm → spec → plan → subagent-driven implementation → review → finish.
  Specs and plans live in `docs/superpowers/`. Skills/skill-edits are themselves
  test-first (RED baseline → write → GREEN verify).
- **Skills:** the repo ships the `compat-report` agent skill for **Claude Code**
  (`.claude/skills/`) and **Codex** (`.codex/skills/`) — it encodes the
  scan→report workflow; keep both copies in sync. The third-party
  `ui-ux-pro-max` design skill is vendored but **git-ignored** (reinstall with
  `uipro init --ai claude|codex`); reports render without it (CSS is baked in).
- **Git discipline:** feature work goes on a branch (not `master` directly);
  Conventional-Commit messages; bump `pyproject.toml` version and tag `vX.Y.Z`
  on release; commit author/committer email is the GitHub noreply
  (`joe0731@users.noreply.github.com`) — never a real corporate email.
- **Report-generator invariants** (in `render_compat.py`): inferred-window note,
  probed-vs-N/A explicit, one column per feature version, **full symbol names**,
  readable `+/−/~` signature diffs, ui-ux-pro-max design (blue+amber, Fira fonts,
  WCAG ≥ 4.5:1 contrast, focus states, reduced-motion, responsive).

## 7. Command reference

```bash
# Static compatibility matrix for a target library
doctor scan --target {transformers,torch,vllm,accelerate} --min A --max B --out DIR
#   --pypi (full stable list), --no-progress

# Static export-capability screening (quantizes-but-may-not-export candidates)
doctor capabilities [--out caps.json]

# Runtime verdict: load -> quantize -> export one model, report the failing stage
doctor smoke --model <hf-id|path> --recipe FP8_DEFAULT_CFG --device cuda \
             [--trust-remote-code] [--out smoke.json]

# Runtime verdict across a target library's versions (per-version isolated envs)
doctor smoke-matrix --model <hf-id> --modelopt nvidia-modelopt==X.Y.Z \
                    --target transformers --min A --max B --recipe FP8_DEFAULT_CFG

# Render reports from a matrix.json / report dir
python report/render_compat.py   <dir>/matrix.json --modelopt-version V --outdir <dir>
python report/render_combined.py <reportdir> --modelopt-version V
```

## 8. Known limitations / next increments

- The static layer is import + signature + export-capability **screening**, not a
  runtime verdict. Reproducing a specific model's failure needs `doctor smoke`
  (single) or `doctor smoke-matrix` (per-version) with that checkpoint on a GPU host.
- `doctor smoke-matrix` installs real modelopt + torch + the target per version —
  heavy and GPU-bound; run it on a cluster, not in CI. The orchestration is
  unit-tested; a single env cell is validated end-to-end (`smoke_prober` emits
  pure JSON with library output quarantined to stderr).
- vLLM scans are heavy and frequently `ENV_ERROR` without CUDA/matching torch —
  expected and shown, not a tool bug.
