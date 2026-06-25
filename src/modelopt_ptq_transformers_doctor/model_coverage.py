"""Transformers model-family coverage inventory for ModelOpt PTQ.

This complements the symbol compatibility matrix. It scans a transformers source
checkout/package and lists model families, then marks which families have direct
ModelOpt PTQ symbol dependencies versus families that merely expose attention /
MoE / linear-like structures worth runtime verification.

This is a static screening signal, not a runtime verdict.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
from pathlib import Path

from .contract import extract_contract
from .relations import resolve_transformers_package_root
from .targets import TARGETS

_SIGNAL_KEYWORDS = {
    "moe": ("moe", "expert"),
    "attention": ("attention",),
    "linear": ("linear",),
}


def _read(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _class_names(source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    return [node.name for node in tree.body if isinstance(node, ast.ClassDef)]


def _signals(classes: list[str]) -> list[str]:
    lowered = [name.lower() for name in classes]
    signals = []
    for signal, needles in _SIGNAL_KEYWORDS.items():
        if any(any(needle in name for needle in needles) for name in lowered):
            signals.append(signal)
    return signals


def _family_from_module(module_path: str) -> str | None:
    prefix = "transformers.models."
    if not module_path.startswith(prefix):
        return None
    rest = module_path[len(prefix):]
    return rest.split(".", 1)[0] if rest else None


def _explicit_symbols(modelopt_root: str) -> dict[str, list[str]]:
    by_family: dict[str, list[str]] = defaultdict(list)
    for rec in extract_contract(modelopt_root, target=TARGETS["transformers"]):
        family = _family_from_module(rec.module_path)
        if family is None:
            continue
        by_family[family].append(rec.key)
    return {family: sorted(set(symbols)) for family, symbols in by_family.items()}


def _modeling_files(models_dir: Path, family: str) -> list[Path]:
    folder = models_dir / family
    files = sorted(folder.glob("modeling_*.py"))
    return [p for p in files if p.is_file()]


def screen_model_coverage(modelopt_root: str, transformers_root: str) -> dict:
    tf_root = resolve_transformers_package_root(transformers_root)
    models_dir = tf_root / "models"
    if not models_dir.is_dir():
        raise FileNotFoundError(f"could not find transformers models directory under {tf_root}")

    explicit = _explicit_symbols(modelopt_root)
    families: list[dict] = []
    for folder in sorted(p for p in models_dir.iterdir() if p.is_dir()):
        family = folder.name
        files = _modeling_files(models_dir, family)
        if not files:
            continue
        classes: list[str] = []
        rel_files: list[str] = []
        for path in files:
            rel_files.append(str(path.relative_to(tf_root)))
            source = _read(path)
            if source:
                classes.extend(_class_names(source))
        signals = _signals(classes)
        direct = explicit.get(family, [])
        if direct:
            coverage = "explicit"
            risk = "covered"
        elif signals:
            coverage = "candidate"
            risk = "verify"
        else:
            coverage = "generic-only"
            risk = "low"
        families.append({
            "family": family,
            "coverage": coverage,
            "risk": risk,
            "modeling_files": rel_files,
            "explicit_symbols": direct,
            "signals": signals,
            "classes": sorted(set(classes)),
        })

    counts = Counter(item["coverage"] for item in families)
    return {
        "modelopt_root": str(modelopt_root),
        "transformers_root": str(tf_root),
        "summary": {
            "families": len(families),
            "explicit": counts.get("explicit", 0),
            "candidate": counts.get("candidate", 0),
            "generic-only": counts.get("generic-only", 0),
        },
        "families": families,
    }


def format_model_coverage_report(report: dict) -> str:
    summary = report.get("summary", {})
    lines = [
        "Transformers model-family coverage inventory",
        "  (static screening signal -- explicit coverage/candidates need runtime smoke verification)",
        "",
        f"ModelOpt root:      {report['modelopt_root']}",
        f"transformers root:  {report['transformers_root']}",
        "",
        "Summary:",
        f"  families:     {summary.get('families', 0)}",
        f"  explicit:     {summary.get('explicit', 0)}",
        f"  candidate:    {summary.get('candidate', 0)}",
        f"  generic-only: {summary.get('generic-only', 0)}",
        "",
        "| family | coverage | risk | signals | explicit symbols | modeling files |",
        "|---|---|---|---|---|---|",
    ]
    order = {"explicit": 0, "candidate": 1, "generic-only": 2}
    for item in sorted(report.get("families", []), key=lambda x: (order.get(x["coverage"], 9), x["family"])):
        signals = ", ".join(item.get("signals", [])) or "-"
        explicit = ", ".join(f"`{s}`" for s in item.get("explicit_symbols", [])) or "-"
        files = ", ".join(f"`{f}`" for f in item.get("modeling_files", [])[:3]) or "-"
        if len(item.get("modeling_files", [])) > 3:
            files += f", +{len(item['modeling_files']) - 3} more"
        lines.append(
            f"| `{item['family']}` | {item['coverage']} | {item['risk']} | "
            f"{signals} | {explicit} | {files} |"
        )
    return "\n".join(lines)
