# Design: `doctor scan` progress bar, ETA, and bisection estimate

Date: 2026-06-23

## Problem

`doctor scan --min … --max … --out …` probes a range of `transformers`
versions by creating a throwaway `uv` venv per version, installing
`transformers` + `torch`, and importing the modelopt dependency symbols. Each
probe takes tens of seconds, and a scan can touch many versions. Today the
command prints nothing until the report is written, so the user has no idea:

- how far along the scan is,
- roughly how long it will take,
- which `transformers` version is being verified right now,
- how many binary-search probes to expect.

## Goal

Give live, honest progress feedback for a scan:

1. A progress bar with elapsed time and an ETA.
2. The `transformers` version currently being verified.
3. An up-front estimate of the number of binary-search probes.

## Key constraint: the probe count is data-dependent

The expensive unit is `EnvRunner.probe_version()` (venv + install + import).
`build_matrix` **caches probes per version**, and the per-symbol binary search
(`compatible_ranges`) short-circuits, so the exact number of installs is not
known before the scan runs. It is bounded:

- **Upper bound** = `N` (the candidate count) — a version is never installed
  twice because of the cache.
- **Lower bound** ≈ one symbol's bisection cost: an anchor sample of up to 5
  points plus two edge binary searches.

Decision (confirmed with user): the progress bar denominator is **N** (the
worst case); the bar may legitimately finish early. An estimated range is
printed once at the start.

## Architecture

### New module `progress.py` (standard library only — no new dependencies)

Owns all progress I/O, keeping `driver.py` free of presentation logic.

- `estimate_probes(n_versions, n_symbols) -> (low, high)` — pure function.
  - `high = n_versions`
  - `low = min(n_versions, 5 + 2 * ceil(log2(n_versions)))` for
    `n_versions >= 1` (define `low = n_versions` when `n_versions <= 1`).
  - Typical runs land near `low` because most symbols share the same
    compatible window and reuse the cache. `n_symbols` is accepted for the
    banner text / future tuning but does not change the bounds.

- `ProgressReporter(stream=sys.stderr, clock=time.monotonic)`:
  - `start(n_versions, n_symbols)` — prints the banner:
    `search space: N versions | est. binary-search probes: ~LOW–N (cached; usually near LOW)`
  - `probe_start(version)` — records the probe start time and the current
    version; fired only on a **cache miss** (a real install).
  - `probe_done(version, status)` — increments the done count, updates the
    rolling average probe duration, redraws the bar.
  - `finish()` — emits a trailing newline and a one-line summary:
    `probed K/N versions in Xm Ys`.

- TTY behaviour (`stream.isatty()` is true): a single-line carriage-return
  bar, e.g.
  `██████░░░░ 7/12  transformers==4.50.0  elapsed 3m12s  ETA <=1m04s`
  - ETA = `avg_probe_time * (N - done)`, displayed with a `<=` marker because
    the scan may finish before reaching `N` (honest upper bound).
- Non-TTY behaviour (piped, redirected, CI): one line per probe, e.g.
  `[ 7/12] transformers==4.50.0  OK  (28.4s)`.

- `NullProgress` — a no-op subclass used for `--no-progress`, so the driver
  calls reporter methods unconditionally (no branching in the hot path).

Formatting helpers (`format_duration`, `format_eta`, bar rendering) are pure
functions so they can be unit-tested without a real clock or stream.

### Driver integration (`driver.py`)

`build_matrix(records, versions, env_runner, reporter=None)` — **backward
compatible**; when `reporter is None` it uses a `NullProgress` instance, so
existing `build_matrix(records, versions, runner)` call sites are unchanged.

- `reporter.start(len(versions), len(static))` is called once before probing.
- The `probe()` closure wraps the **cache-miss** path:
  `probe_start(version)` → `env_runner.probe_version(...)` → `probe_done(version, status)`.
  Cache hits do not fire callbacks, so the displayed count equals real install
  cost (once per unique version, never per symbol).
- `reporter.finish()` is called after the matrix is built.

### CLI (`cli.py`)

- Add `--no-progress` to the `scan` subparser. Progress is **on by default**.
- In `_run_scan`, construct the reporter against `sys.stderr`:
  - `--no-progress` → `NullProgress`
  - otherwise → `ProgressReporter(stream=sys.stderr)`
- Pass the reporter to `build_matrix`. Progress goes to **stderr**; the
  `wrote …` lines on stdout and the `--out` report files are untouched
  (pipe-safe).

## Error handling

- A failed probe (`ENV_ERROR` / `PROBE_ERROR`) still calls `probe_done` with
  that status: the bar advances and the non-TTY log shows the status, so
  failures are visible rather than silent.
- The reporter never raises into the scan — formatting is total (handles
  `done == 0`, `avg == 0`, `n_versions <= 1`).

## Testing

- `progress.py`
  - `estimate_probes` bounds across `n_versions` in `{0, 1, 2, 10, 130}`;
    assert `low <= high == n_versions` and the `<= 1` edge case.
  - `format_duration` / `format_eta` for representative seconds values.
  - bar string rendering for a known `(done, total, width)`.
  - TTY vs non-TTY dispatch via a fake stream with a settable `isatty()` and
    an injected fake clock; assert single-line redraw vs one-line-per-probe.
- `driver.py`
  - spy reporter + fake env_runner: assert callbacks fire **once per unique
    version** (cache miss only), not once per symbol.
- `cli.py`
  - `--no-progress` ⇒ `NullProgress` and nothing written to the stderr stream.

## Out of scope (YAGNI)

- Third-party progress libraries (`rich`, `tqdm`).
- Per-symbol or per-install-step (venv/install/import) sub-progress.
- Parallel probing.
- Persisting/streaming progress to the JSON report.
