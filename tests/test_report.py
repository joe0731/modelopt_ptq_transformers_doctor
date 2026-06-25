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


def test_markdown_contains_authoritative_note():
    md = render_markdown(MATRIX)
    assert "compatible" in md and "authoritative" in md


def test_markdown_title_uses_target_label():
    matrix = dict(MATRIX, target="torch")
    md = render_markdown(matrix)
    assert md.startswith("# modelopt PTQ ↔ torch compatibility matrix")


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


DRIFT_MATRIX = {
    "versions_probed": ["4.48.0", "4.50.0"],
    "symbols": {
        "transformers.m:Foo": {
            "file": "hf.py", "line": 1, "guarded": False, "role": "quant",
            "compatible_ranges": [("4.48.0", "4.50.0")],
            "statuses": {"4.48.0": "OK", "4.50.0": "OK"},
            "signatures": {"4.48.0": "(a)", "4.50.0": "(a, b)"},
            "signature_drift": [["4.48.0", "(a)"], ["4.50.0", "(a, b)"]],
        },
    },
    "dynamic": [],
    "env_errors": {},
}


def test_drift_marker_and_section_render():
    md = render_markdown(DRIFT_MATRIX)
    assert "⚇" in md
    assert "## Signature changes" in md
    assert "4.48.0 `(a)`" in md and "4.50.0 `(a, b)`" in md
    # Verify marker appears on the drifting symbol's row, not just the legend
    symbol_line = next(line for line in md.split("\n") if "transformers.m:Foo" in line)
    assert "⚇" in symbol_line


def test_no_drift_marker_when_absent():
    md = render_markdown(MATRIX)  # MATRIX symbol has no signature_drift
    # Check that the marker is not on the symbol row (not in the table)
    lines = md.split("\n")
    for line in lines:
        if "XAttn" in line:
            assert "⚇" not in line, "Marker should not appear in symbol row"
    assert "## Signature changes" not in md



def test_markdown_renders_structural_checks():
    matrix = dict(MATRIX)
    matrix["target"] = "transformers"
    matrix["structural"] = {
        "attention-interface": {
            "statuses": {"4.48.0": "OK", "4.49.0": "MISSING"},
            "details": {"4.49.0": {"missing": ["ALL_ATTENTION_FUNCTIONS"], "reason": "missing"}},
        }
    }
    md = render_markdown(matrix)
    assert "Transformers structural checks" in md
    assert "attention-interface" in md
    assert "ALL_ATTENTION_FUNCTIONS" in md



def test_markdown_renders_known_probe_checks():
    matrix = dict(MATRIX)
    matrix["target"] = "transformers"
    matrix["known_probes"] = {
        "legacy-modeling-utils-conv1d": {
            "module_path": "transformers.modeling_utils",
            "symbol": "Conv1D",
            "note": "legacy HF plugin path",
            "statuses": {"4.48.0": "MISSING_SYMBOL", "4.49.0": "OK"},
        }
    }
    md = render_markdown(matrix)
    assert "Known upstream seam probes" in md
    assert "legacy-modeling-utils-conv1d" in md
    assert "transformers.modeling_utils.Conv1D" in md

def test_markdown_includes_affected_models_column():
    matrix = {
        "versions_probed": ["5.9.0"],
        "symbols": {
            "transformers.models.t5.modeling_t5:T5Attention": {
                "file": "hf.py", "line": 1, "guarded": False, "role": "quant",
                "compatible_ranges": [("5.9.0", "5.9.0")],
                "statuses": {"5.9.0": "OK"},
            },
            "transformers.modeling_utils:PreTrainedModel": {
                "file": "hf.py", "line": 2, "guarded": False, "role": "export",
                "compatible_ranges": [("5.9.0", "5.9.0")],
                "statuses": {"5.9.0": "OK"},
            },
        },
        "dynamic": [],
        "env_errors": {},
    }
    md = render_markdown(matrix)
    assert "affected models" in md
    assert "T5" in md
    assert "shared / cross-family" in md
