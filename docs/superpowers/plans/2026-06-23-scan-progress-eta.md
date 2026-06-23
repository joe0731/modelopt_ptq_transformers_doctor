# Scan Progress Bar, ETA, and Bisection Estimate — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give `doctor scan` live progress (bar + ETA), show the `transformers` version under test, and print an up-front estimate of binary-search probe count.

**Architecture:** A new stdlib-only `progress.py` owns all progress I/O (pure helpers + a `ProgressReporter` and a no-op `NullProgress`). `driver.build_matrix` gains an optional `reporter` parameter and fires callbacks only on cache-miss (real installs). `cli` adds `--no-progress` and wires a stderr reporter.

**Tech Stack:** Python ≥3.10, standard library only (`math`, `time`, `sys`), `pytest`.

## Global Constraints

- Python **>= 3.10**.
- **No new third-party dependencies** — standard library only.
- Progress output goes to **stderr**; stdout (`wrote …`) and `--out` report files stay untouched.
- `build_matrix` must stay **backward compatible**: existing `build_matrix(records, versions, runner)` calls keep working (new `reporter` param defaults to a no-op).
- Progress is **on by default**; `--no-progress` disables it.
- Progress denominator is **N** (the candidate version count); ETA is an upper bound shown with a `<=` marker.

---

### Task 1: Pure helpers in `progress.py`

**Files:**
- Create: `src/modelopt_ptq_transformers_doctor/progress.py`
- Test: `tests/test_progress.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `estimate_probes(n_versions: int, n_symbols: int) -> tuple[int, int]`
  - `format_duration(seconds: float) -> str`
  - `format_eta(avg: float, remaining: int) -> str`
  - `render_bar(done: int, total: int, width: int = 10) -> str`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_progress.py
import math
from modelopt_ptq_transformers_doctor import progress


def test_estimate_probes_bounds():
    assert progress.estimate_probes(0, 3) == (0, 0)
    assert progress.estimate_probes(1, 3) == (1, 1)
    # high is always n_versions; low never exceeds high
    for n in (2, 10, 130):
        low, high = progress.estimate_probes(n, 5)
        assert high == n
        assert 1 <= low <= n
        assert low == min(n, 5 + 2 * math.ceil(math.log2(n)))


def test_format_duration():
    assert progress.format_duration(0) == "0s"
    assert progress.format_duration(28) == "28s"
    assert progress.format_duration(192) == "3m12s"
    assert progress.format_duration(64) == "1m04s"


def test_format_eta_unknown_when_no_average():
    assert progress.format_eta(0.0, 5) == "?"
    assert progress.format_eta(30.0, 0) == "0s"
    assert progress.format_eta(30.0, 2) == "1m00s"


def test_render_bar():
    assert progress.render_bar(0, 10) == "░" * 10
    assert progress.render_bar(10, 10) == "█" * 10
    assert progress.render_bar(5, 10) == "█████░░░░░"
    # total <= 0 renders a full bar (avoids div-by-zero)
    assert progress.render_bar(0, 0) == "█" * 10
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_progress.py -v`
Expected: FAIL with `ModuleNotFoundError` / `AttributeError: module ... has no attribute 'estimate_probes'`.

- [ ] **Step 3: Write minimal implementation**

```python
# src/modelopt_ptq_transformers_doctor/progress.py
"""Live progress reporting for doctor scan (standard library only)."""

from __future__ import annotations

import math
import sys
import time


def estimate_probes(n_versions: int, n_symbols: int) -> tuple[int, int]:
    """Estimated (low, high) number of unique version probes a scan performs.

    high == n_versions (a version is never installed twice — the driver caches
    per version). low ~= one symbol's bisection cost (an anchor sample of <=5
    points plus two edge binary searches); runs usually land near low because
    symbols share the cache.
    """
    if n_versions <= 1:
        return (n_versions, n_versions)
    low = min(n_versions, 5 + 2 * math.ceil(math.log2(n_versions)))
    return (low, n_versions)


def format_duration(seconds: float) -> str:
    """Compact duration: '28s', '3m12s', '1h05m'."""
    s = int(round(seconds))
    if s < 60:
        return f"{s}s"
    m, s = divmod(s, 60)
    if m < 60:
        return f"{m}m{s:02d}s"
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m"


def format_eta(avg: float, remaining: int) -> str:
    """ETA string from an average probe duration; '?' when unknown."""
    if avg <= 0:
        return "?"
    return format_duration(avg * remaining)


def render_bar(done: int, total: int, width: int = 10) -> str:
    if total <= 0:
        filled = width
    else:
        filled = int(width * done / total)
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_progress.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add src/modelopt_ptq_transformers_doctor/progress.py tests/test_progress.py
git commit -m "feat: add progress estimate/format helpers"
```

