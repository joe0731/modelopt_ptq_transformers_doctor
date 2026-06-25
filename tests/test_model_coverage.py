from pathlib import Path

from modelopt_ptq_transformers_doctor import model_coverage


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_screen_model_coverage_labels_explicit_and_candidates(tmp_path):
    modelopt_root = tmp_path / "modelopt-src"
    transformers_repo = tmp_path / "transformers-src"
    tf = transformers_repo / "src" / "transformers"

    write(modelopt_root / "modelopt/torch/quantization/plugins/huggingface.py", """
from transformers.models.t5.modeling_t5 import T5Attention
from transformers.models.dbrx.modeling_dbrx import DbrxExperts
""")
    write(tf / "__init__.py", "")
    write(tf / "models/t5/modeling_t5.py", """
class T5Attention:
    pass
""")
    write(tf / "models/dbrx/modeling_dbrx.py", """
class DbrxExperts:
    pass
""")
    write(tf / "models/qwen3/modeling_qwen3.py", """
class Qwen3Attention:
    pass
class Qwen3MoeExperts:
    def __init__(self):
        self.gate_up_proj = None
        self.down_proj = None
""")
    write(tf / "models/plain/modeling_plain.py", """
class PlainModel:
    pass
""")

    report = model_coverage.screen_model_coverage(str(modelopt_root), str(transformers_repo))
    by_family = {f["family"]: f for f in report["families"]}

    assert by_family["t5"]["coverage"] == "explicit"
    assert by_family["t5"]["explicit_symbols"] == ["transformers.models.t5.modeling_t5:T5Attention"]
    assert by_family["qwen3"]["coverage"] == "candidate"
    assert "attention" in by_family["qwen3"]["signals"]
    assert "moe" in by_family["qwen3"]["signals"]
    assert by_family["plain"]["coverage"] == "generic-only"


def test_format_model_coverage_report_marks_screening_signal():
    report = {
        "modelopt_root": "/m",
        "transformers_root": "/t",
        "summary": {"families": 2, "explicit": 1, "candidate": 1, "generic-only": 0},
        "families": [
            {"family": "t5", "coverage": "explicit", "risk": "covered",
             "modeling_files": ["models/t5/modeling_t5.py"],
             "explicit_symbols": ["transformers.models.t5.modeling_t5:T5Attention"],
             "signals": ["attention"], "classes": ["T5Attention"]},
            {"family": "qwen3", "coverage": "candidate", "risk": "verify",
             "modeling_files": ["models/qwen3/modeling_qwen3.py"],
             "explicit_symbols": [], "signals": ["moe", "attention"],
             "classes": ["Qwen3Attention", "Qwen3MoeExperts"]},
        ],
    }
    text = model_coverage.format_model_coverage_report(report)
    assert "static screening signal" in text
    assert "qwen3" in text and "candidate" in text
