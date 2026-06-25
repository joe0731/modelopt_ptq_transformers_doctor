"""Static source-to-source screening for ModelOpt <-> transformers relations.

This module complements ``doctor scan``.  The scan checks import/signature
availability across installed target versions; this screening checks whether a
specific transformers source tree still exposes the structural shapes ModelOpt
depends on (attention interfaces, MoE expert containers, and selected export
helpers).

IMPORTANT: this is a screening signal, not a runtime verdict.  It never imports
ModelOpt or transformers; it parses source files with ``ast`` and reports
missing source-level shapes that should be verified at runtime with smoke probes.
"""
from __future__ import annotations

import ast
import importlib.util
import os
from collections import Counter
from pathlib import Path
from typing import Iterable

from .contract import extract_contract
from .targets import TARGETS

_REVERSE_REF_TOKENS = ("modelopt", "nvidia-modelopt", "ModelOpt", "Model Optimizer")

_TOP_LEVEL_SYMBOL_FILES = {
    "AutoConfig": "models/auto/configuration_auto.py",
    "AutoFeatureExtractor": "models/auto/feature_extraction_auto.py",
    "PreTrainedModel": "modeling_utils.py",
    "T5Config": "models/t5/configuration_t5.py",
}

_STRUCTURAL_SPECS = [
    {
        "id": "attention-interface",
        "file": "modeling_utils.py",
        "symbols": ["AttentionInterface", "ALL_ATTENTION_FUNCTIONS"],
        "class_methods": {"AttentionInterface": ["get_interface"]},
    },
    {
        "id": "experts-interface",
        "file": "integrations/moe.py",
        "symbols": ["ExpertsInterface", "ALL_EXPERTS_FUNCTIONS", "use_experts_implementation"],
        "class_methods": {"ExpertsInterface": ["get_interface"]},
    },
    {
        "id": "llama4-text-experts",
        "file": "models/llama4/modeling_llama4.py",
        "class": "Llama4TextExperts",
        "attrs": ["num_experts", "hidden_size", "gate_up_proj", "down_proj", "act_fn"],
    },
    {
        "id": "gpt-oss-experts",
        "file": "models/gpt_oss/modeling_gpt_oss.py",
        "class": "GptOssExperts",
        "attrs": ["num_experts", "hidden_size", "gate_up_proj", "down_proj"],
        "methods": ["_apply_gate", "forward"],
    },
    {
        "id": "qwen3-vl-moe-text-experts",
        "file": "models/qwen3_vl_moe/modeling_qwen3_vl_moe.py",
        "class": "Qwen3VLMoeTextExperts",
        "attrs": ["num_experts", "gate_up_proj", "down_proj", "act_fn"],
        "any_attrs": [["hidden_dim", "hidden_size"], ["intermediate_dim", "intermediate_size"]],
    },
    {
        "id": "mixtral-experts",
        "file": "models/mixtral/modeling_mixtral.py",
        "class": "MixtralExperts",
        "attrs": ["num_experts", "gate_up_proj", "down_proj", "act_fn"],
        "any_attrs": [["hidden_dim", "hidden_size"], ["intermediate_dim", "intermediate_size"]],
        "methods": ["forward"],
    },
    {
        "id": "qwen3-moe-experts",
        "file": "models/qwen3_moe/modeling_qwen3_moe.py",
        "class": "Qwen3MoeExperts",
        "attrs": ["num_experts", "gate_up_proj", "down_proj", "act_fn"],
        "any_attrs": [["hidden_dim", "hidden_size"], ["intermediate_dim", "intermediate_size"]],
        "methods": ["forward"],
    },
    {
        "id": "qwen3-5-moe-experts",
        "file": "models/qwen3_5_moe/modeling_qwen3_5_moe.py",
        "class": "Qwen3_5MoeExperts",
        "attrs": ["num_experts", "gate_up_proj", "down_proj", "act_fn"],
        "any_attrs": [["hidden_dim", "hidden_size"], ["intermediate_dim", "intermediate_size"]],
        "methods": ["forward"],
    },
    {
        "id": "nemotron-h-experts",
        "file": "models/nemotron_h/modeling_nemotron_h.py",
        "class": "NemotronHExperts",
        "attrs": ["num_experts", "hidden_dim", "intermediate_dim", "up_proj", "down_proj", "act_fn"],
        "methods": ["forward"],
    },
    {
        "id": "dbrx-experts",
        "file": "models/dbrx/modeling_dbrx.py",
        "class": "DbrxExpertGLU",
        "attrs": ["hidden_size", "ffn_hidden_size", "moe_num_experts", "w1", "v1", "w2"],
        "methods": ["forward"],
    },
    {
        "id": "fp8-linear",
        "file": "integrations/finegrained_fp8.py",
        "class": "FP8Linear",
        "attrs": ["weight", "weight_scale_inv", "activation_scale"],
        "methods": ["forward"],
    },
]


