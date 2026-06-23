"""Render the compatibility matrix as JSON + Markdown."""

from __future__ import annotations

import json
import os

_MARK = {"OK": "✅", "MISSING_SYMBOL": "⚠️", "MISSING_MODULE": "❌",
         "ENV_ERROR": "🛠", "PROBE_ERROR": "💥"}


def _range_str(ranges) -> str:
    if not ranges:
        return "never"
    return ", ".join(f"{lo} – {hi}" for lo, hi in ranges)


def render_markdown(matrix: dict) -> str:
    versions = matrix["versions_probed"]
    lines = ["# modelopt PTQ ↔ transformers compatibility matrix", ""]

    if matrix.get("env_errors"):
        lines.append("> ⚠️ Some versions failed to build/probe and are unreliable: "
                     + ", ".join(sorted(matrix["env_errors"])) + ".")
        lines.append("")

    header = "| symbol | role | compatible | " + " | ".join(versions) + " |"
    sep = "|---|---|---|" + "---|" * len(versions)
    lines += [header, sep]
    for key, info in sorted(matrix["symbols"].items()):
        cells = [_MARK.get(info["statuses"].get(v, ""), "·") for v in versions]
        guard = " 🛡" if info["guarded"] else ""
        lines.append(f"| `{key}`{guard} | {info['role']} | "
                     f"{_range_str(info['compatible_ranges'])} | " + " | ".join(cells) + " |")

    dyn = matrix.get("dynamic", [])
    if dyn:
        lines += ["", "## Dynamic registrations (not statically checkable)", ""]
        for d in dyn:
            lines.append(f"- `{d['note']}` — {d['file']}:{d['line']}")

    lines += ["", "Legend: ✅ OK · ⚠️ symbol missing · ❌ module missing · "
              "🛠 env error · 💥 probe error · 🛡 import is try/except-guarded", ""]
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
