"""Find validated compatible version ranges for one dependency symbol.

The scan still starts with a small binary-search seed so early progress reaches
likely edges quickly, but the returned ranges are built only from versions that
were actually probed.  This avoids treating compatibility as monotonic: a
breaking release can be followed by a fixed release, and the result must split
that into two ranges instead of collapsing it into one envelope.
"""

from __future__ import annotations

from typing import Callable, Sequence


def _first_true(lo: int, hi: int, pred: Callable[[int], bool]) -> int:
    """First index in [lo, hi] where pred(i) is True, assuming pred is
    monotonic False...True on the range. Returns hi+1 if always False.

    Used only as a best-effort seed. The final result is validated by probing
    every selected version and does not rely on this monotonic assumption.
    """
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


def _seed_bisection(n: int, ok: Callable[[int], bool]) -> None:
    """Warm the probe cache with representative points and tentative edges.

    This keeps the old left/right bisection behaviour as a cheap ordering hint,
    but callers must ignore the inferred edge values: compatibility is not
    guaranteed to be monotonic across upstream releases.
    """
    sample = sorted({0, n - 1, n // 2, n // 4, (3 * n) // 4})
    anchor = next((i for i in sample if ok(i)), None)
    if anchor is None:
        return
    _first_true(0, anchor, ok)
    if anchor < n - 1:
        _first_true(anchor + 1, n - 1, lambda i: not ok(i))


def compatible_ranges(versions: Sequence[str],
                      is_ok: Callable[[str], bool]) -> list[tuple[str, str]]:
    n = len(versions)
    if n == 0:
        return []

    cache: dict[int, bool] = {}

    def ok(i: int) -> bool:
        if i not in cache:
            cache[i] = is_ok(versions[i])
        return cache[i]

    _seed_bisection(n, ok)

    ok_idx = [i for i in range(n) if ok(i)]
    return _contiguous_ranges(versions, ok_idx) if ok_idx else []
