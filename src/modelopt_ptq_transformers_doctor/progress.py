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
