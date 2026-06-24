#!/usr/bin/env python3
"""Render a doctor ``matrix.json`` into:

* ``compatibility.html`` — a polished, colour-graded standalone page, and
* ``compatibility.ipynb`` — a clean, results-only notebook (markdown only,
  no code/execution shown).

Both record the modelopt PTQ <-> transformers compatibility relation. Each
probed version is shown as **yes / no**; versions in range that the bisection
did not probe are shown as **N/A**. Stdlib only.

Usage:
    python render_compat.py MATRIX_JSON --modelopt-version 0.44.0 --outdir DIR
"""
from __future__ import annotations

import argparse
import datetime
import html
import json
import os
import urllib.request

from packaging.version import InvalidVersion, Version

# status -> (emoji square, css class, short label)
STATUS = {
    "OK":             ("🟩", "ok",   "yes"),
    "MISSING_SYMBOL": ("🟨", "warn", "no·sym"),
    "MISSING_MODULE": ("🟥", "bad",  "no·mod"),
    "ENV_ERROR":      ("🟦", "env",  "env"),
    "PROBE_ERROR":    ("🟦", "env",  "probe"),
}
NA = ("⬜", "na", "N/A")


def short(key: str) -> str:
    return key.split(":")[-1]


def range_str(ranges) -> str:
    return "never" if not ranges else ", ".join(f"{lo} – {hi}" for lo, hi in ranges)


# --------------------------------------------------- signature-diff (for readability)

def _split_sig(sig: str):
    """Split a signature string '(a, b=1) -> r' into (params:list, ret:str) or
    (None, None) when it is not a parenthesised signature (e.g. a type name)."""
    s = sig.strip()
    if not s.startswith("("):
        return None, None
    depth = end = 0
    for i, ch in enumerate(s):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                end = i
                break
    inside, ret = s[1:end], s[end + 1:].strip()
    parts, depth, cur, q = [], 0, "", None
    for ch in inside:
        if q:
            cur += ch
            if ch == q:
                q = None
            continue
        if ch in "'\"":
            q = ch; cur += ch
        elif ch in "([{":
            depth += 1; cur += ch
        elif ch in ")]}":
            depth -= 1; cur += ch
        elif ch == "," and depth == 0:
            if cur.strip():
                parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return parts, ret


def _pname(p: str) -> str:
    t = p.strip().lstrip("*").strip()
    for sep in (":", "="):
        if sep in t:
            t = t.split(sep, 1)[0]
    return t.strip() or p.strip()


def sig_changes(old_fp: str, new_fp: str):
    """Human-readable change list between two signature fingerprints.

    Returns a list of (kind, text) where kind in {add, del, mod, ret}, or None
    when either side is opaque (not a signature)."""
    po, ro = _split_sig(old_fp)
    pn, rn = _split_sig(new_fp)
    if po is None or pn is None:
        return None
    om, nm = {}, {}
    for p in po:
        om.setdefault(_pname(p), p)
    for p in pn:
        nm.setdefault(_pname(p), p)
    out = []
    for k, p in nm.items():
        if k not in om:
            out.append(("add", p))
    for k, p in om.items():
        if k not in nm:
            out.append(("del", p))
    for k, p in nm.items():
        if k in om and om[k] != p:
            out.append(("mod", f"{om[k]}  →  {p}"))
    if ro != rn:
        out.append(("ret", f"return {ro or '(none)'} → {rn or '(none)'}"))
    return out


def fetch_full_range(lo: str, hi: str, probed: list[str]) -> list[str]:
    """All stable transformers releases in [lo, hi]; falls back to *probed*."""
    try:
        with urllib.request.urlopen("https://pypi.org/pypi/transformers/json", timeout=30) as r:
            data = json.load(r)
        lov, hiv = Version(lo), Version(hi)
        out = []
        for raw in data.get("releases", {}):
            try:
                v = Version(raw)
            except InvalidVersion:
                continue
            if v.is_prerelease or v.is_devrelease:
                continue
            if lov <= v <= hiv:
                out.append(raw)
        return sorted(set(out) | set(probed), key=Version)
    except Exception:
        return sorted(probed, key=Version)


