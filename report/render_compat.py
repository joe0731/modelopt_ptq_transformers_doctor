#!/usr/bin/env python3
"""Render a doctor ``matrix.json`` into a standalone HTML page and a Jupyter
notebook that record the modelopt PTQ <-> transformers compatibility relation.

Usage:
    python render_compat.py MATRIX_JSON --modelopt-version 0.44.0 --outdir DIR

Stdlib only. Produces ``<outdir>/compatibility.html`` and
``<outdir>/compatibility.ipynb``.
"""
from __future__ import annotations

import argparse
import datetime
import html
import json
import os

MARK = {
    "OK": "✅", "MISSING_SYMBOL": "⚠️", "MISSING_MODULE": "❌",
    "ENV_ERROR": "🛠", "PROBE_ERROR": "💥",
}
CELL_CLASS = {
    "OK": "ok", "MISSING_SYMBOL": "warn", "MISSING_MODULE": "bad",
    "ENV_ERROR": "env", "PROBE_ERROR": "env",
}


def range_str(ranges) -> str:
    if not ranges:
        return "never"
    return ", ".join(f"{lo} – {hi}" for lo, hi in ranges)


def summary(matrix: dict) -> dict:
    syms = matrix["symbols"]
    return {
        "symbols": len(syms),
        "with_window": sum(1 for s in syms.values() if s["compatible_ranges"]),
        "never": sum(1 for s in syms.values() if not s["compatible_ranges"]),
        "drift": sum(1 for s in syms.values() if s.get("signature_drift")),
        "dynamic": len(matrix.get("dynamic", [])),
        "env_errors": len(matrix.get("env_errors", {})),
        "versions": len(matrix.get("versions_probed", [])),
    }


# --------------------------------------------------------------------------- HTML

