#!/usr/bin/env python3
"""Render a doctor ``matrix.json`` into human-facing artifacts:

* ``compatibility.html`` — a polished, colour-graded standalone page, and
* ``compatibility.ipynb`` — a clean, results-only notebook (markdown only).

Each probed version is shown as yes / no; in-range versions not directly
probed are shown as N/A. Stdlib only (plus ``packaging``); the page styling
lives in ``assets/compat.css`` and is inlined at build time.

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

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(HERE, "assets")

# probe status -> (emoji square, css class, short label)
STATUS = {
    "OK":             ("🟩", "ok",   "yes"),
    "MISSING_SYMBOL": ("🟨", "warn", "no·sym"),
    "MISSING_MODULE": ("🟥", "bad",  "no·mod"),
    "ENV_ERROR":      ("🟦", "env",  "env"),
    "PROBE_ERROR":    ("🟦", "env",  "probe"),
}
NA = ("⬜", "na", "N/A")
GLYPH = {"ok": "✓", "warn": "~", "bad": "✗", "env": "!", "na": "–"}
CHANGE_SIGN = {"add": "+", "del": "−", "mod": "~", "ret": "↩"}


def esc(x) -> str:
    return html.escape(str(x))


# ============================================================ data helpers

def short(key: str) -> str:
    return key.split(":")[-1]


def minor(v: str) -> str:
    p = v.split(".")
    return ".".join(p[:2]) if len(p) >= 2 else v


_MODEL_LABELS = {
    "dbrx": "DBRX",
    "gpt_oss": "GPT-OSS",
    "llama4": "Llama 4",
    "mixtral": "Mixtral",
    "nemotron_h": "Nemotron-H",
    "qwen3_5_moe": "Qwen3.5 MoE",
    "qwen3_moe": "Qwen3 MoE",
    "qwen3_vl_moe": "Qwen3 VL MoE",
    "t5": "T5",
}


def affected_models(key: str) -> str:
    module_path = key.split(":", 1)[0]
    parts = module_path.split(".")
    if "models" in parts:
        idx = parts.index("models")
        if idx + 1 < len(parts):
            family = parts[idx + 1]
            return _MODEL_LABELS.get(family, family.replace("_", " ").title())
    if module_path.startswith("transformers"):
        return "shared / cross-family"
    if module_path.startswith("torch"):
        return "all torch-backed models"
    if module_path.startswith("vllm"):
        return "vLLM serving path"
    if module_path.startswith("accelerate"):
        return "accelerate loading/offload path"
    return "unknown"


def range_str(ranges) -> str:
    return "never" if not ranges else ", ".join(f"{lo} – {hi}" for lo, hi in ranges)


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
    return sum(1 for v in probed if info["statuses"].get(v) == "OK") / len(probed)


def minor_status(info: dict, mn: str, all_versions: list[str], probed: set) -> tuple[str, str]:
    """Aggregate one feature (minor) version into (css_class, tooltip):
    green=all probed patches OK, red=all module-missing, amber=mixed/symbol
    missing, na=no patch in this minor was probed."""
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


# ============================================================ signature diff

def _split_sig(sig: str):
    """Split a signature string '(a, b=1) -> r' into (params, ret), or
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
    """Readable change list between two signature fingerprints as a list of
    (kind, text) with kind in {add, del, mod, ret}; None if either is opaque."""
    po, ro = _split_sig(old_fp)
    pn, rn = _split_sig(new_fp)
    if po is None or pn is None:
        return None
    om, nm = {}, {}
    for p in po:
        om.setdefault(_pname(p), p)
    for p in pn:
        nm.setdefault(_pname(p), p)
    out = [("add", p) for k, p in nm.items() if k not in om]
    out += [("del", p) for k, p in om.items() if k not in nm]
    out += [("mod", f"{om[k]}  →  {p}") for k, p in nm.items() if k in om and om[k] != p]
    if ro != rn:
        out.append(("ret", f"return {ro or '(none)'} → {rn or '(none)'}"))
    return out