def minor(v: str) -> str:
    p = v.split(".")
    return ".".join(p[:2]) if len(p) >= 2 else v


def cell_for(info: dict, version: str, probed: set) -> tuple[str, str, str]:
    if version not in probed:
        return NA
    return STATUS.get(info["statuses"].get(version, ""), NA)


def minor_status(info: dict, mn: str, all_versions: list[str], probed: set) -> tuple[str, str]:
    """Aggregate one feature (minor) version into (css_class, tooltip).

    green=all probed patches OK, red=all module-missing, amber=mixed/symbol-
    missing, na=no patch in this minor was probed.
    """
    patches = [v for v in all_versions if minor(v) == mn]
    probed_patches = [v for v in patches if v in probed]
    if not probed_patches:
        return "na", f"{mn}: N/A — not probed ({len(patches)} release(s) in range)"
    sts = [info["statuses"].get(v, "") for v in probed_patches]
    ok = sum(1 for x in sts if x == "OK")
    detail = ", ".join(f"{v} {STATUS.get(info['statuses'].get(v, ''), NA)[2]}" for v in probed_patches)
    if ok == len(sts):
        cls = "ok"
    elif ok == 0:
        cls = "bad" if all(x == "MISSING_MODULE" for x in sts) else "warn"
    else:
        cls = "warn"
    return cls, f"{mn}: {detail}"


def summary(matrix: dict) -> dict:
    syms = matrix["symbols"]
    return {
        "symbols": len(syms),
        "with_window": sum(1 for s in syms.values() if s["compatible_ranges"]),
        "never": sum(1 for s in syms.values() if not s["compatible_ranges"]),
        "drift": sum(1 for s in syms.values() if s.get("signature_drift")),
        "dynamic": len(matrix.get("dynamic", [])),
        "env_errors": len(matrix.get("env_errors", {})),
    }


def support_frac(info: dict, probed: list[str]) -> float:
    if not probed:
        return 0.0
    ok = sum(1 for v in probed if info["statuses"].get(v) == "OK")
    return ok / len(probed)


# --------------------------------------------------------------------------- HTML

