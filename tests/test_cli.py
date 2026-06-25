import os
import sys

import pytest

from modelopt_ptq_transformers_doctor import cli
from modelopt_ptq_transformers_doctor import progress as progress_mod
from modelopt_ptq_transformers_doctor.models import ContractRecord
from modelopt_ptq_transformers_doctor.targets import TARGETS


def test_parser_accepts_bounds_without_modelopt_flag():
    p = cli.build_arg_parser()
    ns = p.parse_args(["scan", "--min", "4.48.0", "--max", "4.52.0"])
    assert ns.min == "4.48.0" and ns.max == "4.52.0"
    assert not hasattr(ns, "modelopt")


def test_main_end_to_end_with_monkeypatched_seams(tmp_path, monkeypatch):
    rec = ContractRecord("transformers.models.x.modeling_x", "XAttn",
                         "f.py", 1, guarded=False, dynamic=False, role="quant")
    monkeypatch.setattr(cli, "installed_modelopt_root", lambda: "/x")
    monkeypatch.setattr(cli, "extract_contract", lambda root, target=None: [rec])
    monkeypatch.setattr(cli, "fetch_available_versions",
                        lambda pkg="transformers": ["4.48.0", "4.49.0", "4.50.0"])

    class FakeRunner:
        def __init__(self, *a, **k):
            pass

        def probe_version(self, version, records):
            ok = int(version.split(".")[1]) >= 49
            return {"status": "OK", "installed": version,
                    "statuses": {f"{r['module_path']}:{r['symbol']}":
                                 ("OK" if ok else "MISSING_SYMBOL") for r in records}}

    monkeypatch.setattr(cli, "EnvRunner", FakeRunner)
    out = tmp_path / "report"
    rc = cli.main(["scan", "--min", "4.48.0", "--max", "4.50.0", "--out", str(out)])
    assert rc == 0
    assert (out / "matrix.json").exists() and (out / "REPORT.md").exists()
    assert "XAttn" in (out / "REPORT.md").read_text()


def test_main_returns_nonzero_when_modelopt_not_installed(monkeypatch, tmp_path, capsys):
    def boom():
        raise ModuleNotFoundError("modelopt is not installed in this environment.")
    monkeypatch.setattr(cli, "installed_modelopt_root", boom)
    rc = cli.main(["scan", "--out", str(tmp_path / "o")])
    assert rc == 2
    assert "modelopt is not installed" in capsys.readouterr().err


def test_main_returns_nonzero_when_extraction_fails(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "installed_modelopt_root", lambda: "/x")

    def boom(root, target=None):
        raise FileNotFoundError("missing allowlist file")
    monkeypatch.setattr(cli, "extract_contract", boom)
    rc = cli.main(["scan", "--out", str(tmp_path / "o")])
    assert rc == 2


def test_parser_accepts_no_progress_flag():
    p = cli.build_arg_parser()
    ns = p.parse_args(["scan", "--no-progress"])
    assert ns.no_progress is True
    ns2 = p.parse_args(["scan"])
    assert ns2.no_progress is False


def test_no_progress_uses_null_reporter(tmp_path, monkeypatch):
    rec = ContractRecord("transformers.models.x.modeling_x", "XAttn",
                         "f.py", 1, guarded=False, dynamic=False, role="quant")
    monkeypatch.setattr(cli, "installed_modelopt_root", lambda: "/x")
    monkeypatch.setattr(cli, "extract_contract", lambda root, target=None: [rec])
    monkeypatch.setattr(cli, "fetch_available_versions",
                        lambda pkg="transformers": ["4.48.0", "4.49.0"])

    class FakeRunner:
        def __init__(self, *a, **k):
            pass

        def probe_version(self, version, records):
            return {"status": "OK", "installed": version,
                    "statuses": {f"{r['module_path']}:{r['symbol']}": "OK"
                                 for r in records}}

    monkeypatch.setattr(cli, "EnvRunner", FakeRunner)

    seen = {}

    def fake_build_matrix(records, versions, runner, reporter=None):
        seen["reporter"] = reporter
        return {"versions_probed": versions, "symbols": {}, "dynamic": [],
                "env_errors": {}}

    monkeypatch.setattr(cli, "build_matrix", fake_build_matrix)
    out = tmp_path / "report"
    rc = cli.main(["scan", "--min", "4.48.0", "--max", "4.49.0",
                   "--out", str(out), "--no-progress"])
    assert rc == 0
    assert isinstance(seen["reporter"], progress_mod.NullProgress)
    assert not isinstance(seen["reporter"], progress_mod.ProgressReporter)


