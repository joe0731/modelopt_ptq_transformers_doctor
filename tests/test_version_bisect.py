from modelopt_ptq_transformers_doctor.version_bisect import (
    compatible_ranges,
    ranges_from_statuses,
)

V = [f"4.{m}" for m in range(40, 60)]  # "4.40".."4.59", 20 versions


def _ok_set(ok_versions):
    s = set(ok_versions)
    return lambda v: v in s


def test_all_ok_returns_full_range():
    assert compatible_ranges(V, lambda v: True) == [(V[0], V[-1])]


def test_none_ok_returns_empty():
    assert compatible_ranges(V, lambda v: False) == []


def test_monotonic_added_at_451_returns_open_ended_window():
    ok = [v for v in V if int(v.split(".")[1]) >= 51]
    assert compatible_ranges(V, _ok_set(ok)) == [("4.51", "4.59")]


def test_contiguous_window_added_then_moved():
    ok = [v for v in V if 51 <= int(v.split(".")[1]) <= 55]
    assert compatible_ranges(V, _ok_set(ok)) == [("4.51", "4.55")]


def test_empty_versions_returns_empty():
    assert compatible_ranges([], lambda v: True) == []


def test_two_disjoint_windows_via_fallback():
    # Anchor sample (ends/mid/quartiles) misses both windows -> full-scan fallback.
    ok = {"4.41", "4.58"}
    assert compatible_ranges(V, lambda v: v in ok) == [("4.41", "4.41"), ("4.58", "4.58")]

def test_break_then_fix_after_ok_anchor_is_split():
    versions = ["5.8", "5.9", "5.10", "5.11", "5.12"]
    ok = {"5.8", "5.9", "5.11", "5.12"}
    assert compatible_ranges(versions, lambda v: v in ok) == [
        ("5.8", "5.9"),
        ("5.11", "5.12"),
    ]


def test_break_inside_candidate_window_is_validated():
    versions = [f"5.{m}" for m in range(8, 17)]
    ok = set(versions) - {"5.13"}
    assert compatible_ranges(versions, lambda v: v in ok) == [
        ("5.8", "5.12"),
        ("5.14", "5.16"),
    ]


def test_safety_validation_probes_every_selected_version():
    calls = []
    versions = ["5.8", "5.9", "5.10", "5.11", "5.12"]
    ok = {"5.8", "5.9", "5.11", "5.12"}

    def is_ok(version):
        calls.append(version)
        return version in ok

    compatible_ranges(versions, is_ok)
    assert set(calls) == set(versions)

def test_ranges_from_statuses_splits_unprobed_gaps():
    versions = ["5.8", "5.9", "5.10", "5.11", "5.12"]
    statuses = {"5.8": True, "5.9": True, "5.11": True, "5.12": True}
    assert ranges_from_statuses(versions, statuses) == [("5.8", "5.9"), ("5.11", "5.12")]
