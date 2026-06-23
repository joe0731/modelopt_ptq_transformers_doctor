from modelopt_ptq_transformers_doctor.models import (
    ContractRecord, OK, MISSING_MODULE, MISSING_SYMBOL, ENV_ERROR, PROBE_ERROR,
)


def test_status_constants_have_exact_values():
    assert (OK, MISSING_MODULE, MISSING_SYMBOL, ENV_ERROR, PROBE_ERROR) == (
        "OK", "MISSING_MODULE", "MISSING_SYMBOL", "ENV_ERROR", "PROBE_ERROR",
    )


def test_record_key_combines_module_and_symbol():
    r = ContractRecord("transformers.models.t5.modeling_t5", "T5Attention",
                       "f.py", 10, guarded=False, dynamic=False, role="quant")
    assert r.key == "transformers.models.t5.modeling_t5:T5Attention"


def test_record_roundtrips_through_dict():
    r = ContractRecord("transformers.pytorch_utils", "Conv1D",
                       "f.py", 5, guarded=True, dynamic=False, role="quant")
    assert ContractRecord.from_dict(r.to_dict()) == r
