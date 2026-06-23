import json
from pathlib import Path

from modelopt_ptq_transformers_doctor.report import render_markdown, write_report

MATRIX = {
    "versions_probed": ["4.49.0", "4.50.0", "4.51.0"],
    "symbols": {
        "transformers.models.x.modeling_x:XAttn": {
            "file": "hf.py", "line": 12, "guarded": True, "role": "quant",
            "compatible_ranges": [("4.50.0", "4.51.0")],
            "statuses": {"4.49.0": "MISSING_SYMBOL", "4.50.0": "OK", "4.51.0": "OK"},
        },
    },
    "dynamic": [{"file": "hf.py", "line": 99, "note": "mod_type"}],
    "env_errors": {},
}


def test_markdown_contains_symbol_versions_and_range():
    md = render_markdown(MATRIX)
    assert "XAttn" in md
    assert "4.50.0 – 4.51.0" in md
    assert "mod_type" in md  # dynamic section
    assert "| 4.49.0 |" in md or "4.49.0" in md


def test_write_report_creates_both_artifacts(tmp_path):
    json_path, md_path = write_report(MATRIX, str(tmp_path / "out"))
    assert Path(json_path).name == "matrix.json"
    assert Path(md_path).name == "REPORT.md"
    assert json.loads(Path(json_path).read_text())["versions_probed"] == MATRIX["versions_probed"]
    assert "XAttn" in Path(md_path).read_text()


def test_compatible_ranges_round_trip_as_lists(tmp_path):
    json_path, _ = write_report(MATRIX, str(tmp_path / "out"))
    loaded = json.loads(Path(json_path).read_text(encoding="utf-8"))
    ranges = loaded["symbols"]["transformers.models.x.modeling_x:XAttn"]["compatible_ranges"]
    # JSON has no tuple type: ranges come back as lists of [lo, hi] with values preserved.
    assert ranges == [["4.50.0", "4.51.0"]]