---

### Task 2: `ProgressReporter` and `NullProgress`

**Files:**
- Modify: `src/modelopt_ptq_transformers_doctor/progress.py`
- Test: `tests/test_progress.py`

**Interfaces:**
- Consumes: `estimate_probes`, `format_duration`, `format_eta`, `render_bar` (Task 1).
- Produces:
  - `class NullProgress` with no-op methods `start(n_versions, n_symbols)`, `probe_start(version)`, `probe_done(version, status)`, `finish()`.
  - `class ProgressReporter(NullProgress)` with constructor
    `ProgressReporter(stream=None, clock=time.monotonic, bar_width=10)`
    (defaults `stream` to `sys.stderr`). Single-line TTY bar when
    `stream.isatty()`, else one line per probe.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_progress.py
from modelopt_ptq_transformers_doctor.progress import ProgressReporter, NullProgress


class FakeStream:
    def __init__(self, tty):
        self._tty = tty
        self.buf = []

    def isatty(self):
        return self._tty

    def write(self, s):
        self.buf.append(s)
        return len(s)

    def flush(self):
        pass

    @property
    def text(self):
        return "".join(self.buf)


class FakeClock:
    def __init__(self, times):
        self.times = list(times)
        self.i = 0

    def __call__(self):
        t = self.times[min(self.i, len(self.times) - 1)]
        self.i += 1
        return t


def test_null_progress_writes_nothing():
    # NullProgress methods must accept the same calls and do nothing.
    np = NullProgress()
    np.start(3, 2)
    np.probe_start("4.50.0")
    np.probe_done("4.50.0", "OK")
    np.finish()  # no exception, no output channel at all


def test_non_tty_logs_one_line_per_probe():
    stream = FakeStream(tty=False)
    # clock: start, then (probe_start, probe_done) pairs, then finish
    clock = FakeClock([0, 0, 5, 5, 30, 60])
    r = ProgressReporter(stream=stream, clock=clock)
    r.start(2, 1)
    r.probe_start("4.50.0")
    r.probe_done("4.50.0", "OK")
    r.probe_start("4.51.0")
    r.probe_done("4.51.0", "ENV_ERROR")
    r.finish()
    text = stream.text
    assert "search space: 2 versions" in text
    assert "est. binary-search probes:" in text
    assert "transformers==4.50.0" in text and "OK" in text
    assert "transformers==4.51.0" in text and "ENV_ERROR" in text
    assert "\r" not in text  # non-TTY never uses carriage returns
    assert "probed 2/2 versions" in text


def test_tty_draws_single_line_bar_with_eta():
    stream = FakeStream(tty=True)
    clock = FakeClock([0, 0, 10, 10, 20, 25])
    r = ProgressReporter(stream=stream, clock=clock)
    r.start(2, 1)
    r.probe_start("4.50.0")
    r.probe_done("4.50.0", "OK")
    text = stream.text
    assert "\r" in text                 # carriage-return redraw
    assert "transformers==4.50.0" in text
    assert "1/2" in text
    assert "ETA <=" in text
    assert "█" in text or "░" in text    # bar glyphs present
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_progress.py -v`
Expected: FAIL with `ImportError: cannot import name 'ProgressReporter'`.

- [ ] **Step 3: Write minimal implementation**

```python
# append to src/modelopt_ptq_transformers_doctor/progress.py

class NullProgress:
    """No-op reporter (used for --no-progress)."""

    def start(self, n_versions: int, n_symbols: int) -> None:  # noqa: D401
        pass

    def probe_start(self, version: str) -> None:
        pass

    def probe_done(self, version: str, status: str) -> None:
        pass

    def finish(self) -> None:
        pass