def drift_steps(seq):
    """Yield (vo, vn, changes) per transition; changes is the sig_changes list
    (possibly None for opaque, or [] for formatting-only)."""
    for (vo, fo), (vn, fn) in zip(seq, seq[1:]):
        yield vo, vn, sig_changes(fo, fn), fo, fn


# ============================================================ version discovery

def fetch_full_range(lo: str, hi: str, probed: list[str], pkg: str = "transformers") -> list[str]:
    """All stable releases of *pkg* in [lo, hi]; falls back to *probed*."""
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{pkg}/json", timeout=30) as r:
            data = json.loads(r.read())
        lov, hiv = Version(lo), Version(hi)
        out = []
        for raw in data.get("releases", {}):
            try:
                v = Version(raw)
            except InvalidVersion:
                continue
            if not (v.is_prerelease or v.is_devrelease) and lov <= v <= hiv:
                out.append(raw)
        return sorted(set(out) | set(probed), key=Version)
    except Exception:
        return sorted(probed, key=Version)


# ============================================================ HTML sections

def _css() -> str:
    with open(os.path.join(ASSET_DIR, "compat.css"), encoding="utf-8") as fh:
        return fh.read()


def _support_bar(frac: float) -> str:
    pct = round(frac * 100)
    hue = round(120 * frac)  # 0=red -> 120=green
    return (f"<div class='bar'><span style='width:{pct}%;background:hsl({hue} 70% 45%)'></span></div>"
            f"<small>{pct}%</small>")


def _cards(s: dict) -> str:
    items = [
        (s["symbols"], "dependency symbols"),
        (s["with_window"], "with compatible ranges"),
        (s["never"], "never compatible"),
        (s["drift"], "signature drift ⚇"),
        (s["dynamic"], "dynamic (unchecked)"),
        (s["env_errors"], "env errors"),
    ]
    cards = "".join(f"<div class='card'><b>{n}</b><span>{label}</span></div>" for n, label in items)
    return f"<div class='cards'>{cards}</div>"


def _probed_block(probed: list[str], all_versions: list[str]) -> str:
    na = [v for v in all_versions if v not in set(probed)]
    probed_chips = " ".join(f"<span class='chip'>{esc(v)}</span>" for v in probed)
    na_chips = " ".join(f"<span class='chip na'>{esc(v)}</span>" for v in na)
    na_row = f"<div class='chips'><b>– N/A, not tested ({len(na)}):</b> {na_chips}</div>" if na else ""
    return (
        f"<details open class='probed'><summary><b>{len(probed)}</b> of {len(all_versions)} "
        "in-range releases were <b>actually probed</b> — the rest are <b>N/A</b> "
        "(not directly tested)</summary>"
        f"<div class='chips'><b>✓ probed ({len(probed)}):</b> {probed_chips}</div>{na_row}</details>"
    )


def _coverage(probed: list[str], all_versions: list[str]) -> str:
    na = len(all_versions) - len(probed)
    if na <= 0:
        return (f"All <b>{len(probed)}</b> stable releases in range were probed directly "
                "(yes/no determined by test; no inferred cells).")
    return (f"<b>{len(probed)}</b> of {len(all_versions)} in-range releases were probed; "
            f"the other {na} are <b>N/A</b> (not directly tested).")


def _per_symbol_table(symbols, probed: list[str]) -> str:
    rows = []
    for key, info in symbols:
        drift = ("<span class='tag drift' title='signature changed within compatible ranges'>⚇ drift</span>"
                 if info.get("signature_drift") else "")
        guard = "<span class='tag guard'>🛡</span>" if info["guarded"] else ""
        win = ("<span class='never'>never</span>" if not info["compatible_ranges"]
               else esc(range_str(info["compatible_ranges"])))
        rows.append(
            f"<tr><td class='sym'><code>{esc(key)}</code> {guard}{drift}</td>"
            f"<td>{esc(affected_models(key))}</td><td>{esc(info['role'])}</td><td>{win}</td>"
            f"<td class='supcell'>{_support_bar(support_frac(info, probed))}</td></tr>"
        )
    return ("<h2>Per-symbol compatibility <small>(ranges are validated from probed versions)</small></h2>"
            "<table><thead><tr><th>symbol</th><th>affected models</th><th>role</th>"
            "<th>compatible ranges <small>(validated)</small></th><th>support</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>")


