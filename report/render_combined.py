#!/usr/bin/env python3
"""Render a combined multi-target compatibility report.

Discovers ``<report_dir>/<target>/matrix.json`` for each known target and
writes ``<report_dir>/index.html`` and ``<report_dir>/index.ipynb``.

Usage:
    python render_combined.py REPORT_DIR --modelopt-version 0.44.0 [--generated D] [--outdir DIR]
"""
from __future__ import annotations

import argparse
import datetime
import json
import os

import render_compat as R
from packaging.version import Version

KNOWN_TARGETS = ["transformers", "torch", "vllm", "accelerate"]


def _load_targets(report_dir: str) -> list[tuple[str, dict]]:
    """Return list of (target, matrix) for each target that has a matrix.json."""
    results = []
    for target in KNOWN_TARGETS:
        path = os.path.join(report_dir, target, "matrix.json")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                matrix = json.load(fh)
            results.append((target, matrix))
    return results


def _all_versions_for(matrix: dict, target_name: str = "transformers") -> list[str]:
    """Fetch full version range or fall back to probed list."""
    probed = matrix["versions_probed"]
    if not probed:
        return []
    pkg = matrix.get("pypi", target_name)
    try:
        return R.fetch_full_range(probed[0], probed[-1], probed, pkg=pkg)
    except Exception:
        return sorted(probed, key=Version)


