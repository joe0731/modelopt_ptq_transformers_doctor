from modelopt_ptq_transformers_doctor import cli
from modelopt_ptq_transformers_doctor.models import ContractRecord


def test_parser_accepts_bounds_without_modelopt_flag():
    p = cli.build_arg_parser()
    ns = p.parse_args(["scan", "--min", "4.48.0", "--max", "4.52.0"])
    assert ns.min == "4.48.0" and ns.max == "4.52.0"
    assert not hasattr(ns, "modelopt")


def test_main_end_to_end_with_monkeypatched_seams(tmp_path, monkeypatch):
    rec = ContractRecord("transformers.models.x.modeling_x", "XAttn",
                         "f.py", 1, guarded=False, dynamic=False, role="quant")
    monkeypatch.setattr(cli, "installed_modelopt_root", lambda: "/x")
    monkeypatch.setattr(cli, "extract_contract", lambda root: [rec])
    monkeypatch.setattr(cli, "fetch_available_versions",
                        lambda: ["4.48.0", "4.49.0", "4.50.0"])

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

    def boom(root):
        raise FileNotFoundError("missing allowlist file")
    monkeypatch.setattr(cli, "extract_contract", boom)
    rc = cli.main(["scan", "--out", str(tmp_path / "o")])
    assert rc == 2