class ProgressReporter(NullProgress):
    """Live progress for a scan. Single-line bar on a TTY, line-per-probe otherwise."""

    def __init__(self, stream=None, clock=time.monotonic, bar_width: int = 10):
        self.stream = stream if stream is not None else sys.stderr
        self.clock = clock
        self.bar_width = bar_width
        self.total = 0
        self.done = 0
        self.total_time = 0.0
        self._t0 = None
        self._probe_t0 = None
        isatty = getattr(self.stream, "isatty", None)
        self._tty = bool(isatty()) if callable(isatty) else False

    def start(self, n_versions: int, n_symbols: int) -> None:
        self.total = n_versions
        self._t0 = self.clock()
        low, high = estimate_probes(n_versions, n_symbols)
        self._emit(
            f"search space: {n_versions} versions | "
            f"est. binary-search probes: ~{low}-{high} "
            f"(cached; usually near {low})\n"
        )

    def probe_start(self, version: str) -> None:
        self._probe_t0 = self.clock()
        if self._tty:
            self._redraw(version)

    def probe_done(self, version: str, status: str) -> None:
        dur = (self.clock() - self._probe_t0) if self._probe_t0 is not None else 0.0
        self.done += 1
        self.total_time += dur
        if self._tty:
            self._redraw(version)
        else:
            self._emit(
                f"[{self.done:>2}/{self.total}] transformers=={version}  "
                f"{status}  ({dur:.1f}s)\n"
            )

    def finish(self) -> None:
        elapsed = (self.clock() - self._t0) if self._t0 is not None else 0.0
        if self._tty:
            self._emit("\n")
        self._emit(f"probed {self.done}/{self.total} versions in "
                   f"{format_duration(elapsed)}\n")

    # --- helpers -------------------------------------------------------
    def _avg(self) -> float:
        return self.total_time / self.done if self.done else 0.0

    def _redraw(self, version: str) -> None:
        elapsed = (self.clock() - self._t0) if self._t0 is not None else 0.0
        remaining = max(self.total - self.done, 0)
        bar = render_bar(self.done, self.total, self.bar_width)
        line = (f"\r{bar} {self.done}/{self.total}  "
                f"transformers=={version}  "
                f"elapsed {format_duration(elapsed)}  "
                f"ETA <={format_eta(self._avg(), remaining)}")
        self._emit(line + "\x1b[K")  # clear to end-of-line for shrinking text

    def _emit(self, text: str) -> None:
        self.stream.write(text)
        self.stream.flush()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_progress.py -v`
Expected: PASS (all tests).

- [ ] **Step 5: Commit**

```bash
git add src/modelopt_ptq_transformers_doctor/progress.py tests/test_progress.py
git commit -m "feat: add ProgressReporter and NullProgress"
```

---

### Task 3: Wire reporter into `build_matrix`

**Files:**
- Modify: `src/modelopt_ptq_transformers_doctor/driver.py`
- Test: `tests/test_driver.py`

**Interfaces:**
- Consumes: `NullProgress`, `ProgressReporter` (Task 2).
- Produces: `build_matrix(records, versions, env_runner, reporter=None) -> dict`
  — fires `reporter.start` once, `probe_start`/`probe_done` once per **unique**
  version (cache miss), and `reporter.finish` once.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_driver.py

class SpyReporter:
    def __init__(self):
        self.started = None
        self.starts = []
        self.dones = []
        self.finished = False

    def start(self, n_versions, n_symbols):
        self.started = (n_versions, n_symbols)

    def probe_start(self, version):
        self.starts.append(version)

    def probe_done(self, version, status):
        self.dones.append((version, status))

    def finish(self):
        self.finished = True


def test_reporter_fires_once_per_unique_version():
    runner = FakeRunner(present_from=50)
    spy = SpyReporter()
    # two symbols share the per-version cache -> callbacks count unique installs
    build_matrix([_rec(), _rec()], VERSIONS, runner, reporter=spy)
    assert spy.started == (len(VERSIONS), 2)
    assert sorted(set(spy.starts)) == sorted(spy.starts)   # no version started twice
    assert len(spy.starts) == len(spy.dones) == runner.calls
    assert len(spy.starts) <= len(VERSIONS)
    assert spy.finished is True


def test_build_matrix_without_reporter_still_works():
    runner = FakeRunner(present_from=50)
    m = build_matrix([_rec()], VERSIONS, runner)  # no reporter kwarg
    assert m["symbols"]  # unchanged behaviour
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_driver.py::test_reporter_fires_once_per_unique_version -v`
Expected: FAIL with `TypeError: build_matrix() got an unexpected keyword argument 'reporter'`.

