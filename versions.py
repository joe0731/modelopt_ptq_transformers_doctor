"""Discover and select transformers versions to probe."""

from __future__ import annotations

import json
import urllib.request

from packaging.version import InvalidVersion, Version

PYPI_URL = "https://pypi.org/pypi/transformers/json"


def fetch_available_versions(opener=urllib.request.urlopen, url=PYPI_URL) -> list[str]:
    """Return all stable (non-pre/dev-release) transformers versions from PyPI, sorted ascending."""
    with opener(url) as resp:
        data = json.load(resp)
    out = []
    for raw in data.get("releases", {}):
        try:
            ver = Version(raw)
        except InvalidVersion:
            continue
        if ver.is_prerelease or ver.is_devrelease:
            continue
        out.append(raw)
    return sorted(out, key=Version)


def select_versions(available, min_v: str | None, max_v: str | None) -> list[str]:
    """Return the subset of *available* versions within [min_v, max_v], sorted ascending."""
    lo = Version(min_v) if min_v else None
    hi = Version(max_v) if max_v else None
    chosen = []
    for raw in available:
        ver = Version(raw)
        if lo and ver < lo:
            continue
        if hi and ver > hi:
            continue
        chosen.append(raw)
    return sorted(chosen, key=Version)
