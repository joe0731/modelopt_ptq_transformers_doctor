import json, sys, importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "report"))
rc = importlib.import_module("render_combined")


def _matrix(probed, key):
    return {"versions_probed": probed, "symbols": {key: {"file": "f.py", "line": 1,
            "guarded": False, "role": "quant", "compatible_ranges": [[probed[0], probed[-1]]],
            "statuses": {v: "OK" for v in probed}, "signatures": {}, "signature_drift": None}},
            "dynamic": [], "env_errors": {}}


def test_combined_has_section_per_target(tmp_path):
    (tmp_path / "torch").mkdir(); (tmp_path / "accelerate").mkdir()
    (tmp_path / "torch" / "matrix.json").write_text(json.dumps(_matrix(["2.6.0"], "torch:Tensor")))
    (tmp_path / "accelerate" / "matrix.json").write_text(json.dumps(_matrix(["1.10.0"], "accelerate:Accelerator")))
    rc.build_combined(str(tmp_path), "0.44.0", "2026-06-24")
    html = (tmp_path / "index.html").read_text()
    assert "torch" in html and "accelerate" in html and "Overview" in html
    nb = json.loads((tmp_path / "index.ipynb").read_text())
    assert sum(1 for c in nb["cells"] if c["cell_type"] == "code") == 0
