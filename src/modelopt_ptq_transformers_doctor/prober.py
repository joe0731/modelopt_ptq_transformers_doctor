"""Standalone import-level prober. Runs inside a foreign uv env: stdlib only."""

import importlib
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


def _transformers_version():
    try:
        import transformers
        return getattr(transformers, "__version__", None)
    except Exception:
        return None


def main():
    payload = json.load(sys.stdin)
    out = {
        "transformers_version": _transformers_version(),
        "statuses": probe_records(payload["records"]),
    }
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    main()
