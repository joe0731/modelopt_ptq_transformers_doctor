from modelopt_ptq_transformers_doctor.contract import extract_from_source


def _by_key(records):
    return {r.key: r for r in records}


def test_extracts_plain_from_import():
    src = "from transformers.models.t5.modeling_t5 import T5Attention\n"
    recs = _by_key(extract_from_source(src, "f.py", "quant"))
    r = recs["transformers.models.t5.modeling_t5:T5Attention"]
    assert r.symbol == "T5Attention" and r.guarded is False and r.dynamic is False
    assert r.role == "quant" and r.line == 1


def test_extracts_multi_symbol_import():
    src = "from transformers.models.dbrx.modeling_dbrx import DbrxExpertGLU, DbrxExperts\n"
    keys = {r.key for r in extract_from_source(src, "f.py", "quant")}
    assert "transformers.models.dbrx.modeling_dbrx:DbrxExpertGLU" in keys
    assert "transformers.models.dbrx.modeling_dbrx:DbrxExperts" in keys


def test_guarded_flag_set_inside_try_except_importerror():
    src = (
        "try:\n"
        "    from transformers.models.llama4.modeling_llama4 import Llama4TextExperts\n"
        "except ImportError:\n"
        "    pass\n"
    )
    r = _by_key(extract_from_source(src, "f.py", "quant"))[
        "transformers.models.llama4.modeling_llama4:Llama4TextExperts"]
    assert r.guarded is True


def test_unguarded_when_try_catches_other_exception():
    src = (
        "try:\n"
        "    from transformers.foo import Bar\n"
        "except ValueError:\n"
        "    pass\n"
    )
    r = _by_key(extract_from_source(src, "f.py", "quant"))["transformers.foo:Bar"]
    assert r.guarded is False


def test_extracts_capitalized_attribute_access():
    src = "import transformers\nx = transformers.pytorch_utils.Conv1D\n"
    keys = {r.key for r in extract_from_source(src, "f.py", "quant")}
    assert "transformers.pytorch_utils:Conv1D" in keys


def test_ignores_lowercase_attribute_access():
    src = "import transformers\nv = transformers.__version__\n"
    recs = extract_from_source(src, "f.py", "quant")
    assert all(r.symbol != "__version__" for r in recs)


def test_detects_dynamic_registration():
    src = (
        "for mod_type in types:\n"
        "    QuantModuleRegistry.register({mod_type: mod_type.__name__})(W)\n"
    )
    dyn = [r for r in extract_from_source(src, "f.py", "quant") if r.dynamic]
    assert len(dyn) == 1 and dyn[0].symbol == "mod_type"


def test_nested_capitalized_chain_not_double_counted():
    src = "import transformers\nx = transformers.SomeCls.AnotherCls\n"
    keys = [r.key for r in extract_from_source(src, "f.py", "quant")]
    assert keys == ["transformers.SomeCls:AnotherCls"]


def test_method_call_on_class_still_captures_class():
    src = "import transformers\ntransformers.Foo.bar()\n"
    keys = {r.key for r in extract_from_source(src, "f.py", "quant")}
    assert "transformers:Foo" in keys


def test_extract_contract_raises_for_missing_allowlist_file(tmp_path):
    import pytest
    from modelopt_ptq_transformers_doctor.contract import extract_contract
    with pytest.raises(FileNotFoundError) as exc:
        extract_contract(str(tmp_path))
    assert "modelopt/torch" in str(exc.value)


def test_guarded_flag_set_for_module_not_found_error():
    src = (
        "try:\n"
        "    from transformers.x import Y\n"
        "except ModuleNotFoundError:\n"
        "    pass\n"
    )
    r = _by_key(extract_from_source(src, "f.py", "quant"))["transformers.x:Y"]
    assert r.guarded is True


def _keys(src):
    return {r.key for r in extract_from_source(src, "f.py", "quant")}


def test_captures_lowercase_module_level_function():
    src = "import transformers\nx = transformers.models.llama.modeling_llama.eager_attention_forward\n"
    assert "transformers.models.llama.modeling_llama:eager_attention_forward" in _keys(src)


def test_does_not_capture_class_method_but_keeps_class():
    src = "import transformers\ny = transformers.AutoModelForCausalLM.from_pretrained\n"
    keys = _keys(src)
    assert "transformers:AutoModelForCausalLM" in keys
    assert "transformers.AutoModelForCausalLM:from_pretrained" not in keys


def test_skips_dunder_leaf():
    src = "import transformers\nv = transformers.__version__\n"
    assert not any(r.symbol == "__version__" for r in extract_from_source(src, "f.py", "quant"))
