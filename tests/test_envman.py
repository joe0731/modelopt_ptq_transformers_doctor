import json
import shutil
import subprocess
import types

import pytest

from modelopt_ptq_transformers_doctor.envman import EnvRunner

RECORDS = [{"module_path": "json", "symbol": "dumps", "dynamic": False}]


def _fake_run_factory(install_rc=0, probe_stdout=None, probe_rc=0):
    def fake_run(cmd, **kw):
        is_probe = any("prober" in str(c) for c in cmd)
        if is_probe:
            return types.SimpleNamespace(returncode=probe_rc, stdout=probe_stdout or "", stderr="")
        return types.SimpleNamespace(returncode=install_rc, stdout="", stderr="boom")
    return fake_run


def test_successful_probe_returns_statuses():
    out = json.dumps({"transformers_version": "4.50.0", "statuses": {"json:dumps": "OK"}})
    runner = EnvRunner("prober.py", runner=_fake_run_factory(probe_stdout=out))
    res = runner.probe_version("4.50.0", RECORDS)
    assert res["status"] == "OK"
    assert res["installed"] == "4.50.0"
    assert res["statuses"] == {"json:dumps": "OK"}


def test_install_failure_returns_env_error():
    runner = EnvRunner("prober.py", runner=_fake_run_factory(install_rc=1))
    res = runner.probe_version("9.9.9", RECORDS)
    assert res["status"] == "ENV_ERROR"
    assert res["statuses"] == {}


def test_prober_bad_output_returns_probe_error():
    runner = EnvRunner("prober.py", runner=_fake_run_factory(probe_stdout="not json"))
    res = runner.probe_version("4.50.0", RECORDS)
    assert res["status"] == "PROBE_ERROR"


def test_prober_nonzero_exit_returns_probe_error():
    runner = EnvRunner("prober.py", runner=_fake_run_factory(probe_stdout="{}", probe_rc=1))
    res = runner.probe_version("4.50.0", RECORDS)
    assert res["status"] == "PROBE_ERROR"


@pytest.mark.skipif(shutil.which("uv") is None, reason="uv not installed")
def test_integration_real_uv_probes_stdlib_symbol(tmp_path):
    from modelopt_ptq_transformers_doctor import prober
    runner = EnvRunner(prober.__file__, extra_deps=())
    res = runner.probe_version("4.46.0", RECORDS)
    assert res["status"] in {"OK", "ENV_ERROR"}  # OK unless offline / version pull fails