def test_progress_on_by_default_uses_reporter(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "installed_modelopt_root", lambda: "/x")
    monkeypatch.setattr(cli, "extract_contract", lambda root, target=None: [])
    monkeypatch.setattr(cli, "fetch_available_versions", lambda pkg="transformers": ["4.48.0"])
    monkeypatch.setattr(cli, "select_versions", lambda available, mn, mx: ["4.48.0"])
    monkeypatch.setattr(cli, "EnvRunner", lambda *a, **k: object())

    seen = {}

    def fake_build_matrix(records, versions, runner, reporter=None):
        seen["reporter"] = reporter
        return {"versions_probed": versions, "symbols": {}, "dynamic": [],
                "env_errors": {}}

    monkeypatch.setattr(cli, "build_matrix", fake_build_matrix)
    rc = cli.main(["scan", "--min", "4.48.0", "--max", "4.48.0",
                   "--out", str(tmp_path / "r")])
    assert rc == 0
    assert isinstance(seen["reporter"], progress_mod.ProgressReporter)
    assert seen["reporter"].stream is sys.stderr


def test_target_default_is_transformers(capsys, monkeypatch, tmp_path):
    """--target defaults to transformers; out dir = doctor-report/transformers."""
    seen = {}

    monkeypatch.setattr(cli, "installed_modelopt_root", lambda: "/x")
    monkeypatch.setattr(cli, "extract_contract", lambda root, target=None: [])
    monkeypatch.setattr(cli, "fetch_available_versions",
                        lambda pkg="transformers": ["4.48.0"])
    monkeypatch.setattr(cli, "select_versions",
                        lambda available, mn, mx: ["4.48.0"])

    def fake_env_runner(*a, pkg=None, extra_deps=(), **k):
        seen["pkg"] = pkg
        seen["extra_deps"] = extra_deps
        return object()

    monkeypatch.setattr(cli, "EnvRunner", fake_env_runner)

    def fake_build_matrix(records, versions, runner, reporter=None):
        return {"versions_probed": versions, "symbols": {}, "dynamic": [],
                "env_errors": {}}

    monkeypatch.setattr(cli, "build_matrix", fake_build_matrix)

    def fake_write_report(matrix, out_dir):
        seen["out_dir"] = out_dir
        report_dir = tmp_path / "r"
        report_dir.mkdir(parents=True, exist_ok=True)
        json_p = report_dir / "matrix.json"
        md_p = report_dir / "REPORT.md"
        json_p.write_text("{}")
        md_p.write_text("# report")
        return json_p, md_p

    monkeypatch.setattr(cli, "write_report", fake_write_report)

    rc = cli.main(["scan", "--min", "4.48.0", "--max", "4.48.0", "--no-progress"])
    assert rc == 0
    assert seen["out_dir"] == os.path.join("doctor-report", "transformers")
    assert seen["pkg"] == "transformers"


def test_target_explicit(capsys, monkeypatch, tmp_path):
    """Explicit --target uses that target's pypi/deps/name."""
    non_transformers = [k for k in TARGETS if k != "transformers"]
    if not non_transformers:
        pytest.skip("only one target registered")

    target_key = non_transformers[0]
    target = TARGETS[target_key]
    seen = {}

    monkeypatch.setattr(cli, "installed_modelopt_root", lambda: "/x")
    monkeypatch.setattr(cli, "extract_contract", lambda root, target=None: [])
    monkeypatch.setattr(cli, "fetch_available_versions",
                        lambda pkg=target.pypi: ["1.0.0"])
    monkeypatch.setattr(cli, "select_versions",
                        lambda available, mn, mx: ["1.0.0"])

    def fake_env_runner(*a, pkg=None, extra_deps=(), **k):
        seen["pkg"] = pkg
        seen["extra_deps"] = extra_deps
        return object()

    monkeypatch.setattr(cli, "EnvRunner", fake_env_runner)

    def fake_build_matrix(records, versions, runner, reporter=None):
        return {"versions_probed": versions, "symbols": {}, "dynamic": [],
                "env_errors": {}}

    monkeypatch.setattr(cli, "build_matrix", fake_build_matrix)

    def fake_write_report(matrix, out_dir):
        seen["out_dir"] = out_dir
        report_dir = tmp_path / "r"
        report_dir.mkdir(parents=True, exist_ok=True)
        json_p = report_dir / "matrix.json"
        md_p = report_dir / "REPORT.md"
        json_p.write_text("{}")
        md_p.write_text("# report")
        return json_p, md_p

    monkeypatch.setattr(cli, "write_report", fake_write_report)

    rc = cli.main(["scan", "--target", target_key, "--no-progress"])
    assert rc == 0
    assert seen["pkg"] == target.pypi
    assert seen["extra_deps"] == target.pinned_deps
    assert seen["out_dir"] == os.path.join("doctor-report", target.name)