- [ ] **Step 3: Write minimal implementation**

Modify `src/modelopt_ptq_transformers_doctor/driver.py`. Add the import near the top:

```python
from .progress import NullProgress
```

Change the signature and the `probe` closure, and add `start`/`finish` calls:

```python
def build_matrix(records, versions, env_runner, reporter=None):
    reporter = reporter or NullProgress()
    static = [r for r in records if not r.dynamic]
    dynamic = [r for r in records if r.dynamic]
    record_dicts = [r.to_dict() for r in static]

    cache: dict[str, dict] = {}
    env_errors: dict[str, str] = {}

    reporter.start(len(versions), len(static))

    def probe(version: str) -> dict:
        if version not in cache:
            reporter.probe_start(version)
            res = env_runner.probe_version(version, record_dicts)
            cache[version] = res
            if res["status"] != "OK":
                env_errors[version] = res["status"]
            reporter.probe_done(version, res["status"])
        return cache[version]
```

Leave the rest of the function unchanged, and add `reporter.finish()` immediately before the final `return matrix`:

```python
    matrix["versions_probed"] = sorted(cache, key=Version)
    reporter.finish()
    return matrix
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_driver.py -v`
Expected: PASS (all existing tests + the two new ones).

- [ ] **Step 5: Commit**

```bash
git add src/modelopt_ptq_transformers_doctor/driver.py tests/test_driver.py
git commit -m "feat: fire progress callbacks per unique version in build_matrix"
```

---

### Task 4: `--no-progress` flag + CLI wiring

**Files:**
- Modify: `src/modelopt_ptq_transformers_doctor/cli.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `ProgressReporter`, `NullProgress` (Task 2); `build_matrix(..., reporter=)` (Task 3).
- Produces: `scan` subcommand accepts `--no-progress`; `_run_scan` builds a
  stderr `ProgressReporter` (or `NullProgress` when `--no-progress`) and passes
  it to `build_matrix`.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_cli.py
from modelopt_ptq_transformers_doctor import progress as progress_mod


def test_parser_accepts_no_progress_flag():
    p = cli.build_arg_parser()
    ns = p.parse_args(["scan", "--no-progress"])
    assert ns.no_progress is True
    ns2 = p.parse_args(["scan"])
    assert ns2.no_progress is False


def test_no_progress_uses_null_reporter(tmp_path, monkeypatch):
    rec = ContractRecord("transformers.models.x.modeling_x", "XAttn",
                         "f.py", 1, guarded=False, dynamic=False, role="quant")
    monkeypatch.setattr(cli, "installed_modelopt_root", lambda: "/x")
    monkeypatch.setattr(cli, "extract_contract", lambda root: [rec])
    monkeypatch.setattr(cli, "fetch_available_versions",
                        lambda: ["4.48.0", "4.49.0"])

    class FakeRunner:
        def __init__(self, *a, **k):
            pass

        def probe_version(self, version, records):
            return {"status": "OK", "installed": version,
                    "statuses": {f"{r['module_path']}:{r['symbol']}": "OK"
                                 for r in records}}

    monkeypatch.setattr(cli, "EnvRunner", FakeRunner)

    seen = {}

    def fake_build_matrix(records, versions, runner, reporter=None):
        seen["reporter"] = reporter
        return {"versions_probed": versions, "symbols": {}, "dynamic": [],
                "env_errors": {}}

    monkeypatch.setattr(cli, "build_matrix", fake_build_matrix)
    out = tmp_path / "report"
    rc = cli.main(["scan", "--min", "4.48.0", "--max", "4.49.0",
                   "--out", str(out), "--no-progress"])
    assert rc == 0
    assert isinstance(seen["reporter"], progress_mod.NullProgress)
    assert not isinstance(seen["reporter"], progress_mod.ProgressReporter)


def test_progress_on_by_default_uses_reporter(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "installed_modelopt_root", lambda: "/x")
    monkeypatch.setattr(cli, "extract_contract", lambda root: [])
    monkeypatch.setattr(cli, "fetch_available_versions", lambda: ["4.48.0"])
    monkeypatch.setattr(cli, "EnvRunner", lambda *a, **k: object())

    seen = {}

    def fake_build_matrix(records, versions, runner, reporter=None):
        seen["reporter"] = reporter
        return {"versions_probed": versions, "symbols": {}, "dynamic": [],
                "env_errors": {}}

    monkeypatch.setattr(cli, "build_matrix", fake_build_matrix)
    rc = cli.main(["scan", "--min", "4.48.0", "--max", "4.48.0",
                   "--out", str(tmp_path / "r")])
    assert rc == 0
    assert isinstance(seen["reporter"], progress_mod.ProgressReporter)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::test_parser_accepts_no_progress_flag -v`
