"""Render the compatibility matrix as JSON + Markdown."""

from __future__ import annotations

import json
import os

_MARK = {"OK": "✅", "MISSING_SYMBOL": "⚠️", "MISSING_MODULE": "❌",
         "MISSING": "⚠️", "ERROR": "💥", "UNKNOWN": "?",
         "ENV_ERROR": "🛠", "PROBE_ERROR": "💥"}


def _range_str(ranges) -> str:
    if not ranges:
        return "never"
    return ", ".join(f"{lo} – {hi}" for lo, hi in ranges)


def render_markdown(matrix: dict) -> str:
    versions = matrix["versions_probed"]
    target_label = matrix.get("target", "transformers")
    lines = [f"# modelopt PTQ ↔ {target_label} compatibility matrix", ""]

    lines.append("> Version columns show only the versions the bisection actually probed "
                 "(a sample, not every version in range). "
                 "The **compatible** column is the authoritative result.")
    lines.append("")

    if matrix.get("env_errors"):
        lines.append("> ⚠️ Some versions failed to build/probe and are unreliable: "
                     + ", ".join(sorted(matrix["env_errors"]))
                     + ". Compatible ranges adjacent to these versions may be understated.")
        lines.append("")

    header = "| symbol | role | compatible | " + " | ".join(versions) + " |"
    sep = "|---|---|---|" + "---|" * len(versions)
    lines += [header, sep]
    for key, info in sorted(matrix["symbols"].items()):
        cells = [_MARK.get(info["statuses"].get(v, ""), "·") for v in versions]
        guard = " 🛡" if info["guarded"] else ""
        drift = " ⚇" if info.get("signature_drift") else ""
        lines.append(f"| `{key}`{guard}{drift} | {info['role']} | "
                     f"{_range_str(info['compatible_ranges'])} | " + " | ".join(cells) + " |")

    dyn = matrix.get("dynamic", [])
    if dyn:
        lines += ["", "## Dynamic registrations (not statically checkable)", ""]
        for d in dyn:
            lines.append(f"- `{d['note']}` — {d['file']}:{d['line']}")

    known_probes = matrix.get("known_probes", {})
    if known_probes:
        lines += ["", "## Known upstream seam probes", "",
                  "> Static probes for historically brittle ModelOpt/transformers symbols. "
                  "They may cover legacy or optional integrations and are not runtime verdicts.", ""]
        lines.append("| probe | symbol | note | " + " | ".join(versions) + " |")
        lines.append("|---|---|---|" + "---|" * len(versions))
        for probe_id, info in sorted(known_probes.items()):
            cells = [_MARK.get(info.get("statuses", {}).get(v, ""), "·") for v in versions]
            symbol = f"{info.get('module_path')}.{info.get('symbol')}"
            lines.append(f"| `{probe_id}` | `{symbol}` | {info.get('note', '')} | " + " | ".join(cells) + " |")

    structural = matrix.get("structural", {})
    if structural:
        lines += ["", "## Transformers structural checks", "",
                  "> Static source-shape screening for known ModelOpt/transformers seams "
                  "(attention dispatch, MoE expert containers, FP8 helpers). "
                  "This is not a runtime verdict; verify failures with `doctor smoke`.", ""]
        lines.append("| check | source | " + " | ".join(versions) + " |")
        lines.append("|---|---|" + "---|" * len(versions))
        for check_id, info in sorted(structural.items()):
            cells = [_MARK.get(info.get("statuses", {}).get(v, ""), "·") for v in versions]
            lines.append(f"| `{check_id}` | `{info.get('file') or ''}` | " + " | ".join(cells) + " |")
        detail_lines = []
        for check_id, info in sorted(structural.items()):
            for v, detail in sorted(info.get("details", {}).items()):
                missing = ", ".join(detail.get("missing", [])) or detail.get("reason", "")
                detail_lines.append(f"- `{check_id}` @ `{v}`: {missing}")
        if detail_lines:
            lines += ["", "Structural check details:", ""] + detail_lines

    drifts = [(k, info) for k, info in sorted(matrix["symbols"].items())
              if info.get("signature_drift")]
    if drifts:
        lines += ["", "## Signature changes (within compatible window)", ""]
        for k, info in drifts:
            trail = " → ".join(f"{v} `{fp}`" for v, fp in info["signature_drift"])
            lines.append(f"- `{k}`: {trail}")

    lines += ["", "Legend: ✅ OK · ⚠️ symbol missing · ❌ module missing · "
              "🛠 env error · 💥 probe error · 🛡 import is try/except-guarded · "
              "⚇ signature changed within compatible window", ""]
    return "\n".join(lines)


def write_report(matrix: dict, out_dir: str) -> tuple[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "matrix.json")
    md_path = os.path.join(out_dir, "REPORT.md")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(matrix, fh, indent=2, ensure_ascii=False)
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(render_markdown(matrix))
    return json_path, md_path
