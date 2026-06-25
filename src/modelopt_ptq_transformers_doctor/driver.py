"""Orchestrate: contract × versions → compatibility matrix."""

from __future__ import annotations

from packaging.version import Version

from .version_bisect import (
    RISK_ADAPTIVE_STRATEGY,
    expand_probe_indices,
    initial_probe_indices,
    ranges_from_statuses,
)
from .models import OK, ContractRecord
from .progress import NullProgress


def _safe(fn, *args):
    """Call a progress-reporter callback; never let it raise into the scan."""
    try:
        fn(*args)
    except Exception:
        pass


def _signature_drift(sigs: dict) -> list | None:
    """Transition points [[version, fingerprint], ...] when >1 distinct
    fingerprints appear across the version->fingerprint map; else None."""
    transitions: list = []
    prev = object()
    for v in sorted(sigs, key=Version):
        fp = sigs[v]
        if fp != prev:
            transitions.append([v, fp])
            prev = fp
    return transitions if len(transitions) > 1 else None


def build_matrix(records: list[ContractRecord], versions: list[str], env_runner, reporter=None,
                 strategy: str = RISK_ADAPTIVE_STRATEGY, target_name: str | None = None) -> dict:
    """Build a symbol × version compatibility matrix.

    ``versions_probed`` in the returned dict contains only versions actually
    installed and probed, not necessarily the full input list.
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

    matrix = {"versions_probed": [], "symbols": {}, "dynamic": [], "env_errors": env_errors,
              "structural": {}, "known_probes": {}, "strategy": strategy}

    keys = [r.key for r in static]

    def status_vector(index: int) -> tuple:
        res = cache[versions[index]]
        if res["status"] != OK:
            return (res["status"],)
        return tuple(res.get("statuses", {}).get(key, "UNKNOWN") for key in keys)

    if static:
        pending = set(initial_probe_indices(versions, strategy=strategy, target_name=target_name))
        while pending:
            for index in sorted(pending):
                probe(versions[index])
            pending = set(expand_probe_indices(
                versions,
                probed_indices={versions.index(v) for v in cache},
                status_at_index=status_vector,
                strategy=strategy,
                target_name=target_name,
            ))

    for r in static:
        statuses: dict[str, str] = {}
        ok_by_version: dict[str, bool] = {}
        for v, res in cache.items():
            status = res["statuses"].get(r.key, res["status"]) if res["status"] == OK else res["status"]
            statuses[v] = status
            ok_by_version[v] = status == OK
        matrix["symbols"][r.key] = {
            "file": r.file, "line": r.line, "guarded": r.guarded, "role": r.role,
            "compatible_ranges": ranges_from_statuses(versions, ok_by_version),
            "statuses": statuses,
        }

    # Known historical seam probes returned by the prober (transformers target only).
    for v, res in cache.items():
        if res["status"] != OK:
            continue
        for probe in res.get("known_probes", []) or []:
            pid = probe.get("id")
            if not pid:
                continue
            entry = matrix["known_probes"].setdefault(
                pid, {
                    "module_path": probe.get("module_path"),
                    "symbol": probe.get("symbol"),
                    "note": probe.get("note", ""),
                    "statuses": {},
                }
            )
            entry["statuses"][v] = probe.get("status", "UNKNOWN")

    # Structural source checks returned by the prober (transformers target only).
    for v, res in cache.items():
        if res["status"] != OK:
            continue
        for check in res.get("structural", []) or []:
            cid = check.get("id")
            if not cid:
                continue
            entry = matrix["structural"].setdefault(
                cid, {"file": check.get("file"), "statuses": {}, "details": {}}
            )
            entry["statuses"][v] = check.get("status", "UNKNOWN")
            if check.get("status") != OK:
                entry["details"][v] = {
                    "missing": check.get("missing", []),
                    "reason": check.get("reason", ""),
                }

    # Signatures pass: collect signatures from OK versions and detect drift.
    for r in static:
        info = matrix["symbols"][r.key]
        sigs = {}
        for v, res in cache.items():
            if res["status"] == OK:
                fp = res.get("signatures", {}).get(r.key)
                if fp is not None:
                    sigs[v] = fp
        info["signatures"] = sigs
        info["signature_drift"] = _signature_drift(sigs)

    matrix["dynamic"] = [{"file": r.file, "line": r.line, "note": r.symbol or "runtime-discovered"}
                         for r in dynamic]
    matrix["versions_probed"] = sorted(cache, key=Version)
    _safe(reporter.finish)
    return matrix