def _overview_html(targets_data: list[tuple[str, dict, dict, list[str]]]) -> str:
    """Build the Overview HTML table.

    targets_data is list of (target, matrix, summary, all_versions).
    """
    rows = []
    for target, matrix, s, all_versions in targets_data:
        probed = matrix["versions_probed"]
        lo = all_versions[0] if all_versions else (probed[0] if probed else "?")
        hi = all_versions[-1] if all_versions else (probed[-1] if probed else "?")
        ver_range = f"{R.esc(lo)} – {R.esc(hi)}"
        rows.append(
            f"<tr>"
            f"<td><a href='#{R.esc(target)}'>{R.esc(target)}</a></td>"
            f"<td>{ver_range}</td>"
            f"<td>{len(probed)}</td>"
            f"<td>{s['symbols']}</td>"
            f"<td>{s['with_window']}</td>"
            f"<td>{s['drift']}</td>"
            f"<td>{s['env_errors']}</td>"
            f"</tr>"
        )
    return (
        "<h2>Overview</h2>"
        "<table><thead><tr>"
        "<th>target</th><th>version range</th><th>#probed</th>"
        "<th>symbols</th><th>with_window</th><th>drift</th><th>env_errors</th>"
        "</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def _target_section_html(target: str, matrix: dict, all_versions: list[str]) -> str:
    """Build the per-target <section> block."""
    probed = matrix["versions_probed"]
    probed_set = set(probed)
    symbols = sorted(matrix["symbols"].items())
    minors = sorted({R.minor(v) for v in all_versions}, key=Version) if all_versions else sorted({R.minor(v) for v in probed}, key=Version)

    parts = [
        R._per_symbol_table(symbols, probed),
        R._support_grid(symbols, minors, all_versions or probed, probed_set, probed),
        R._drift_section(symbols),
        R._never_section(symbols),
        R._dynamic_section(matrix),
    ]
    inner = "\n".join(p for p in parts if p)
    return f"<section id='{R.esc(target)}'><h1>{R.esc(target)}</h1>{inner}</section>"


def build_combined(report_dir: str, modelopt_version: str, generated: str, outdir: str | None = None) -> None:
    """Build index.html and index.ipynb from all available target matrix files."""
    if outdir is None:
        outdir = report_dir

    targets_raw = _load_targets(report_dir)
    if not targets_raw:
        # Write empty stubs so callers don't crash
        os.makedirs(outdir, exist_ok=True)
        html = (
            "<!DOCTYPE html>\n<html lang='en'><head><meta charset='utf-8'>"
            f"<title>modelopt {R.esc(modelopt_version)} compatibility</title>"
            f"<style>{R._css()}</style></head><body>"
            "<header><h1>modelopt PTQ compatibility</h1></header>"
            "<main><p>No target data found.</p></main></body></html>"
        )
        with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(html)
        nb = {"cells": [R._md("# No data found")], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}
        with open(os.path.join(outdir, "index.ipynb"), "w", encoding="utf-8") as fh:
            json.dump(nb, fh, indent=1)
        return

    # Gather data for each target
    targets_data = []
    for target, matrix in targets_raw:
        all_versions = _all_versions_for(matrix, target_name=target)
        s = R.summary(matrix)
        targets_data.append((target, matrix, s, all_versions))

    # ---- HTML ----
    overview = _overview_html(targets_data)
    sections = "\n".join(
        _target_section_html(target, matrix, all_versions)
        for target, matrix, s, all_versions in targets_data
    )

    html_body = f"{overview}\n{sections}"
    html = (
        "<!DOCTYPE html>\n"
        "<html lang='en'><head><meta charset='utf-8'>\n"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>\n"
        f"<title>modelopt {R.esc(modelopt_version)} compatibility</title>\n"
        f"<style>\n{R._css()}\n</style></head>\n"
        "<body>\n"
        "<header>\n"
        "  <h1>modelopt PTQ compatibility</h1>\n"
        f"  <div class='meta'>modelopt <b>{R.esc(modelopt_version)}</b>"
        f" &nbsp;·&nbsp; generated {R.esc(generated)}</div>\n"
        "</header>\n"
        f"<main>\n{html_body}\n</main>\n"
        "</body></html>\n"
    )

    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html)

    # ---- Notebook (markdown-only) ----
    cells = []

    # Title + overview table cell
    overview_md_rows = [
        "| target | version range | #probed | symbols | with_window | drift | env_errors |",
        "|---|---|:--:|:--:|:--:|:--:|:--:|",
    ]
    for target, matrix, s, all_versions in targets_data:
        probed = matrix["versions_probed"]
        lo = all_versions[0] if all_versions else (probed[0] if probed else "?")
        hi = all_versions[-1] if all_versions else (probed[-1] if probed else "?")
        overview_md_rows.append(
            f"| [{target}](#{target}) | {lo} – {hi} | {len(probed)} | "
            f"{s['symbols']} | {s['with_window']} | {s['drift']} | {s['env_errors']} |"
        )

    cells.append(R._md(
        f"# modelopt PTQ compatibility — modelopt `{modelopt_version}`",
        "",
        f"Generated: {generated}",
        "",
        "## Overview",
        "",
        *overview_md_rows,
    ))

    # Per-target cells
    for target, matrix, s, all_versions in targets_data:
        probed = matrix["versions_probed"]
        probed_set = set(probed)
        symbols = sorted(matrix["symbols"].items())
        minors = (
            sorted({R.minor(v) for v in all_versions}, key=Version)
            if all_versions
            else sorted({R.minor(v) for v in probed}, key=Version)
        )
        versions_for_grid = all_versions or probed
        lo = versions_for_grid[0] if versions_for_grid else "?"
        hi = versions_for_grid[-1] if versions_for_grid else "?"

        # Per-symbol table
        sym_rows = [
            "| symbol | role | compatible window (inferred) | support |",
            "|---|---|---|:--:|",
        ]
        for key, info in symbols:
            win = R.range_str(info["compatible_ranges"])
            win = "**never**" if win == "never" else win
            frac = sum(1 for v in probed if info["statuses"].get(v) == "OK") / len(probed) if probed else 0.0
            emoji = "🟩" if frac == 1 else ("🟥" if frac == 0 else "🟨")
            sym_rows.append(f"| `{key}` | {info['role']} | {win} | {emoji} |")

        grid_rows = [
            "| symbol | " + " | ".join(minors) + " |",
            "|---|" + "|".join([":--:"] * len(minors)) + "|",
        ]
        for key, info in symbols:
            grid_rows.append(
                f"| `{key}` | " + " | ".join(R._nb_minor_cell(info, mn, probed) for mn in minors) + " |"
            )

        cells.append(R._md(
            f"## {target}",
            "",
            f"Range: `{lo}` – `{hi}`  ·  {len(probed)} versions probed",
            "",
            "### Per-symbol compatibility",
            "",
            *sym_rows,
            "",
            "### Support grid (by minor version)",
            "",
            "🟩 yes · 🟨 partial · 🟥 no · ⬜ N/A",
            "",
            *grid_rows,
        ))

    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    with open(os.path.join(outdir, "index.ipynb"), "w", encoding="utf-8") as fh:
        json.dump(nb, fh, indent=1, ensure_ascii=False)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("report_dir")
    ap.add_argument("--modelopt-version", required=True)
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--generated", default=datetime.date.today().isoformat())
    args = ap.parse_args()

    outdir = args.outdir or args.report_dir
    build_combined(args.report_dir, args.modelopt_version, args.generated, outdir)
    print("wrote", os.path.join(outdir, "index.html"))
    print("wrote", os.path.join(outdir, "index.ipynb"))


if __name__ == "__main__":
    main()
