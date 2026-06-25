from modelopt_ptq_transformers_doctor import smoke


def _stages(fail_at=None, exc=RuntimeError("boom")):
    """Build a stages dict that raises at *fail_at* (load/quantize/export)."""
    calls = []

    def mk(name):
        def fn(model=None):
            calls.append(name)
            if name == fail_at:
                raise exc
            return f"model-after-{name}"
        return fn

    return {"load": mk("load"), "quantize": mk("quantize"), "export": mk("export")}, calls


def test_all_stages_ok():
    stages, calls = _stages()
    r = smoke.run_smoke(stages)
    assert r["status"] == "OK" and r["reached"] == "done"
    assert calls == ["load", "quantize", "export"]


def test_load_failure_stops_early():
    stages, calls = _stages(fail_at="load", exc=AttributeError("'NemotronHConfig' object has no attribute 'moe_latent_size'"))
    r = smoke.run_smoke(stages)
    assert r["status"] == "LOAD_ERROR" and r["reached"] == "load"
    assert r["error_type"] == "AttributeError" and "moe_latent_size" in r["error"]
    assert calls == ["load"]  # did not proceed to quantize/export


def test_quantize_failure():
    stages, _ = _stages(fail_at="quantize")
    r = smoke.run_smoke(stages)
    assert r["status"] == "QUANTIZE_ERROR" and r["reached"] == "quantize"


def test_export_failure_classified():
    stages, calls = _stages(fail_at="export",
                            exc=NotImplementedError("MoE model with experts type 'NemotronHExperts' is not supported in export."))
    r = smoke.run_smoke(stages)
    assert r["status"] == "EXPORT_ERROR" and r["reached"] == "export"
    assert r["error_type"] == "NotImplementedError" and "NemotronHExperts" in r["error"]
    assert calls == ["load", "quantize", "export"]


def test_error_message_truncated():
    stages, _ = _stages(fail_at="quantize", exc=RuntimeError("x" * 5000))
    r = smoke.run_smoke(stages)
    assert len(r["error"]) <= 500


def test_build_smoke_matrix_probes_each_version_in_order():
    seen = []

    def fake(v):
        seen.append(v)
        return {"reached": "export", "status": "EXPORT_ERROR", "error_type": "NotImplementedError",
                "error": "x"} if v == "5.5.0" else {"reached": "done", "status": "OK",
                                                     "error_type": None, "error": None}

    m = smoke.build_smoke_matrix(["4.50.0", "5.5.0"], fake)
    assert seen == ["4.50.0", "5.5.0"]
    assert m["4.50.0"]["status"] == "OK" and m["5.5.0"]["status"] == "EXPORT_ERROR"
