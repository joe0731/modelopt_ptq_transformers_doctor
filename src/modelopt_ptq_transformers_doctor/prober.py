"""Standalone import-level prober. Runs inside a foreign uv env: stdlib only."""

import importlib
import inspect
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
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    main()
