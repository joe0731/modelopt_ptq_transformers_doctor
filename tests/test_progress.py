# tests/test_progress.py
import math
from modelopt_ptq_transformers_doctor import progress


def test_estimate_probes_bounds():
    assert progress.estimate_probes(0, 3) == (0, 0)
    assert progress.estimate_probes(1, 3) == (1, 1)
    # high is always n_versions; low never exceeds high
    for n in (2, 10, 130):
        low, high = progress.estimate_probes(n, 5)
        assert high == n
        assert 1 <= low <= n
        assert low == min(n, 5 + 2 * math.ceil(math.log2(n)))


def test_format_duration():
    assert progress.format_duration(0) == "0s"
    assert progress.format_duration(28) == "28s"
    assert progress.format_duration(192) == "3m12s"
    assert progress.format_duration(64) == "1m04s"


def test_format_eta_unknown_when_no_average():
    assert progress.format_eta(0.0, 5) == "?"
    assert progress.format_eta(30.0, 0) == "0s"
    assert progress.format_eta(30.0, 2) == "1m00s"


def test_render_bar():
    assert progress.render_bar(0, 10) == "░" * 10
    assert progress.render_bar(10, 10) == "█" * 10
    assert progress.render_bar(5, 10) == "█████░░░░░"
    # total <= 0 renders a full bar (avoids div-by-zero)
    assert progress.render_bar(0, 0) == "█" * 10