def test_capabilities_command(monkeypatch, capsys):
    monkeypatch.setattr(cli, "installed_modelopt_root", lambda: "/x")
    monkeypatch.setattr(cli, "screen_modelopt", lambda root: {
        "export_named": ["QuantDbrxExperts"], "export_fallbacks": ["iterable experts"],
        "quant_experts": ["_QuantDbrxExperts", "_QuantNonGatedFusedExperts"],
        "candidates": ["_QuantNonGatedFusedExperts"],
        "candidates_detail": [{"name": "_QuantNonGatedFusedExperts", "maybe_fallback": False}],
        "files_found": {}})
    rc = cli.main(["capabilities"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "_QuantNonGatedFusedExperts" in out and "screening" in out.lower()


def test_capabilities_in_parser():
    p = cli.build_arg_parser()
    assert p.parse_args(["capabilities"]).command == "capabilities"


def test_smoke_in_parser():
    p = cli.build_arg_parser()
    ns = p.parse_args(["smoke", "--model", "tiny", "--recipe", "FP8_DEFAULT_CFG"])
    assert ns.command == "smoke" and ns.model == "tiny" and ns.device == "cuda"


def test_smoke_command_ok(monkeypatch, capsys):
    def fake_build(model, recipe, device="cuda", trust_remote_code=False):
        return {"load": lambda: "m", "quantize": lambda m: "m", "export": lambda m: None}
    monkeypatch.setattr(cli, "build_real_stages", fake_build)
    rc = cli.main(["smoke", "--model", "tiny", "--recipe", "FP8_DEFAULT_CFG"])
    assert rc == 0 and "OK" in capsys.readouterr().out


def test_smoke_command_reports_export_failure(monkeypatch, capsys):
    def fake_build(model, recipe, device="cuda", trust_remote_code=False):
        def exp(m):
            raise NotImplementedError("experts type 'NemotronHExperts' is not supported in export.")
        return {"load": lambda: "m", "quantize": lambda m: "m", "export": exp}
    monkeypatch.setattr(cli, "build_real_stages", fake_build)
    rc = cli.main(["smoke", "--model", "x", "--recipe", "R"])
    out = capsys.readouterr().out
    assert rc == 0 and "EXPORT_ERROR" in out and "NemotronHExperts" in out


def test_smoke_matrix_command(monkeypatch, tmp_path):
    import json
    monkeypatch.setattr(cli, "fetch_available_versions", lambda pkg="transformers": ["5.11.0", "5.12.0"])
    monkeypatch.setattr(cli, "select_versions", lambda a, mn, mx: ["5.11.0", "5.12.0"])

    class FakeSmoke:
        def __init__(self, **k):
            pass

        def smoke_version(self, v, **k):
            if v == "5.12.0":
                return {"reached": "export", "status": "EXPORT_ERROR",
                        "error_type": "NotImplementedError", "error": "NemotronHExperts"}
            return {"reached": "done", "status": "OK", "error_type": None, "error": None}

    monkeypatch.setattr(cli, "SmokeEnvRunner", FakeSmoke)
    out = tmp_path / "sm"
    rc = cli.main(["smoke-matrix", "--model", "m", "--modelopt", "nvidia-modelopt==0.44.0",
                   "--out", str(out), "--min", "5.11.0", "--max", "5.12.0"])
    assert rc == 0
    d = json.loads((out / "smoke_matrix.json").read_text())
    assert d["results"]["5.12.0"]["status"] == "EXPORT_ERROR" and d["results"]["5.11.0"]["status"] == "OK"
    assert (out / "SMOKE.md").read_text().count("|") > 4
