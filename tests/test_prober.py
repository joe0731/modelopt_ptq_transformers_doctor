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
