"""Orchestrate: contract × versions → compatibility matrix."""

from __future__ import annotations

from packaging.version import Version

from .version_bisect import compatible_ranges
from .models import OK, ContractRecord
from .progress import NullProgress


def _safe(fn, *args):
    """Call a progress-reporter callback; never let it raise into the scan."""
    try:
        fn(*args)
    except Exception:
        pass


def build_matrix(records: list[ContractRecord], versions: list[str], env_runner, reporter=None) -> dict:
    """Build a symbol × version compatibility matrix.

    ``versions_probed`` in the returned dict contains only the bisection-probed
    subset of *versions* (those actually installed and probed), not the full
    input list.
    """
    reporter = reporter or NullProgress()
    static = [r for r in records if not r.dynamic]
    dynamic = [r for r in records if r.dynamic]
    record_dicts = [r.to_dict() for r in static]

    cache: dict[str, dict] = {}
    env_errors: dict[str, str] = {}

    _safe(reporter.start, len(versions), len(static))

    def probe(version: str) -> dict:
        if version not in cache:
            _safe(reporter.probe_start, version)
            res = env_runner.probe_version(version, record_dicts)
            cache[version] = res
            if res["status"] != "OK":
                env_errors[version] = res["status"]
            _safe(reporter.probe_done, version, res["status"])
        return cache[version]

    matrix = {"versions_probed": [], "symbols": {}, "dynamic": [], "env_errors": env_errors}

    for r in static:
        def is_ok(version: str, key: str = r.key) -> bool:
            res = probe(version)
            if res["status"] != "OK":
                return False
            return res["statuses"].get(key) == OK

        matrix["symbols"][r.key] = {
            "file": r.file, "line": r.line, "guarded": r.guarded, "role": r.role,
            "compatible_ranges": compatible_ranges(versions, is_ok), "statuses": {},
        }

    # Second pass: cache is now complete, so every symbol's statuses covers the same probed versions.
    for r in static:
        info = matrix["symbols"][r.key]
        for v, res in cache.items():
            info["statuses"][v] = (
                res["statuses"].get(r.key, res["status"]) if res["status"] == OK else res["status"]
            )

    matrix["dynamic"] = [{"file": r.file, "line": r.line, "note": r.symbol or "runtime-discovered"}
                         for r in dynamic]
    matrix["versions_probed"] = sorted(cache, key=Version)
    _safe(reporter.finish)
    return matrix
