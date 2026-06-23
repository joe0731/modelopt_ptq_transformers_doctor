"""Binary-search a symbol's contiguous compatible version window."""

from __future__ import annotations

from typing import Callable, Sequence


def _first_true(lo: int, hi: int, pred: Callable[[int], bool]) -> int:
    """First index in [lo, hi] where pred(i) is True, assuming pred is
    monotonic False...True on the range. Returns hi+1 if always False."""
    res = hi + 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if pred(mid):
            res = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return res


def _contiguous_ranges(versions: Sequence[str], ok_idx: list[int]) -> list[tuple[str, str]]:
    ranges: list[tuple[str, str]] = []
    start = prev = ok_idx[0]
    for i in ok_idx[1:]:
        if i == prev + 1:
            prev = i
        else:
            ranges.append((versions[start], versions[prev]))
            start = prev = i
    ranges.append((versions[start], versions[prev]))
    return ranges


def compatible_ranges(versions: Sequence[str],
                      is_ok: Callable[[str], bool]) -> list[tuple[str, str]]:
    n = len(versions)
    if n == 0:
        return []

    def ok(i: int) -> bool:
        return is_ok(versions[i])

    sample = sorted({0, n - 1, n // 2, n // 4, (3 * n) // 4})
    anchor = next((i for i in sample if ok(i)), None)

    if anchor is None:
        ok_idx = [i for i in range(n) if ok(i)]
        return _contiguous_ranges(versions, ok_idx) if ok_idx else []

    # NOTE: This assumes a single contiguous OK window.  Non-contiguous OK-sets
    # are collapsed to their outer envelope; the no-anchor branch above falls
    # back to a full scan instead.

    # Left edge: first True in [0, anchor] (monotonic False...True up to anchor).
    left = _first_true(0, anchor, ok)
    # Right edge: first False *after* anchor; window ends just before it.
    # Guard: if anchor is already the last index the window extends to the end.
    if anchor == n - 1:
        right = n - 1
    else:
        first_false = _first_true(anchor + 1, n - 1, lambda i: not ok(i))
        right = first_false - 1
    return [(versions[left], versions[right])]
