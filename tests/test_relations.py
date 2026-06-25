from pathlib import Path

from modelopt_ptq_transformers_doctor import relations


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_resolve_transformers_package_root_accepts_repo_root(tmp_path):
    pkg = tmp_path / "transformers-src" / "src" / "transformers"
    write(pkg / "__init__.py", "")

    assert relations.resolve_transformers_package_root(tmp_path / "transformers-src") == pkg
    assert relations.resolve_transformers_package_root(pkg) == pkg


def test_screen_relations_checks_direct_symbols_and_structures(tmp_path):
    modelopt_root = tmp_path / "modelopt-src"
    transformers_repo = tmp_path / "transformers-src"
    tf = transformers_repo / "src" / "transformers"

    write(modelopt_root / "modelopt/torch/quantization/plugins/huggingface.py", """
import transformers
from transformers.models.llama4.modeling_llama4 import Llama4TextExperts
from transformers.models.gpt_oss.modeling_gpt_oss import GptOssExperts
_ = transformers.pytorch_utils.Conv1D
""")
    write(tf / "__init__.py", "")
    write(tf / "pytorch_utils.py", "class Conv1D: pass\n")
    write(tf / "modeling_utils.py", """
class AttentionInterface:
    def get_interface(self, name, default): return default
ALL_ATTENTION_FUNCTIONS = AttentionInterface()
""")
    write(tf / "integrations/moe.py", """
class ExpertsInterface:
    def get_interface(self, name, default): return default
ALL_EXPERTS_FUNCTIONS = ExpertsInterface()
def use_experts_implementation(*args, **kwargs): pass
""")
    write(tf / "models/llama4/modeling_llama4.py", """
class Llama4TextExperts:
    def __init__(self):
        self.num_experts = 2
        self.hidden_size = 8
        self.gate_up_proj = None
        self.down_proj = None
        self.act_fn = None
""")

    report = relations.screen_relations(str(modelopt_root), str(transformers_repo))
    assert report["direct_contract"]["total"] == 3
    missing = {item["symbol"] for item in report["direct_contract"]["items"]
               if item["status"] == "MISSING"}
    assert "GptOssExperts" in missing
    assert "Conv1D" not in missing

    structural = {item["id"]: item for item in report["structural"]}
    assert structural["attention-interface"]["status"] == "OK"
    assert structural["experts-interface"]["status"] == "OK"
    assert structural["llama4-text-experts"]["status"] == "OK"
    assert structural["gpt-oss-experts"]["status"] == "MISSING"


def test_screen_relations_reports_reverse_references(tmp_path):
    modelopt_root = tmp_path / "modelopt-src"
    transformers_repo = tmp_path / "transformers-src"
    tf = transformers_repo / "src" / "transformers"
    write(modelopt_root / "modelopt/torch/quantization/plugins/huggingface.py", "")
    write(tf / "__init__.py", "# no imports\n")
    write(tf / "some_module.py", "# modelopt compatibility note\n")

    report = relations.screen_relations(str(modelopt_root), str(transformers_repo))
    assert report["reverse_refs"]
    assert report["reverse_refs"][0]["file"] == "some_module.py"


def test_format_relations_report_labels_screening(tmp_path):
    report = {
        "modelopt_root": "/m",
        "transformers_root": "/t",
        "direct_contract": {"total": 1, "quant": 1, "export": 0,
                            "guarded": 0, "dynamic": 0,
                            "items": [{"symbol": "X", "module_path": "transformers.x",
                                       "status": "MISSING", "file": "f.py",
                                       "line": 1, "reason": "module file missing"}]},
        "structural": [{"id": "attention-interface", "status": "OK",
                        "missing": [], "reason": ""}],
        "reverse_refs": [],
    }
    text = relations.format_relations_report(report)
    assert "static screening" in text
    assert "MISSING" in text
