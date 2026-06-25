"""Choose dependency versions to probe and derive validated compatible ranges.

``full`` validates every selected release. ``risk-adaptive`` keeps the binary
search spirit for speed: start with endpoints/quartiles and feature-version
edges, fully cover known-risk feature versions, then recursively fill gaps only
where observed version-wide status vectors change. Returned ranges are always
built from directly probed versions; unprobed gaps split ranges instead of being
painted compatible.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence

from packaging.version import InvalidVersion, Version

FULL_STRATEGY = "full"
RISK_ADAPTIVE_STRATEGY = "risk-adaptive"
SCAN_STRATEGIES = (RISK_ADAPTIVE_STRATEGY, FULL_STRATEGY)

_RISK_FEATURES: dict[str, set[tuple[int, int]]] = {
    "transformers": {(4, 56), (4, 57), (5, 0), (5, 10)},
    "torch": {(2, 1)},
    "vllm": {(0, 7), (0, 8), (0, 9), (0, 10), (0, 11)},
}


def _first_true(lo: int, hi: int, pred: Callable[[int], bool]) -> int:
    """First index in [lo, hi] where pred(i) is True, assuming pred(i) is
    monotonic False...True. Used only as a best-effort ordering seed.
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


def ranges_from_statuses(versions: Sequence[str], ok_by_version: Mapping[str, bool]) -> list[tuple[str, str]]:
    """Build ranges from directly known OK statuses.

    Missing versions are treated as unprobed gaps, so a range never spans over an
    untested release.
    """
    ok_idx = [i for i, version in enumerate(versions) if ok_by_version.get(version) is True]
    return _contiguous_ranges(versions, ok_idx) if ok_idx else []


def _seed_bisection(n: int, ok: Callable[[int], bool]) -> None:
    sample = sorted({0, n - 1, n // 2, n // 4, (3 * n) // 4})
    anchor = next((i for i in sample if ok(i)), None)
    if anchor is None:
        return
    _first_true(0, anchor, ok)
    if anchor < n - 1:
        _first_true(anchor + 1, n - 1, lambda i: not ok(i))


def compatible_ranges(versions: Sequence[str],
                      is_ok: Callable[[str], bool],
                      *,
                      strategy: str = FULL_STRATEGY,
                      target_name: str | None = None) -> list[tuple[str, str]]:
    """Compatibility ranges for standalone callers.

    The default remains full validation for backward compatibility. Driver-level
    scans use ``initial_probe_indices`` / ``expand_probe_indices`` so all symbols
    share one probe cache.
    """
    n = len(versions)
    if n == 0:
        return []
    if strategy not in SCAN_STRATEGIES:
        raise ValueError(f"unknown scan strategy: {strategy}")

    cache: dict[int, bool] = {}

    def ok(i: int) -> bool:
        if i not in cache:
            cache[i] = is_ok(versions[i])
        return cache[i]

    if strategy == FULL_STRATEGY:
        _seed_bisection(n, ok)
        statuses = {versions[i]: ok(i) for i in range(n)}
        return ranges_from_statuses(versions, statuses)

    pending = set(initial_probe_indices(versions, strategy=strategy, target_name=target_name))
    while pending:
        for i in sorted(pending):
            ok(i)
        pending = set(expand_probe_indices(
            versions,
            probed_indices=set(cache),
            status_at_index=lambda i: ("OK",) if ok(i) else ("NOT_OK",),
            strategy=strategy,
            target_name=target_name,
        ))
    return ranges_from_statuses(versions, {versions[i]: v for i, v in cache.items()})


def initial_probe_indices(versions: Sequence[str], *, strategy: str,
                          target_name: str | None = None) -> list[int]:
    """Initial version indices for a scan strategy."""
    if strategy not in SCAN_STRATEGIES:
        raise ValueError(f"unknown scan strategy: {strategy}")
    n = len(versions)
    if n == 0:
        return []
    if strategy == FULL_STRATEGY:
        return list(range(n))

    selected = {0, n - 1, n // 2, n // 4, (3 * n) // 4}
    groups: dict[tuple[int, int] | tuple[str, str], list[int]] = {}
    for i, version in enumerate(versions):
        groups.setdefault(_feature_key(version), []).append(i)
    for indices in groups.values():
        selected.add(indices[0])
        selected.add(indices[-1])

    latest_feature = _feature_key(versions[-1])
    for feature, indices in groups.items():
        if _is_high_risk_feature(feature, target_name, latest_feature):
            selected.update(indices)
    return sorted(i for i in selected if 0 <= i < n)


def expand_probe_indices(versions: Sequence[str], *, probed_indices: set[int],
                         status_at_index: Callable[[int], tuple], strategy: str,
                         target_name: str | None = None) -> list[int]:
    """Return additional indices to probe after observing current results."""
    if strategy == FULL_STRATEGY:
        return [i for i in range(len(versions)) if i not in probed_indices]
    if strategy != RISK_ADAPTIVE_STRATEGY:
        raise ValueError(f"unknown scan strategy: {strategy}")

    n = len(versions)
    extra: set[int] = set()
    for i in sorted(probed_indices):
        state = status_at_index(i)
        if state and state[0] in {"ENV_ERROR", "PROBE_ERROR"}:
            if i > 0:
                extra.add(i - 1)
            if i + 1 < n:
                extra.add(i + 1)

    ordered = sorted(probed_indices)
    for left, right in zip(ordered, ordered[1:]):
        if right - left <= 1:
            continue
        if status_at_index(left) != status_at_index(right):
            extra.add((left + right) // 2)
    return sorted(i for i in extra if i not in probed_indices)


def _feature_key(version: str) -> tuple[int, int] | tuple[str, str]:
    try:
        release = Version(version).release
    except InvalidVersion:
        parts = version.split(".")
        return (parts[0], parts[1] if len(parts) > 1 else "0")
    major = release[0] if release else 0
    minor = release[1] if len(release) > 1 else 0
    return (major, minor)


def _is_high_risk_feature(feature: tuple[int, int] | tuple[str, str],
                          target_name: str | None,
                          latest_feature: tuple[int, int] | tuple[str, str]) -> bool:
    # ``latest_feature`` is accepted for future policy tuning; do not mark it
    # risky by default, because a one-minor search space would otherwise become
    # a full scan and defeat the quick strategy.
    _ = latest_feature
    if not isinstance(feature[0], int) or not isinstance(feature[1], int):
        return False
    return feature in _RISK_FEATURES.get(target_name or "", set())