def resolve_transformers_package_root(root: str | os.PathLike[str]) -> Path:
    """Return the ``transformers`` package directory for a repo/package root."""
    p = Path(root)
    candidates = [
        p,
        p / "src" / "transformers",
        p / "transformers",
    ]
    for c in candidates:
        if c.name == "transformers" and (c / "__init__.py").is_file():
            return c
    raise FileNotFoundError(
        f"could not find a transformers package under {p}; expected src/transformers or transformers"
    )


def installed_package_root(package: str) -> Path:
    """Locate an installed package without importing it."""
    spec = importlib.util.find_spec(package)
    if spec is None or not spec.origin:
        raise ModuleNotFoundError(f"{package} is not installed in this environment")
    return Path(spec.origin).parent


def _read(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _top_level_symbols(source: str) -> set[str]:
    tree = ast.parse(source)
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                names.update(_assigned_names(target))
        elif isinstance(node, ast.AnnAssign):
            names.update(_assigned_names(node.target))
    return names


def _assigned_names(node: ast.AST) -> set[str]:
    if isinstance(node, ast.Name):
        return {node.id}
    if isinstance(node, (ast.Tuple, ast.List)):
        out: set[str] = set()
        for elt in node.elts:
            out.update(_assigned_names(elt))
        return out
    return set()


def _class_info(source: str, class_name: str) -> dict | None:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            attrs: set[str] = set()
            methods: set[str] = set()
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.add(child.name)
                for sub in ast.walk(child):
                    attrs.update(_self_attrs_from_node(sub))
            return {"attrs": attrs, "methods": methods}
    return None


def _self_attrs_from_node(node: ast.AST) -> set[str]:
    targets: Iterable[ast.AST]
    if isinstance(node, ast.Assign):
        targets = node.targets
    elif isinstance(node, ast.AnnAssign):
        targets = [node.target]
    elif isinstance(node, ast.AugAssign):
        targets = [node.target]
    else:
        return set()
    out: set[str] = set()
    for target in targets:
        if (
            isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name)
            and target.value.id == "self"
        ):
            out.add(target.attr)
    return out


def _module_relpath(module_path: str, symbol: str) -> str | None:
    if module_path == "transformers":
        return _TOP_LEVEL_SYMBOL_FILES.get(symbol)
    prefix = "transformers."
    if not module_path.startswith(prefix):
        return None
    parts = module_path[len(prefix):].split(".")
    return "/".join(parts) + ".py"


def _check_module_symbol(tf_root: Path, module_path: str, symbol: str) -> tuple[str, str]:
    rel = _module_relpath(module_path, symbol)
    if rel is None:
        return "UNCHECKED", "no source mapping for module"
    source = _read(tf_root / rel)
    if source is None:
        return "MISSING", f"module file missing: {rel}"
    try:
        symbols = _top_level_symbols(source)
    except SyntaxError as exc:
        return "ERROR", f"cannot parse {rel}: {exc}"
    if symbol not in symbols:
        return "MISSING", f"symbol missing from {rel}"
    return "OK", ""


def _screen_direct_contract(modelopt_root: str, tf_root: Path) -> dict:
    records = extract_contract(modelopt_root, target=TARGETS["transformers"])
    counts = Counter(r.role for r in records)
    items = []
    for r in records:
        if not r.module_path.startswith("transformers"):
            continue
        status, reason = _check_module_symbol(tf_root, r.module_path, r.symbol)
        items.append({
            "module_path": r.module_path,
            "symbol": r.symbol,
            "file": r.file,
            "line": r.line,
            "role": r.role,
            "guarded": r.guarded,
            "status": status,
            "reason": reason,
        })
    return {
        "total": len(records),
        "quant": counts.get("quant", 0),
        "export": counts.get("export", 0),
        "guarded": sum(1 for r in records if r.guarded),
        "dynamic": sum(1 for r in records if r.dynamic),
        "items": items,
    }