def _support_grid(symbols, minors, all_versions, probed_set, probed) -> str:
    probed_minors = {minor(v) for v in probed}
    head = "".join(f"<th class='vh{' na' if mn not in probed_minors else ''}'>{esc(mn)}</th>"
                   for mn in minors)
    rows = []
    for key, info in symbols:
        cells = "".join(
            (lambda c, tip: f"<td class='{c}' title='{esc(tip)}'>{GLYPH[c]}</td>")(
                *minor_status(info, mn, all_versions, probed_set))
            for mn in minors
        )
        rows.append(f"<tr><th class='rsym'><code>{esc(key)}</code></th>{cells}</tr>")
    return ("<h2>Support grid <small>(symbol × feature version — colour = compatibility; "
            "hover for patch detail)</small></h2>"
            f"<div class='grid-wrap'><table><tr><th class='rsym'>symbol</th>{head}</tr>"
            f"{''.join(rows)}</table></div>")


def _drift_section(symbols) -> str:
    drifts = [(k, i) for k, i in symbols if i.get("signature_drift")]
    if not drifts:
        return ""
    items = []
    for k, info in drifts:
        steps = []
        for vo, vn, chg, fo, fn in drift_steps(info["signature_drift"]):
            vhead = f"<span class='v'>{esc(vo)} → {esc(vn)}</span>"
            if chg is None:
                body = f"<code>{esc(fo)}</code> <span class='arr'>→</span> <code>{esc(fn)}</code>"
            elif len(chg) > 6:
                nb = {kk: sum(1 for t, _ in chg if t == kk) for kk in CHANGE_SIGN}
                detail = "".join(f"<div class='cz {t}'>{esc(CHANGE_SIGN[t])} {esc(txt)}</div>" for t, txt in chg)
                body = (f"<span class='cz mod'>+{nb['add']} −{nb['del']} ~{nb['mod']} params (major rewrite)</span>"
                        f"<details><summary>details</summary>{detail}</details>")
            elif chg:
                body = "".join(f"<div class='cz {t}'>{esc(CHANGE_SIGN[t])} {esc(txt)}</div>" for t, txt in chg)
            else:
                body = "<div class='cz'>(reordered / formatting only)</div>"
            steps.append(f"<div class='step'>{vhead}{body}</div>")
        items.append(f"<li><code>{esc(k)}</code>{''.join(steps)}</li>")
    return ("<h2>⚇ Signature changes <small>(within compatible ranges — what actually changed)"
            "</small></h2><ul class='drift'>" + "".join(items) + "</ul>")


def _never_section(symbols) -> str:
    never = [k for k, i in symbols if not i["compatible_ranges"]]
    if not never:
        return ""
    items = "".join(f"<li><code>{esc(k)}</code></li>" for k in never)
    return ("<h2>✗ Never compatible <small>(architecture absent in this range)</small></h2>"
            f"<ul class='never-list'>{items}</ul>")


def _dynamic_section(matrix: dict) -> str:
    dyn = matrix.get("dynamic", [])
    if not dyn:
        return ""
    items = "".join(f"<li><code>{esc(d['note'])}</code> "
                    f"<span class='loc'>{esc(d['file'])}:{esc(d['line'])}</span></li>" for d in dyn)
    return (f"<details><summary>Dynamic registrations ({len(dyn)}) — runtime-discovered, "
            f"not statically checkable</summary><ul class='dyn'>{items}</ul></details>")


