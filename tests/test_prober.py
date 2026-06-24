import json
import subprocess
import sys
from pathlib import Path

from modelopt_ptq_transformers_doctor import prober

PROBER = Path(prober.__file__)


def test_probe_one_ok_for_real_stdlib_symbol():
    assert prober.probe_one("json", "dumps") == "OK"


def test_probe_one_missing_module():
    assert prober.probe_one("definitely_not_a_module_xyz", "X") == "MISSING_MODULE"


def test_probe_one_missing_symbol():
    assert prober.probe_one("json", "no_such_attr_xyz") == "MISSING_SYMBOL"


def test_probe_one_none_symbol_is_ok_when_module_imports():
    assert prober.probe_one("json", None) == "OK"


def test_probe_records_skips_dynamic_and_builds_keys():
    recs = [
        {"module_path": "json", "symbol": "dumps", "dynamic": False},
        {"module_path": "json", "symbol": "nope_xyz", "dynamic": False},
        {"module_path": "", "symbol": "mod_type", "dynamic": True},
    ]
    out = prober.probe_records(recs)
    assert out == {"json:dumps": "OK", "json:nope_xyz": "MISSING_SYMBOL"}


def test_main_runs_as_subprocess_via_stdin_stdout():
    payload = json.dumps({"records": [{"module_path": "json", "symbol": "dumps",
                                       "dynamic": False}]})
    proc = subprocess.run([sys.executable, str(PROBER)], input=payload,
                          capture_output=True, text=True, check=True)
    out = json.loads(proc.stdout)
    assert out["statuses"] == {"json:dumps": "OK"}
    assert "transformers_version" in out


def test_fingerprint_function_is_signature_string():
    assert prober.fingerprint(lambda x, y=1: None) == "(x, y=1)"


def test_fingerprint_class_uses_init_signature():
    class C:
        def __init__(self, a, b=2):
            pass
    assert prober.fingerprint(C) == "(a, b=2)"


def test_fingerprint_non_callable_is_type_name():
    assert prober.fingerprint({}) == "dict"
    assert prober.fingerprint([1]) == "list"


def test_fingerprint_falls_back_when_signature_unavailable(monkeypatch):
    def boom(_obj):
        raise ValueError("no signature")
    monkeypatch.setattr(prober.inspect, "signature", boom)
    assert prober.fingerprint(lambda: None) == "<no-signature>"


def test_probe_signatures_only_ok_non_dynamic():
    import inspect as _inspect
    import json as _json
    recs = [
        {"module_path": "json", "symbol": "dumps", "dynamic": False},
        {"module_path": "json", "symbol": "nope_xyz", "dynamic": False},
        {"module_path": "", "symbol": "mod_type", "dynamic": True},
    ]
    sigs = prober.probe_signatures(recs)
    assert sigs == {"json:dumps": str(_inspect.signature(_json.dumps))}


def test_main_subprocess_includes_signatures():
    payload = json.dumps({"records": [{"module_path": "json", "symbol": "dumps",
                                       "dynamic": False}]})
    proc = subprocess.run([sys.executable, str(PROBER)], input=payload,
                          capture_output=True, text=True, check=True)
    out = json.loads(proc.stdout)
    assert "json:dumps" in out["signatures"]