def build_html(matrix: dict, modelopt_version: str, generated: str) -> str:
    versions = matrix["versions_probed"]
    s = summary(matrix)
    lo = versions[0] if versions else "?"
    hi = versions[-1] if versions else "?"

    def esc(x):
        return html.escape(str(x))

    rows_compat = []
    for key, info in sorted(matrix["symbols"].items()):
        drift = " ⚇" if info.get("signature_drift") else ""
        guard = "🛡" if info["guarded"] else ""
        win = range_str(info["compatible_ranges"])
        win_cls = "never" if not info["compatible_ranges"] else "win"
        rows_compat.append(
            f"<tr><td class='sym'><code>{esc(key)}</code> {guard}{drift}</td>"
            f"<td>{esc(info['role'])}</td>"
            f"<td class='{win_cls}'>{esc(win)}</td></tr>"
        )

    # status grid
    head_cells = "".join(f"<th class='vh'>{esc(v)}</th>" for v in versions)
    grid_rows = []
    for key, info in sorted(matrix["symbols"].items()):
        cells = []
        for v in versions:
            st = info["statuses"].get(v, "")
            cells.append(f"<td class='{CELL_CLASS.get(st, '')}' title='{esc(st)}'>"
                         f"{MARK.get(st, '·')}</td>")
        grid_rows.append(f"<tr><td class='sym'><code>{esc(key)}</code></td>" + "".join(cells) + "</tr>")

    drift_html = ""
    drifts = [(k, i) for k, i in sorted(matrix["symbols"].items()) if i.get("signature_drift")]
    if drifts:
        items = []
        for k, info in drifts:
            trail = " → ".join(f"{esc(v)} <code>{esc(fp)}</code>" for v, fp in info["signature_drift"])
            items.append(f"<li><code>{esc(k)}</code>: {trail}</li>")
        drift_html = "<h2>Signature changes (within compatible window)</h2><ul class='drift'>" \
                     + "".join(items) + "</ul>"

    dyn_html = ""
    if matrix.get("dynamic"):
        items = "".join(f"<li><code>{esc(d['note'])}</code> — {esc(d['file'])}:{esc(d['line'])}</li>"
                        for d in matrix["dynamic"])
        dyn_html = f"<h2>Dynamic registrations (not statically checkable)</h2><ul>{items}</ul>"

    env_html = ""
    if matrix.get("env_errors"):
        items = "".join(f"<li>{esc(v)} — {esc(st)}</li>" for v, st in sorted(matrix["env_errors"].items()))
        env_html = f"<h2>Environment errors</h2><ul>{items}</ul>"

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>modelopt {esc(modelopt_version)} ↔ transformers compatibility</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
         margin: 0; padding: 0 0 4rem; line-height: 1.5; color: #1b1f23; background: #fff; }}
  header {{ background: #0b3d2e; color: #eafff5; padding: 1.6rem 2rem; }}
  header h1 {{ margin: 0 0 .3rem; font-size: 1.4rem; }}
  header .meta {{ opacity: .85; font-size: .9rem; }}
  main {{ padding: 1.5rem 2rem; max-width: 1200px; }}
  .cards {{ display: flex; gap: .8rem; flex-wrap: wrap; margin: 1rem 0 1.5rem; }}
  .card {{ border: 1px solid #d0d7de; border-radius: 8px; padding: .7rem 1rem; min-width: 90px; }}
  .card b {{ display: block; font-size: 1.5rem; }}
  .card span {{ font-size: .8rem; color: #57606a; }}
  h2 {{ margin-top: 2rem; border-bottom: 1px solid #d0d7de; padding-bottom: .3rem; }}
  table {{ border-collapse: collapse; font-size: .86rem; }}
  th, td {{ border: 1px solid #d0d7de; padding: .3rem .5rem; text-align: left; }}
  th {{ background: #f6f8fa; position: sticky; top: 0; }}
  td.sym {{ white-space: nowrap; }}
  code {{ background: #eff1f3; padding: .05rem .3rem; border-radius: 4px; font-size: .85em; }}
  .grid-wrap {{ overflow-x: auto; border: 1px solid #d0d7de; border-radius: 8px; }}
  .grid-wrap table {{ border: 0; }} .grid-wrap th, .grid-wrap td {{ border-width: 0 1px 1px 0; }}
  th.vh {{ writing-mode: vertical-rl; transform: rotate(180deg); text-align: left; font-weight: 500; }}
  td.ok {{ background: #e6ffec; }} td.warn {{ background: #fff8c5; }}
  td.bad {{ background: #ffebe9; }} td.env {{ background: #ddf4ff; }}
  td.win {{ color: #1a7f37; font-weight: 600; }} td.never, .never {{ color: #cf222e; }}
  ul.drift code {{ font-size: .8em; }}
  .legend {{ color: #57606a; font-size: .85rem; margin-top: 1.5rem; }}
</style></head>
<body>
<header>
  <h1>modelopt PTQ ↔ transformers compatibility matrix</h1>
  <div class="meta">modelopt <b>{esc(modelopt_version)}</b> &nbsp;·&nbsp; transformers {esc(lo)} – {esc(hi)}
   &nbsp;·&nbsp; {s['versions']} versions probed &nbsp;·&nbsp; generated {esc(generated)}</div>
</header>
<main>
  <div class="cards">
    <div class="card"><b>{s['symbols']}</b><span>dependency symbols</span></div>
    <div class="card"><b>{s['with_window']}</b><span>with a compatible window</span></div>
    <div class="card"><b>{s['never']}</b><span>never compatible</span></div>
    <div class="card"><b>{s['drift']}</b><span>signature drift ⚇</span></div>
    <div class="card"><b>{s['dynamic']}</b><span>dynamic (unchecked)</span></div>
    <div class="card"><b>{s['env_errors']}</b><span>env errors</span></div>
  </div>

  <p>The <b>compatible</b> column is the authoritative per-symbol version window
  (the version grid below shows only the versions the bisection actually probed —
  a sample, not every version in range).</p>

  <h2>Per-symbol compatibility</h2>
  <table>
    <tr><th>symbol</th><th>role</th><th>compatible window</th></tr>
    {''.join(rows_compat)}
  </table>

  <h2>Status grid (probed versions)</h2>
  <div class="grid-wrap"><table>
    <tr><th>symbol</th>{head_cells}</tr>
    {''.join(grid_rows)}
  </table></div>

  {drift_html}
  {dyn_html}
  {env_html}

  <p class="legend">Legend: ✅ OK · ⚠️ symbol missing · ❌ module missing ·
   🛠 env error · 💥 probe error · 🛡 import is try/except-guarded ·
   ⚇ signature changed within the compatible window</p>
</main>
</body></html>
"""


# ----------------------------------------------------------------------- notebook

def _md(*lines):
    return {"cell_type": "markdown", "metadata": {}, "source": [l + "\n" for l in lines]}


def _code_with_html(source_lines, html_out):
    return {
        "cell_type": "code", "metadata": {}, "execution_count": 1,
        "source": [l + "\n" for l in source_lines],
        "outputs": [{
            "output_type": "execute_result", "execution_count": 1, "metadata": {},
            "data": {"text/html": [html_out], "text/plain": ["<rendered table>"]},
        }],
    }


def build_ipynb(matrix: dict, modelopt_version: str, generated: str) -> dict:
    s = summary(matrix)
    versions = matrix["versions_probed"]
    lo = versions[0] if versions else "?"
    hi = versions[-1] if versions else "?"

    # per-symbol compatibility table as HTML (reused as the cell's pre-rendered output)
    rows = ["<table><tr><th>symbol</th><th>role</th><th>compatible window</th><th>drift</th></tr>"]
    for key, info in sorted(matrix["symbols"].items()):
        d = "⚇" if info.get("signature_drift") else ""
        rows.append(f"<tr><td><code>{html.escape(key)}</code></td><td>{info['role']}</td>"
                    f"<td>{html.escape(range_str(info['compatible_ranges']))}</td><td>{d}</td></tr>")
    rows.append("</table>")
    compat_html = "".join(rows)

    drift_lines = ["## Signature changes (within compatible window)", ""]
    drifts = [(k, i) for k, i in sorted(matrix["symbols"].items()) if i.get("signature_drift")]
    if drifts:
        for k, info in drifts:
            trail = " → ".join(f"`{v}` `{fp}`" for v, fp in info["signature_drift"])
            drift_lines.append(f"- `{k}`: {trail}")
    else:
        drift_lines.append("_No signature drift detected in the probed window._")

    dyn_lines = ["## Dynamic registrations (not statically checkable)", ""]
    if matrix.get("dynamic"):
        for d in matrix["dynamic"]:
            dyn_lines.append(f"- `{d['note']}` — {d['file']}:{d['line']}")
    else:
        dyn_lines.append("_None._")

    cells = [
        _md(f"# modelopt PTQ ↔ transformers compatibility",
            "",
            f"**modelopt:** `{modelopt_version}`  ·  **transformers:** {lo} – {hi}  ·  "
            f"**{s['versions']}** versions probed  ·  generated {generated}",
            "",
            f"- dependency symbols: **{s['symbols']}**",
            f"- with a compatible window: **{s['with_window']}**, never compatible: **{s['never']}**",
            f"- signature drift ⚇: **{s['drift']}**  ·  dynamic (unchecked): **{s['dynamic']}**  ·  "
            f"env errors: **{s['env_errors']}**",
            "",
            "The **compatible** column is the authoritative per-symbol version window.",
            "This notebook is rendered from `matrix.json`; re-run the cells to regenerate."),
        _md("## Per-symbol compatibility"),
        _code_with_html(
            ["import json, html",
             "m = json.load(open('matrix.json'))",
             "def rng(rs): return 'never' if not rs else ', '.join(f'{a} – {b}' for a,b in rs)",
             "rows = ['<table><tr><th>symbol</th><th>role</th><th>compatible window</th><th>drift</th></tr>']",
             "for k, i in sorted(m['symbols'].items()):",
             "    d = '⚇' if i.get('signature_drift') else ''",
             "    rows.append(f\"<tr><td><code>{html.escape(k)}</code></td><td>{i['role']}</td>\"",
             "                f\"<td>{html.escape(rng(i['compatible_ranges']))}</td><td>{d}</td></tr>\")",
             "rows.append('</table>')",
             "from IPython.display import HTML",
             "HTML(''.join(rows))"],
            compat_html),
        _md(*drift_lines),
        _md(*dyn_lines),
        _md("---",
            "Legend: ✅ OK · ⚠️ symbol missing · ❌ module missing · 🛠 env error · "
            "💥 probe error · 🛡 guarded import · ⚇ signature changed within window"),
    ]
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4, "nbformat_minor": 5,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("matrix")
    ap.add_argument("--modelopt-version", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--generated", default=datetime.date.today().isoformat())
    args = ap.parse_args()

    with open(args.matrix, encoding="utf-8") as fh:
        matrix = json.load(fh)

    os.makedirs(args.outdir, exist_ok=True)
    html_path = os.path.join(args.outdir, "compatibility.html")
    ipynb_path = os.path.join(args.outdir, "compatibility.ipynb")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(build_html(matrix, args.modelopt_version, args.generated))
    with open(ipynb_path, "w", encoding="utf-8") as fh:
        json.dump(build_ipynb(matrix, args.modelopt_version, args.generated), fh, indent=1, ensure_ascii=False)
    print("wrote", html_path)
    print("wrote", ipynb_path)


if __name__ == "__main__":
    main()