def _legend() -> str:
    rows = [
        ("var(--ok)", "✓ yes (imports OK)"),
        ("var(--warn)", "~ partial / symbol missing"),
        ("var(--bad)", "✗ no · module missing"),
        ("var(--env)", "! env/probe error"),
        ("#d0d7de", "– N/A (not tested)"),
    ]
    swatches = "".join(f"<span><span class='sw' style='background:{bg}'></span>{esc(t)}</span>"
                       for bg, t in rows)
    return f"<div class='legend'>{swatches}<span>🛡 guarded import · ⚇ signature drift</span></div>"


def build_html(matrix: dict, modelopt_version: str, generated: str, all_versions: list[str]) -> str:
    probed = matrix["versions_probed"]
    probed_set = set(probed)
    symbols = sorted(matrix["symbols"].items())
    minors = sorted({minor(v) for v in all_versions}, key=Version)
    lo, hi = (all_versions[0], all_versions[-1]) if all_versions else ("?", "?")
    s = summary(matrix)
    target_label = matrix.get("target", "transformers")
    strategy = matrix.get("strategy", "legacy")

    body = "\n  ".join([
        _probed_block(probed, all_versions),
        _per_symbol_table(symbols, probed),
        _support_grid(symbols, minors, all_versions, probed_set, probed),
        _drift_section(symbols),
        _never_section(symbols),
        _dynamic_section(matrix),
        _legend(),
    ])

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>modelopt {esc(modelopt_version)} ↔ {esc(target_label)} compatibility</title>
<style>
{_css()}
</style></head>
<body>
<header>
  <h1>modelopt PTQ ↔ {esc(target_label)} compatibility</h1>
  <div class="meta">modelopt <b>{esc(modelopt_version)}</b> &nbsp;·&nbsp; {esc(target_label)} <b>{esc(lo)} – {esc(hi)}</b>
   &nbsp;·&nbsp; {len(probed)} versions probed &nbsp;·&nbsp; strategy {esc(strategy)} &nbsp;·&nbsp; generated {esc(generated)}</div>
</header>
<main>
  <div class="note">{_coverage(probed, all_versions)} Compatible ranges are built only from directly probed OK versions. Scan strategy: {esc(strategy)}.</div>
  {_cards(s)}
  {body}