def build_html(matrix: dict, modelopt_version: str, generated: str, all_versions: list[str]) -> str:
    probed = matrix["versions_probed"]
    probed_set = set(probed)
    s = summary(matrix)
    lo, hi = (all_versions[0], all_versions[-1]) if all_versions else ("?", "?")

    def esc(x):
        return html.escape(str(x))

    def support_bar(frac):
        pct = round(frac * 100)
        hue = round(120 * frac)  # 0=red -> 120=green
        return (f"<div class='bar'><span style='width:{pct}%;"
                f"background:hsl({hue} 70% 45%)'></span></div>"
                f"<small>{pct}%</small>")

    # per-symbol table
    sym_rows = []
    for key, info in sorted(matrix["symbols"].items()):
        drift = "<span class='tag drift' title='signature changed within window'>⚇ drift</span>" \
            if info.get("signature_drift") else ""
        guard = "<span class='tag guard'>🛡</span>" if info["guarded"] else ""
        win = range_str(info["compatible_ranges"])
        win_html = f"<span class='never'>never</span>" if not info["compatible_ranges"] else esc(win)
        sym_rows.append(
            f"<tr><td class='sym'><code>{esc(key)}</code> {guard}{drift}</td>"
            f"<td>{esc(info['role'])}</td>"
            f"<td>{win_html}</td>"
            f"<td class='supcell'>{support_bar(support_frac(info, probed))}</td></tr>"
        )

    # grid: one column per feature (minor) version, coloured by compatibility
    minors = sorted({minor(v) for v in all_versions}, key=Version)
    probed_minors = {minor(v) for v in probed}
    head = "".join(
        f"<th class='vh{' na' if mn not in probed_minors else ''}'>{esc(mn)}</th>" for mn in minors
    )
    glyph = {"ok": "✓", "warn": "~", "bad": "✗", "env": "!", "na": "–"}
    grid_rows = []
    for key, info in sorted(matrix["symbols"].items()):
        cells = []
        for mn in minors:
            cls, tip = minor_status(info, mn, all_versions, probed_set)
            cells.append(f"<td class='{cls}' title='{esc(tip)}'>{glyph[cls]}</td>")
        grid_rows.append(
            f"<tr><th class='rsym'><code>{esc(key)}</code></th>" + "".join(cells) + "</tr>"
        )

    drift_html = ""
    drifts = [(k, i) for k, i in sorted(matrix["symbols"].items()) if i.get("signature_drift")]
    if drifts:
        sym = {"add": "+", "del": "−", "mod": "~", "ret": "↩"}
        items = []
        for k, info in drifts:
            seq = info["signature_drift"]
            steps = []
            for (vo, fo), (vn, fn) in zip(seq, seq[1:]):
                chg = sig_changes(fo, fn)
                head = f"<span class='v'>{esc(vo)} → {esc(vn)}</span>"
                if chg is None:
                    body = f"<code>{esc(fo)}</code> <span class='arr'>→</span> <code>{esc(fn)}</code>"
                elif len(chg) > 6:
                    nb = {kk: sum(1 for t, _ in chg if t == kk) for kk in ("add", "del", "mod", "ret")}
                    detail = "".join(f"<div class='cz {t}'>{esc(sym[t])} {esc(txt)}</div>" for t, txt in chg)
                    body = (f"<span class='cz mod'>+{nb['add']} −{nb['del']} ~{nb['mod']} params (major rewrite)</span>"
                            f"<details><summary>details</summary>{detail}</details>")
                elif chg:
                    body = "".join(f"<div class='cz {t}'>{esc(sym[t])} {esc(txt)}</div>" for t, txt in chg)
                else:
                    body = "<div class='cz'>(reordered / formatting only)</div>"
                steps.append(f"<div class='step'>{head}{body}</div>")
            items.append(f"<li><code>{esc(k)}</code>{''.join(steps)}</li>")
        drift_html = ("<h2>⚇ Signature changes <small>(within the compatible window — what actually changed)</small></h2>"
                      "<ul class='drift'>" + "".join(items) + "</ul>")

    never = [k for k, i in sorted(matrix["symbols"].items()) if not i["compatible_ranges"]]
    never_html = ""
    if never:
        items = "".join(f"<li><code>{esc(k)}</code></li>" for k in never)
        never_html = ("<h2>✗ Never compatible <small>(architecture absent in this range)</small></h2>"
                      f"<ul class='never-list'>{items}</ul>")

    dyn_html = ""
    if matrix.get("dynamic"):
        items = "".join(f"<li><code>{esc(d['note'])}</code> <span class='loc'>{esc(d['file'])}:{esc(d['line'])}</span></li>"
                        for d in matrix["dynamic"])
        dyn_html = ("<details><summary>Dynamic registrations "
                    f"({len(matrix['dynamic'])}) — runtime-discovered, not statically checkable</summary>"
                    f"<ul class='dyn'>{items}</ul></details>")

    na_versions = [v for v in all_versions if v not in probed_set]
    na_count = len(na_versions)
    probed_chips = " ".join(f"<span class='chip'>{esc(v)}</span>" for v in probed)
    na_chips = " ".join(f"<span class='chip na'>{esc(v)}</span>" for v in na_versions)
    probed_block = (
        f"<details open class='probed'><summary><b>{len(probed)}</b> of {len(all_versions)} "
        "in-range releases were <b>actually probed</b> — the rest are <b>N/A</b> "
        "(inferred from the window, not tested)</summary>"
        f"<div class='chips'><b>✓ probed ({len(probed)}):</b> {probed_chips}</div>"
        + (f"<div class='chips'><b>– N/A, not tested ({na_count}):</b> {na_chips}</div>" if na_versions else "")
        + "</details>"
    )
    coverage = (f"All <b>{len(probed)}</b> stable releases in range were probed directly "
                "(yes/no determined by test; no inferred cells)." if na_count == 0 else
                f"<b>{len(probed)}</b> of {len(all_versions)} in-range releases were probed; "
                f"the other {na_count} are <b>N/A</b> (not directly tested).")

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>modelopt {esc(modelopt_version)} ↔ transformers compatibility</title>
<style>
  :root {{ --line:#d8dee4; --muted:#636c76; --ok:#2da44e; --warn:#d4a72c; --bad:#cf222e; --env:#0969da; --na:#d0d7de; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: ui-sans-serif,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
         margin:0; color:#1f2328; background:#f6f8fa; line-height:1.5; }}
  header {{ background:linear-gradient(135deg,#0b3d2e,#10684c); color:#eafff5; padding:2rem 2.2rem; }}
  header h1 {{ margin:0 0 .4rem; font-size:1.45rem; font-weight:650; }}
  header .meta {{ opacity:.9; font-size:.9rem; }} header .meta b {{ color:#fff; }}
  main {{ max-width:1180px; margin:0 auto; padding:1.5rem 2.2rem 4rem; }}
  .note {{ background:#fff; border:1px solid var(--line); border-left:4px solid var(--ok);
          border-radius:8px; padding:.7rem 1rem; margin:1.2rem 0; font-size:.9rem; }}
  .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(120px,1fr)); gap:.8rem; margin:1.2rem 0 1.8rem; }}
  .card {{ background:#fff; border:1px solid var(--line); border-radius:10px; padding:.8rem 1rem; }}
  .card b {{ display:block; font-size:1.7rem; font-weight:680; line-height:1.1; }}
  .card span {{ font-size:.78rem; color:var(--muted); }}
  h2 {{ margin:2.2rem 0 .8rem; font-size:1.15rem; }} h2 small {{ color:var(--muted); font-weight:400; font-size:.8rem; }}
  table {{ border-collapse:collapse; background:#fff; font-size:.86rem; width:100%; border:1px solid var(--line); border-radius:10px; overflow:hidden; }}
  th,td {{ padding:.45rem .6rem; text-align:left; border-bottom:1px solid var(--line); }}
  thead th, table tr:first-child th {{ background:#f6f8fa; color:var(--muted); font-weight:600; }}
  td.sym {{ white-space:nowrap; }}
  code {{ background:#eff1f3; padding:.08rem .35rem; border-radius:5px; font-size:.85em; }}
  .tag {{ font-size:.72rem; padding:.05rem .35rem; border-radius:10px; margin-left:.25rem; white-space:nowrap; }}
  .tag.drift {{ background:#fff1e5; color:#bc4c00; border:1px solid #ffd8b5; }}
  .tag.guard {{ background:#eef; }}
  .never {{ color:var(--bad); font-weight:600; }}
  .supcell {{ width:140px; }}
  .bar {{ display:inline-block; width:100px; height:8px; background:#eaeef2; border-radius:5px; overflow:hidden; vertical-align:middle; }}
  .bar span {{ display:block; height:100%; }} .supcell small {{ margin-left:.4rem; color:var(--muted); }}
  .grid-wrap {{ overflow-x:auto; border:1px solid var(--line); border-radius:10px; background:#fff; }}
  .grid-wrap table {{ border:0; border-radius:0; font-size:.8rem; }}
  .grid-wrap th, .grid-wrap td {{ border-bottom:1px solid #eaeef2; }}
  th.vh {{ writing-mode:vertical-rl; transform:rotate(180deg); font-weight:500; padding:.4rem .15rem; white-space:nowrap; }}
  th.vh.na {{ color:var(--na); }}
  th.rsym {{ position:sticky; left:0; background:#fff; white-space:nowrap; z-index:1; border-right:1px solid var(--line); }}
  .grid-wrap td {{ min-width:26px; padding:0; height:24px; text-align:center; color:#fff; font-size:.74rem; font-weight:700; }}
  td.ok{{background:var(--ok)}} td.warn{{background:var(--warn)}} td.bad{{background:var(--bad)}}
  td.env{{background:var(--env)}} td.na{{color:#8c959f;background:repeating-linear-gradient(45deg,#fff,#fff 3px,#eaeef2 3px,#eaeef2 6px)}}
  ul.drift {{ list-style:none; padding:0; }} ul.drift>li {{ background:#fff; border:1px solid var(--line); border-radius:8px; padding:.6rem .9rem; margin-bottom:.6rem; }}
  .step {{ margin:.5rem 0 0; padding-left:.8rem; border-left:2px solid #eaeef2; }}
  .step .v {{ display:inline-block; color:#0969da; font-weight:650; font-size:.82rem; margin-bottom:.2rem; }}
  .cz {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.78rem; padding:.1rem .2rem; margin:.1rem 0; border-radius:4px; }}
  .cz.add {{ color:#1a7f37; background:#e6ffec; }} .cz.del {{ color:#cf222e; background:#ffebe9; }}
  .cz.mod {{ color:#9a6700; background:#fff8c5; }} .cz.ret {{ color:#0550ae; background:#ddf4ff; }}
  .arr {{ color:var(--muted); }}
  .never-list code, .dyn code {{ color:#1f2328; }} .loc {{ color:var(--muted); font-size:.8em; }}
  details {{ margin-top:1.2rem; }} summary {{ cursor:pointer; color:var(--muted); }}
  ul.dyn {{ columns:2; font-size:.85rem; }}
  details.probed {{ background:#fff; border:1px solid var(--line); border-radius:8px; padding:.6rem .9rem; margin:1.2rem 0; }}
  .chips {{ margin:.4rem 0; font-size:.8rem; line-height:2; }}
  .chip {{ background:#e6ffec; border:1px solid #b7f0c2; border-radius:10px; padding:.06rem .45rem; margin:.1rem; white-space:nowrap; }}
  .chip.na {{ background:#f6f8fa; border-color:#d0d7de; color:#8c959f; }}
  .legend {{ margin-top:1.8rem; font-size:.85rem; color:var(--muted); display:flex; gap:1rem; flex-wrap:wrap; align-items:center; }}
  .sw {{ display:inline-block; width:12px; height:12px; border-radius:3px; vertical-align:middle; margin-right:.25rem; }}
</style></head>
<body>
<header>
  <h1>modelopt PTQ ↔ transformers compatibility</h1>
  <div class="meta">modelopt <b>{esc(modelopt_version)}</b> &nbsp;·&nbsp; transformers <b>{esc(lo)} – {esc(hi)}</b>
   &nbsp;·&nbsp; {len(probed)} versions probed &nbsp;·&nbsp; generated {esc(generated)}</div>
</header>
<main>
  <div class="note">{coverage} The <b>compatible</b> window is the authoritative per-symbol result.</div>
  <div class="cards">
    <div class="card"><b>{s['symbols']}</b><span>dependency symbols</span></div>
    <div class="card"><b>{s['with_window']}</b><span>with a compatible window</span></div>
    <div class="card"><b>{s['never']}</b><span>never compatible</span></div>
    <div class="card"><b>{s['drift']}</b><span>signature drift ⚇</span></div>
    <div class="card"><b>{s['dynamic']}</b><span>dynamic (unchecked)</span></div>
    <div class="card"><b>{s['env_errors']}</b><span>env errors</span></div>
  </div>

  {probed_block}

  <h2>Per-symbol compatibility <small>(window is inferred from the probed sample)</small></h2>
  <table>
    <thead><tr><th>symbol</th><th>role</th><th>compatible window <small>(inferred)</small></th><th>support</th></tr></thead>
    <tbody>{''.join(sym_rows)}</tbody>
  </table>

  <h2>Support grid <small>(symbol × feature version — colour = compatibility; hover for patch detail)</small></h2>
  <div class="grid-wrap"><table>
    <tr><th class="rsym">symbol</th>{head}</tr>
    {''.join(grid_rows)}
  </table></div>

  {drift_html}
  {never_html}
  {dyn_html}

  <div class="legend">
    <span><span class="sw" style="background:var(--ok)"></span>✓ yes (imports OK)</span>
    <span><span class="sw" style="background:var(--warn)"></span>~ partial / symbol missing</span>
    <span><span class="sw" style="background:var(--bad)"></span>✗ no · module missing</span>
    <span><span class="sw" style="background:var(--env)"></span>! env/probe error</span>
    <span><span class="sw" style="background:#d0d7de"></span>– N/A (not tested)</span>
    <span>🛡 guarded import · ⚇ signature drift</span>
  </div>
</main>
</body></html>
"""


# ----------------------------------------------------------------- notebook (md only)

def _md(*lines):
    return {"cell_type": "markdown", "metadata": {}, "source": [l + "\n" for l in lines]}


def build_ipynb(matrix: dict, modelopt_version: str, generated: str, all_versions: list[str]) -> dict:
    probed = matrix["versions_probed"]
    probed_set = set(probed)
    s = summary(matrix)
    lo, hi = (all_versions[0], all_versions[-1]) if all_versions else ("?", "?")
    minors = sorted({minor(v) for v in all_versions}, key=Version)

    def sup_emoji(info):
        f = support_frac(info, probed)
        return "🟩" if f == 1 else ("🟥" if f == 0 else "🟨")

    def minor_cell(info, mn):
        sts = {info["statuses"].get(v) for v in probed if minor(v) == mn}
        if not sts:
            return "⬜"
        if sts == {"OK"}:
            return "🟩"
        if "OK" in sts:
            return "🟨"
        if sts <= {"MISSING_MODULE"}:
            return "🟥"
        return "🟨"

    na_count = len([v for v in all_versions if v not in probed_set])
    coverage = (f"All **{len(probed)}** stable releases in `{lo}`–`{hi}` were probed directly "
                "— yes/no determined by test, no inferred (N/A) cells."
                if na_count == 0 else
                f"**{len(probed)}** of {len(all_versions)} in-range releases were probed directly; "
                f"the other **{na_count}** are N/A (not tested).")

    na_versions = [v for v in all_versions if v not in probed_set]

    # per-symbol table
    tbl = ["| symbol | role | compatible window (inferred) | support | |",
           "|---|---|---|:--:|:--:|"]
    for key, info in sorted(matrix["symbols"].items()):
        win = range_str(info["compatible_ranges"])
        win = f"**never**" if win == "never" else win
        drift = "⚇" if info.get("signature_drift") else ""
        tbl.append(f"| `{key}` | {info['role']} | {win} | {sup_emoji(info)} | {drift} |")

    # minor grid
    grid = ["| symbol | " + " | ".join(minors) + " |",
            "|---|" + "|".join([":--:"] * len(minors)) + "|"]
    for key, info in sorted(matrix["symbols"].items()):
        cells = " | ".join(minor_cell(info, mn) for mn in minors)
        grid.append(f"| `{key}` | {cells} |")

    drift_lines = []
    drifts = [(k, i) for k, i in sorted(matrix["symbols"].items()) if i.get("signature_drift")]
    if drifts:
        sym = {"add": "+", "del": "−", "mod": "~", "ret": "↩"}
        for k, info in drifts:
            drift_lines.append(f"**`{k}`**")
            seq = info["signature_drift"]
            for (vo, fo), (vn, fn) in zip(seq, seq[1:]):
                chg = sig_changes(fo, fn)
                if chg is None:
                    drift_lines.append(f"- `{vo} → {vn}` — `{fo}` → `{fn}`")
                elif len(chg) > 6:
                    nb = {kk: sum(1 for t, _ in chg if t == kk) for kk in ("add", "del", "mod", "ret")}
                    drift_lines.append(f"- `{vo} → {vn}` — **+{nb['add']} −{nb['del']} ~{nb['mod']}** params (major rewrite)")
                elif chg:
                    parts = "; ".join(f"{sym[t]} `{txt}`" for t, txt in chg)
                    drift_lines.append(f"- `{vo} → {vn}` — {parts}")
                else:
                    drift_lines.append(f"- `{vo} → {vn}` — (reordered / formatting only)")
            drift_lines.append("")
    else:
        drift_lines = ["_No signature drift detected._"]

    never = [k for k, i in sorted(matrix["symbols"].items()) if not i["compatible_ranges"]]
    never_lines = ([f"- `{k}`" for k in never] if never else ["_None._"])

    dyn_lines = ["<details><summary>"
                 f"{len(matrix.get('dynamic', []))} dynamic registrations "
                 "(runtime-discovered, not statically checkable)</summary>", ""]
    for d in matrix.get("dynamic", []):
        dyn_lines.append(f"- `{d['note']}` — {d['file']}:{d['line']}")
    dyn_lines += ["", "</details>"]

    cells = [
        _md(f"# modelopt PTQ ↔ transformers compatibility",
            "",
            f"**modelopt** `{modelopt_version}`  ·  **transformers** `{lo}`–`{hi}`  ·  "
            f"**{len(probed)}** versions probed  ·  generated {generated}",
            "",
            coverage,
            "",
            f"| symbols | compatible | never | signature drift ⚇ | dynamic | env errors |",
            f"|:--:|:--:|:--:|:--:|:--:|:--:|",
            f"| **{s['symbols']}** | {s['with_window']} | {s['never']} | {s['drift']} | "
            f"{s['dynamic']} | {s['env_errors']} |"),
        _md("## Versions actually probed",
            f"Bisection directly tested **{len(probed)}** of **{len(all_versions)}** stable "
            f"releases in `{lo}`–`{hi}`. The compatible window is **inferred** from these "
            "samples — versions marked N/A below were **not** tested.",
            "",
            "**✓ probed:** " + ", ".join(f"`{v}`" for v in probed),
            "",
            ("**– N/A (not tested):** " + ", ".join(f"`{v}`" for v in na_versions))
            if na_versions else "_All in-range releases were probed._"),
        _md("## Per-symbol compatibility",
            "",
            "The **compatible window** is the authoritative result; **support** is "
            "🟩 full · 🟨 partial · 🟥 never across probed versions.",
            "",
            *tbl),
        _md("## Support grid <sub>(by minor version)</sub>",
            "",
            "🟩 yes · 🟨 partial / symbol missing · 🟥 no / module missing · ⬜ N/A",
            "",
            *grid),
        _md("## ⚇ Signature changes",
            "*A symbol that still imports but whose signature changed within its window — "
            "the \"imports fine, breaks at runtime\" risk.*",
            "",
            *drift_lines),
        _md("## ✗ Never compatible",
            "*Architecture absent from this transformers range.*",
            "",
            *never_lines),
        _md(*dyn_lines),
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
    probed = matrix["versions_probed"]
    all_versions = fetch_full_range(probed[0], probed[-1], probed) if probed else []

    os.makedirs(args.outdir, exist_ok=True)
    html_path = os.path.join(args.outdir, "compatibility.html")
    ipynb_path = os.path.join(args.outdir, "compatibility.ipynb")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(build_html(matrix, args.modelopt_version, args.generated, all_versions))
    with open(ipynb_path, "w", encoding="utf-8") as fh:
        json.dump(build_ipynb(matrix, args.modelopt_version, args.generated, all_versions),
                  fh, indent=1, ensure_ascii=False)
    print("wrote", html_path)
    print("wrote", ipynb_path)


if __name__ == "__main__":
    main()
