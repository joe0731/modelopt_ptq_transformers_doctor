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


from modelopt_ptq_transformers_doctor.progress import ProgressReporter, NullProgress


class FakeStream:
    def __init__(self, tty):
        self._tty = tty
        self.buf = []

    def isatty(self):
        return self._tty

    def write(self, s):
        self.buf.append(s)
        return len(s)

    def flush(self):
        pass

    @property
    def text(self):
        return "".join(self.buf)


class FakeClock:
    def __init__(self, times):
        self.times = list(times)
        self.i = 0

    def __call__(self):
        t = self.times[min(self.i, len(self.times) - 1)]
        self.i += 1
        return t


def test_null_progress_writes_nothing():
    # NullProgress methods must accept the same calls and do nothing.
    np = NullProgress()
    np.start(3, 2)
    np.probe_start("4.50.0")
    np.probe_done("4.50.0", "OK")
    np.finish()  # no exception, no output channel at all


def test_non_tty_logs_one_line_per_probe():
    stream = FakeStream(tty=False)
    # clock: start, then (probe_start, probe_done) pairs, then finish
    clock = FakeClock([0, 0, 5, 5, 30, 60])
    r = ProgressReporter(stream=stream, clock=clock)
    r.start(2, 1)
    r.probe_start("4.50.0")
    r.probe_done("4.50.0", "OK")
    r.probe_start("4.51.0")
    r.probe_done("4.51.0", "ENV_ERROR")
    r.finish()
    text = stream.text
    assert "search space: 2 versions" in text
    assert "est. binary-search probes:" in text
    assert "transformers==4.50.0" in text and "OK" in text
    assert "transformers==4.51.0" in text and "ENV_ERROR" in text
    assert "\r" not in text  # non-TTY never uses carriage returns
    assert "probed 2/2 versions" in text


def test_tty_draws_single_line_bar_with_eta():
    stream = FakeStream(tty=True)
    clock = FakeClock([0, 0, 10, 10, 20, 25])
    r = ProgressReporter(stream=stream, clock=clock)
    r.start(2, 1)
    r.probe_start("4.50.0")
    r.probe_done("4.50.0", "OK")
    text = stream.text
    assert "\r" in text                 # carriage-return redraw
    assert "transformers==4.50.0" in text
    assert "1/2" in text
    assert "ETA <=" in text
    assert "█" in text or "░" in text    # bar glyphs present