</main>
</body></html>
"""


# ============================================================ notebook (md only)

def _md(*lines):
    return {"cell_type": "markdown", "metadata": {}, "source": [l + "\n" for l in lines]}


def _nb_support_emoji(info, probed):
    f = support_frac(info, probed)
    return "🟩" if f == 1 else ("🟥" if f == 0 else "🟨")


def _nb_minor_cell(info, mn, probed):
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


def build_ipynb(matrix: dict, modelopt_version: str, generated: str, all_versions: list[str]) -> dict:
    probed = matrix["versions_probed"]
    probed_set = set(probed)
    symbols = sorted(matrix["symbols"].items())
    minors = sorted({minor(v) for v in all_versions}, key=Version)
    lo, hi = (all_versions[0], all_versions[-1]) if all_versions else ("?", "?")
    s = summary(matrix)
    na = [v for v in all_versions if v not in probed_set]
    target_label = matrix.get("target", "transformers")

    coverage = (f"All **{len(probed)}** stable releases in `{lo}`–`{hi}` were probed directly "
                "— yes/no determined by test, no inferred (N/A) cells." if not na else
                f"**{len(probed)}** of {len(all_versions)} in-range releases were probed directly; "
                f"the other **{len(na)}** are N/A (not tested).")

    tbl = ["| symbol | affected models | role | compatible ranges (validated) | support | |",
           "|---|---|---|---|:--:|:--:|"]
    for key, info in symbols:
        win = range_str(info["compatible_ranges"])
        win = "**never**" if win == "never" else win
        tbl.append(f"| `{key}` | {affected_models(key)} | {info['role']} | {win} | "
                   f"{_nb_support_emoji(info, probed)} | {'⚇' if info.get('signature_drift') else ''} |")

    grid = ["| symbol | " + " | ".join(minors) + " |",
            "|---|" + "|".join([":--:"] * len(minors)) + "|"]
    for key, info in symbols:
        grid.append(f"| `{key}` | " + " | ".join(_nb_minor_cell(info, mn, probed) for mn in minors) + " |")

    drift_lines = []
    drifts = [(k, i) for k, i in symbols if i.get("signature_drift")]
    if drifts:
        for k, info in drifts:
            drift_lines.append(f"**`{k}`**")
            for vo, vn, chg, fo, fn in drift_steps(info["signature_drift"]):
                if chg is None:
                    drift_lines.append(f"- `{vo} → {vn}` — `{fo}` → `{fn}`")
                elif len(chg) > 6:
                    nb = {kk: sum(1 for t, _ in chg if t == kk) for kk in CHANGE_SIGN}
                    drift_lines.append(f"- `{vo} → {vn}` — **+{nb['add']} −{nb['del']} ~{nb['mod']}** params (major rewrite)")
                elif chg:
                    drift_lines.append(f"- `{vo} → {vn}` — " + "; ".join(f"{CHANGE_SIGN[t]} `{txt}`" for t, txt in chg))
                else:
                    drift_lines.append(f"- `{vo} → {vn}` — (reordered / formatting only)")
            drift_lines.append("")
    else:
        drift_lines = ["_No signature drift detected._"]

    never = [k for k, i in symbols if not i["compatible_ranges"]]
    never_lines = [f"- `{k}`" for k in never] if never else ["_None._"]

    dyn_lines = ["<details><summary>"
                 f"{len(matrix.get('dynamic', []))} dynamic registrations "
                 "(runtime-discovered, not statically checkable)</summary>", ""]
    dyn_lines += [f"- `{d['note']}` — {d['file']}:{d['line']}" for d in matrix.get("dynamic", [])]
    dyn_lines += ["", "</details>"]

    cells = [
        _md(f"# modelopt PTQ ↔ {target_label} compatibility", "",
            f"**modelopt** `{modelopt_version}`  ·  **{target_label}** `{lo}`–`{hi}`  ·  "
            f"**{len(probed)}** versions probed  ·  generated {generated}", "",
            coverage, "",
            "| symbols | compatible | never | signature drift ⚇ | dynamic | env errors |",
            "|:--:|:--:|:--:|:--:|:--:|:--:|",
            f"| **{s['symbols']}** | {s['with_window']} | {s['never']} | {s['drift']} | "
            f"{s['dynamic']} | {s['env_errors']} |"),
        _md("## Versions actually probed",
            f"The scan directly tested **{len(probed)}** of **{len(all_versions)}** stable "
            f"releases in `{lo}`–`{hi}`. Compatible ranges are built only from "
            "tested versions; versions marked N/A below were **not** tested.", "",
            "**✓ probed:** " + ", ".join(f"`{v}`" for v in probed), "",
            ("**– N/A (not tested):** " + ", ".join(f"`{v}`" for v in na)) if na
            else "_All in-range releases were probed._"),
        _md("## Per-symbol compatibility", "",
            "The **compatible ranges** are validated from probed versions; **support** is "
            "🟩 full · 🟨 partial · 🟥 never across probed versions.", "", *tbl),
        _md("## Support grid <sub>(by minor version)</sub>", "",
            "🟩 yes · 🟨 partial / symbol missing · 🟥 no / module missing · ⬜ N/A", "", *grid),
        _md("## ⚇ Signature changes",
            "*A symbol that still imports but whose signature changed within compatible ranges — "
            "the \"imports fine, breaks at runtime\" risk.*", "", *drift_lines),
        _md("## ✗ Never compatible", "*Architecture absent from this transformers range.*", "",
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
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("matrix")
    ap.add_argument("--modelopt-version", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--generated", default=datetime.date.today().isoformat())
    args = ap.parse_args()

    with open(args.matrix, encoding="utf-8") as fh:
        matrix = json.load(fh)
    probed = matrix["versions_probed"]
    pkg = matrix.get("pypi", "transformers")
    all_versions = fetch_full_range(probed[0], probed[-1], probed, pkg=pkg) if probed else []

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
