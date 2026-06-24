import importlib, sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "report"))
rc = importlib.import_module("render_compat")


def test_fetch_full_range_uses_pkg_in_url(monkeypatch):
    seen = {}
    class _Resp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self): return b'{"releases": {}}'
    def fake_urlopen(url, timeout=0):
        seen["url"] = url; return _Resp()
    monkeypatch.setattr(rc.urllib.request, "urlopen", fake_urlopen)
    rc.fetch_full_range("2.0.0", "2.6.0", ["2.0.0"], pkg="torch")
    assert "/torch/" in seen["url"]


def test_build_html_labels_target():
    m = {"target": "torch", "pypi": "torch", "versions_probed": ["2.6.0"],
         "symbols": {}, "dynamic": [], "env_errors": {}}
    html = rc.build_html(m, "0.46.0", "2026-06-24", ["2.6.0"])
    assert "torch" in html and "↔ torch" in html
