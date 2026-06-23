from modelopt_ptq_transformers_doctor.bisect import compatible_ranges

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
