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
