from modelopt_ptq_transformers_doctor.targets import TARGETS, Target


def test_four_targets_present():
    assert set(TARGETS) == {"transformers", "torch", "vllm", "accelerate"}


def test_each_target_well_formed():
    for name, t in TARGETS.items():
        assert isinstance(t, Target) and t.name == name
        assert t.pypi and t.import_roots and t.files
        assert all(f.endswith(".py") for f in t.files)


def test_transformers_target_matches_legacy_allowlist():
    from modelopt_ptq_transformers_doctor import allowlist
    t = TARGETS["transformers"]
    assert t.import_roots == ("transformers",)
    assert set(t.quant_files) == set(allowlist.QUANT_FILES)
    assert set(t.export_files) == set(allowlist.EXPORT_FILES)
    assert t.role_of(allowlist.QUANT_FILES[0]) == "quant"


def test_pinned_deps_isolation():
    assert TARGETS["torch"].pinned_deps  # pins transformers/accelerate
    assert TARGETS["vllm"].pinned_deps == ()  # vllm dictates torch
    assert any("torch" in d for d in TARGETS["accelerate"].pinned_deps)
