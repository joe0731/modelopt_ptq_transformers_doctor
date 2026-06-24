import io
import json
from contextlib import contextmanager

from modelopt_ptq_transformers_doctor.versions import (
    fetch_available_versions, select_versions,
)


@contextmanager
def _fake_opener(payload):
    yield io.StringIO(json.dumps(payload))


def test_fetch_filters_prereleases_and_sorts():
    payload = {"releases": {"4.50.0": [], "4.49.0": [], "4.51.0rc1": [], "bogus": []}}
    out = fetch_available_versions(opener=lambda url, timeout=None: _fake_opener(payload))
    assert out == ["4.49.0", "4.50.0"]


def test_select_versions_inclusive_bounds():
    avail = ["4.48.0", "4.49.0", "4.50.0", "4.51.0"]
    assert select_versions(avail, "4.49.0", "4.50.0") == ["4.49.0", "4.50.0"]


def test_select_versions_no_bounds_returns_all_sorted():
    avail = ["4.50.0", "4.48.0"]
    assert select_versions(avail, None, None) == ["4.48.0", "4.50.0"]


def test_fetch_uses_pkg_in_url():
    seen = {}
    def fake_opener(url, timeout=0):
        seen["url"] = url
        import io, json
        return io.BytesIO(json.dumps({"releases": {"1.0.0": []}}).encode())
    from modelopt_ptq_transformers_doctor.versions import fetch_available_versions
    out = fetch_available_versions(pkg="torch", opener=fake_opener)
    assert "torch" in seen["url"] and out == ["1.0.0"]