def _screen_structural(tf_root: Path) -> list[dict]:
    checks = []
    for spec in _STRUCTURAL_SPECS:
        rel = spec["file"]
        source = _read(tf_root / rel)
        missing: list[str] = []
        status = "OK"
        reason = ""
        if source is None:
            checks.append({**_base_check(spec), "status": "MISSING",
                           "missing": [rel], "reason": "source file missing"})
            continue
        try:
            symbols = _top_level_symbols(source)
        except SyntaxError as exc:
            checks.append({**_base_check(spec), "status": "ERROR",
                           "missing": [], "reason": f"cannot parse source: {exc}"})
            continue

        for symbol in spec.get("symbols", []):
            if symbol not in symbols:
                missing.append(symbol)

        cls = spec.get("class")
        info = None
        if cls:
            info = _class_info(source, cls)
            if info is None:
                missing.append(f"class {cls}")
            else:
                for attr in spec.get("attrs", []):
                    if attr not in info["attrs"]:
                        missing.append(f"self.{attr}")
                for group in spec.get("any_attrs", []):
                    if not any(attr in info["attrs"] for attr in group):
                        missing.append("one of " + "/".join(f"self.{a}" for a in group))
                for method in spec.get("methods", []):
                    if method not in info["methods"]:
                        missing.append(f"method {method}")

        for class_name, methods in spec.get("class_methods", {}).items():
            cinfo = _class_info(source, class_name)
            if cinfo is None:
                missing.append(f"class {class_name}")
            else:
                for method in methods:
                    if method not in cinfo["methods"]:
                        missing.append(f"{class_name}.{method}")

        if missing:
            status = "MISSING"
            reason = "required source shape not found"
        checks.append({**_base_check(spec), "status": status, "missing": missing, "reason": reason})
    return checks


def _base_check(spec: dict) -> dict:
    return {"id": spec["id"], "file": spec["file"], "class": spec.get("class")}


def _find_reverse_refs(tf_root: Path) -> list[dict]:
    refs: list[dict] = []
    for path in sorted(tf_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for lineno, line in enumerate(lines, 1):
            if any(token in line for token in _REVERSE_REF_TOKENS):
                refs.append({
                    "file": str(path.relative_to(tf_root)),
                    "line": lineno,
                    "text": line.strip()[:160],
                })
    return refs


def screen_relations(modelopt_root: str, transformers_root: str) -> dict:
    """Screen a ModelOpt source tree against a transformers source tree."""
    tf_root = resolve_transformers_package_root(transformers_root)
    return {
        "modelopt_root": str(modelopt_root),
        "transformers_root": str(tf_root),
        "direct_contract": _screen_direct_contract(modelopt_root, tf_root),
        "structural": _screen_structural(tf_root),
        "reverse_refs": _find_reverse_refs(tf_root),
    }


def format_relations_report(report: dict) -> str:
    """Human-readable relation screening report."""
    direct = report["direct_contract"]
    direct_items = direct.get("items", [])
    missing_direct = [i for i in direct_items if i["status"] != "OK"]
    missing_struct = [i for i in report["structural"] if i["status"] != "OK"]

    lines = [
        "ModelOpt <-> transformers source relation screening",
        "  (static screening signal -- verify candidates at runtime, NOT a verdict)",
        "",
        f"ModelOpt root:      {report['modelopt_root']}",
        f"transformers root:  {report['transformers_root']}",
        "",
        "Direct transformers contract:",
        f"  records: {direct['total']} "
        f"(quant={direct['quant']}, export={direct['export']}, "
        f"guarded={direct['guarded']}, dynamic={direct['dynamic']})",
        f"  checked direct symbols: {len(direct_items)}",
        f"  non-OK direct symbols:  {len(missing_direct)}",
        "",
        "Structural checks:",
        f"  checks: {len(report['structural'])}",
        f"  non-OK checks: {len(missing_struct)}",
    ]
    if missing_direct:
        lines.extend(["", "Direct symbols to inspect:"])
        for item in missing_direct:
            lines.append(
                f"  - {item['status']} {item['module_path']}.{item['symbol']} "
                f"from {item['file']}:{item['line']} ({item['reason']})"
            )
    if missing_struct:
        lines.extend(["", "Structural checks to inspect:"])
        for item in missing_struct:
            missing = ", ".join(item["missing"]) or item["reason"]
            lines.append(f"  - {item['status']} {item['id']} in {item['file']}: {missing}")

    lines.extend(["", f"Reverse transformers -> ModelOpt references: {len(report['reverse_refs'])}"])
    for ref in report["reverse_refs"][:10]:
        lines.append(f"  - {ref['file']}:{ref['line']} {ref['text']}")
    if len(report["reverse_refs"]) > 10:
        lines.append(f"  ... {len(report['reverse_refs']) - 10} more")
    return "\n".join(lines)
