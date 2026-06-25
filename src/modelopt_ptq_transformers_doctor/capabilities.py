"""Static *screening* for modelopt PTQ export-capability gaps.

modelopt can quantize more MoE expert architectures than its HF export path
explicitly supports (e.g. it quantizes NemotronH's experts but the export path
raises ``NotImplementedError`` for them). This module statically flags expert
types that quantization handles but that are **not explicitly named** in the
export branch and **don't statically match a known structural fallback**.

IMPORTANT — this is a *screening signal, not a verdict*. Export support is a
runtime predicate (a few names, plus structural fallbacks: fused-expert weight
quantizers, or iterable experts), so static analysis cannot prove support or
its absence. Candidates are "verify at runtime", not "broken".

Source of truth (relative to the modelopt root):
- export named cases:   modelopt/torch/export/unified_export_hf.py
- quant expert classes: modelopt/torch/quantization/plugins/huggingface.py
"""
from __future__ import annotations

import ast
import os
import re

EXPORT_FILE = "modelopt/torch/export/unified_export_hf.py"
QUANT_FILE = "modelopt/torch/quantization/plugins/huggingface.py"

_QUANT_EXPERTS_RE = re.compile(r"^_?Quant.*Experts$")


def export_named_experts(source: str) -> set[str]:
    """Expert class-name string literals matched in export via
    ``"X" in type(...).__name__`` (scoped to names containing 'Experts')."""
    out: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Compare) and any(isinstance(o, ast.In) for o in node.ops):
            left = node.left
            if isinstance(left, ast.Constant) and isinstance(left.value, str) and "Experts" in left.value:
                if any(isinstance(c, ast.Attribute) and c.attr == "__name__" for c in node.comparators):
                    out.add(left.value)
    return out


def export_structural_fallbacks(source: str) -> list[str]:
    """Runtime-structural fallbacks the export branch accepts beyond named cases.
    These are not statically verifiable per-architecture — only their presence."""
    fb = []
    if "has_fused_experts_quantizers" in source or "_weight_quantizers" in source:
        fb.append("fused-expert weight quantizers")
    if "Iterable" in source:
        fb.append("iterable experts")
    return fb


def quant_experts_classes(source: str) -> set[str]:
    """modelopt quantized-experts classes (``class _Quant*Experts``)."""
    return {
        node.name
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ClassDef) and _QUANT_EXPERTS_RE.match(node.name)
    }


def screen(export_named: set[str], quant_classes: set[str]) -> list[str]:
    """Quant experts classes not covered by any export-named substring."""
    return sorted(q for q in quant_classes
                  if not any(name in q for name in export_named))


def screen_sources(export_source: str, quant_source: str) -> dict:
    named = export_named_experts(export_source)
    fallbacks = export_structural_fallbacks(export_source)
    quant = quant_experts_classes(quant_source)
    candidates = screen(named, quant)
    has_fused_fb = any("fused" in f for f in fallbacks)
    detail = [
        {"name": c, "maybe_fallback": bool(has_fused_fb and "Fused" in c)}
        for c in candidates
    ]
    return {
        "export_named": sorted(named),
        "export_fallbacks": fallbacks,
        "quant_experts": sorted(quant),
        "candidates": candidates,
        "candidates_detail": detail,
    }


def screen_modelopt(modelopt_root: str) -> dict:
    """Run the screening against an installed modelopt tree.

    Missing source files yield empty inputs (older/newer layouts degrade
    gracefully); the returned report notes which files were found."""
    def _read(rel: str) -> str:
        path = os.path.join(modelopt_root, rel)
        if not os.path.isfile(path):
            return ""
        with open(path, encoding="utf-8") as fh:
            return fh.read()

    export_src, quant_src = _read(EXPORT_FILE), _read(QUANT_FILE)
    report = screen_sources(export_src, quant_src)
    report["files_found"] = {
        EXPORT_FILE: bool(export_src),
        QUANT_FILE: bool(quant_src),
    }
    return report


def format_report(report: dict) -> str:
    """Human-readable screening report (plain text)."""
    lines = ["modelopt PTQ export-capability screening",
             "  (static screening signal — verify candidates at runtime, NOT a verdict)",
             ""]
    lines.append(f"Export explicitly names: {', '.join(report['export_named']) or '(none)'}")
    lines.append(f"Export structural fallbacks (runtime-only): "
                 f"{', '.join(report['export_fallbacks']) or '(none)'}")
    lines.append(f"Quant handles experts:   {', '.join(report['quant_experts']) or '(none)'}")
    lines.append("")
    if report["candidates_detail"]:
        lines.append("Candidates to verify (quant-handled, not export-named):")
        for c in report["candidates_detail"]:
            note = "  — may be covered by the fused-experts fallback; verify" if c["maybe_fallback"] \
                else "  — no known fallback match; likely needs export support"
            lines.append(f"  • {c['name']}{note}")
    else:
        lines.append("No screening candidates: every quant-handled experts class is export-named.")
    return "\n".join(lines)