Expected: FAIL with `AttributeError: 'Namespace' object has no attribute 'no_progress'`.

- [ ] **Step 3: Write minimal implementation**

In `src/modelopt_ptq_transformers_doctor/cli.py`, add the import near the top:

```python
from .progress import ProgressReporter, NullProgress
```

Add the flag in `build_arg_parser` (after the `--out` argument):

```python
    scan.add_argument("--no-progress", action="store_true",
                      help="disable the live progress bar / ETA output")
```

In `_run_scan`, replace the matrix-building line:

```python
    runner = EnvRunner(prober.__file__)
    reporter = NullProgress() if args.no_progress else ProgressReporter(stream=sys.stderr)
    matrix = build_matrix(records, versions, runner, reporter=reporter)
```

(`sys` is already imported in `cli.py`.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_cli.py -v`
Expected: PASS (existing tests + 3 new ones).

- [ ] **Step 5: Run the full suite**

Run: `pytest -q`
Expected: PASS (all tests across the project).

- [ ] **Step 6: Commit**

```bash
git add src/modelopt_ptq_transformers_doctor/cli.py tests/test_cli.py
git commit -m "feat: add --no-progress flag and wire scan progress reporter"
```

---

### Task 5: Document the flag in README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add `--no-progress` to the options table and note progress behaviour**

In the options table under "Usage", add a row:

```markdown
| `--no-progress` | disable the live progress bar / ETA (progress is on by default, printed to stderr) |
```

And add a short paragraph after the options table:

```markdown
During a scan, progress is printed to **stderr**: an up-front estimate of the
number of binary-search probes (`~LOW-N`), then a live bar showing the
`transformers` version under test, elapsed time, and an ETA. On a
non-interactive stream (pipe / CI) it logs one line per probed version instead.
Use `--no-progress` to silence it.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: document scan progress output and --no-progress"
```

---

## Self-Review

**Spec coverage:**
- Progress bar + ETA → Task 2 (`ProgressReporter` TTY path).
- Current version under test → Task 2 (`probe_start`/`_redraw` shows `transformers==X`).
- Up-front bisection estimate → Task 1 (`estimate_probes`) + Task 2 (`start` banner).
- Denominator N / ETA upper bound → Task 2 (`render_bar(done, total=N)`, `ETA <=`).
- Cache-miss-only callbacks (once per unique version) → Task 3 + its test.
- TTY vs non-TTY → Task 2 tests.
- `--no-progress`, default on, stderr → Task 4 + tests.
- Backward-compatible `build_matrix` → Task 3 (`reporter=None`) + `test_build_matrix_without_reporter_still_works`.
- No new dependencies → only `math`/`time`/`sys` used.
- README docs → Task 5.

**Placeholder scan:** none — every code/test step contains complete code.

**Type consistency:** `estimate_probes`/`format_duration`/`format_eta`/`render_bar` signatures match between Task 1 definition and Task 2 use; `ProgressReporter(stream=, clock=, bar_width=)` and the four reporter methods (`start`, `probe_start`, `probe_done`, `finish`) are consistent across Tasks 2–4; `build_matrix(..., reporter=None)` matches between Task 3 and Task 4.
