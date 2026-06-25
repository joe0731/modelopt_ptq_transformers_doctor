"""Standalone import-level prober. Runs inside a foreign uv env: stdlib only."""

import ast
import importlib
import importlib.util
import inspect
import os
import json
import sys

OK = "OK"
MISSING_MODULE = "MISSING_MODULE"
MISSING_SYMBOL = "MISSING_SYMBOL"


def probe_one(module_path, symbol):
    try:
        mod = importlib.import_module(module_path)
    except Exception:
        return MISSING_MODULE
    if symbol is None:
        return OK
    return OK if hasattr(mod, symbol) else MISSING_SYMBOL


def probe_records(records):
    statuses = {}
    for r in records:
        if r.get("dynamic"):
            continue
        key = "{}:{}".format(r["module_path"], r["symbol"])
        statuses[key] = probe_one(r["module_path"], r["symbol"])
    return statuses


def fingerprint(obj):
    """A stable string identity for drift detection: a callable's signature,
    or the type name for non-callables; '<no-signature>' when unavailable."""
    if callable(obj):
        try:
            return str(inspect.signature(obj))
        except (ValueError, TypeError):
            return "<no-signature>"
    return type(obj).__name__


def probe_signatures(records):
    sigs = {}
    for r in records:
        if r.get("dynamic"):
            continue
        module_path, symbol = r["module_path"], r["symbol"]
        if probe_one(module_path, symbol) != OK:
            continue
        try:
            mod = importlib.import_module(module_path)
            obj = mod if symbol is None else getattr(mod, symbol)
            sigs["{}:{}".format(module_path, symbol)] = fingerprint(obj)
        except Exception:
            continue
    return sigs


_KNOWN_TRANSFORMERS_SEAMS = [
    {
        "id": "legacy-modeling-utils-conv1d",
        "module_path": "transformers.modeling_utils",
        "symbol": "Conv1D",
        "note": "legacy ModelOpt HF plugin path; newer transformers exposes Conv1D under pytorch_utils",
    },
    {
        "id": "pytorch-utils-conv1d",
        "module_path": "transformers.pytorch_utils",
        "symbol": "Conv1D",
        "note": "current HF GPT-2 Conv1D location used by newer ModelOpt plugins",
    },
    {
        "id": "medusa-flash-attn-available",
        "module_path": "transformers.utils",
        "symbol": "is_flash_attn_available",
        "note": "Medusa/speculative path import used by older ModelOpt examples",
    },
]


def probe_known_transformers_seams():
    """Probe known historical ModelOpt/transformers seam symbols.

    These are screening probes: they may cover legacy or optional integrations
    that are not present in the current AST allowlist, so failures are not by
    themselves PTQ verdicts.
    """
    out = []
    for item in _KNOWN_TRANSFORMERS_SEAMS:
        result = dict(item)
        result["status"] = probe_one(item["module_path"], item["symbol"])
        out.append(result)
    return out


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


def _transformers_root():
    spec = importlib.util.find_spec("transformers")
    if spec is None or not spec.origin:
        return None
    return os.path.dirname(spec.origin)


def _read(path):
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _assigned_names(node):
    if isinstance(node, ast.Name):
        return {node.id}
    if isinstance(node, (ast.Tuple, ast.List)):
        out = set()
        for elt in node.elts:
            out.update(_assigned_names(elt))
        return out
    return set()


def _top_level_symbols(source):
    tree = ast.parse(source)
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                names.update(_assigned_names(target))
        elif isinstance(node, ast.AnnAssign):
            names.update(_assigned_names(node.target))
    return names


def _self_attrs_from_node(node):
    if isinstance(node, ast.Assign):
        targets = node.targets
    elif isinstance(node, ast.AnnAssign):
        targets = [node.target]
    elif isinstance(node, ast.AugAssign):
        targets = [node.target]
    else:
        return set()
    out = set()
    for target in targets:
        if (isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"):
            out.add(target.attr)
    return out


def _class_info(source, class_name):
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            attrs = set()
            methods = set()
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.add(child.name)
                for sub in ast.walk(child):
                    attrs.update(_self_attrs_from_node(sub))
            return {"attrs": attrs, "methods": methods}
    return None


def probe_transformers_structures(package_root=None):
    """Source-level structural checks for known ModelOpt/transformers seams.

    Standard-library only: the prober runs inside throwaway target envs.
    """
    root = package_root or _transformers_root()
    checks = []
    if root is None:
        return [{"id": spec["id"], "file": spec["file"], "status": MISSING_MODULE,
                 "missing": ["transformers"], "reason": "transformers package not found"}
                for spec in _STRUCTURAL_SPECS]

    for spec in _STRUCTURAL_SPECS:
        rel = spec["file"]
        source = _read(os.path.join(root, rel))
        missing = []
        if source is None:
            checks.append({"id": spec["id"], "file": rel, "status": "MISSING",
                           "missing": [rel], "reason": "source file missing"})
            continue
        try:
            symbols = _top_level_symbols(source)
        except SyntaxError as exc:
            checks.append({"id": spec["id"], "file": rel, "status": "ERROR",
                           "missing": [], "reason": "cannot parse source: {}".format(exc)})
            continue

        for symbol in spec.get("symbols", []):
            if symbol not in symbols:
                missing.append(symbol)

        cls = spec.get("class")
        if cls:
            info = _class_info(source, cls)
            if info is None:
                missing.append("class " + cls)
            else:
                for attr in spec.get("attrs", []):
                    if attr not in info["attrs"]:
                        missing.append("self." + attr)
                for group in spec.get("any_attrs", []):
                    if not any(attr in info["attrs"] for attr in group):
                        missing.append("one of " + "/".join("self." + a for a in group))
                for method in spec.get("methods", []):
                    if method not in info["methods"]:
                        missing.append("method " + method)

        for class_name, methods in spec.get("class_methods", {}).items():
            info = _class_info(source, class_name)
            if info is None:
                missing.append("class " + class_name)
            else:
                for method in methods:
                    if method not in info["methods"]:
                        missing.append(class_name + "." + method)

        checks.append({"id": spec["id"], "file": rel,
                       "status": "MISSING" if missing else "OK",
                       "missing": missing,
                       "reason": "required source shape not found" if missing else ""})
    return checks


def _transformers_version():
    try:
        import transformers
        return getattr(transformers, "__version__", None)
    except Exception:
        return None


def main():
    payload = json.load(sys.stdin)
    records = payload["records"]
    out = {
        "transformers_version": _transformers_version(),
        "statuses": probe_records(records),
        "signatures": probe_signatures(records),
    }
    if payload.get("probe_structures"):
        out["structural"] = probe_transformers_structures()
        out["known_probes"] = probe_known_transformers_seams()
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    main()
