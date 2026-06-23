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
    out = fetch_available_versions(opener=lambda url: _fake_opener(payload))
    assert out == ["4.49.0", "4.50.0"]


def test_select_versions_inclusive_bounds():
    avail = ["4.48.0", "4.49.0", "4.50.0", "4.51.0"]
    assert select_versions(avail, "4.49.0", "4.50.0") == ["4.49.0", "4.50.0"]


def test_select_versions_no_bounds_returns_all_sorted():
    avail = ["4.50.0", "4.48.0"]
    assert select_versions(avail, None, None) == ["4.48.0", "4.50.0"]
