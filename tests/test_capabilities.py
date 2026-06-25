from modelopt_ptq_transformers_doctor import capabilities as cap

EXPORT_SRC = '''
import collections.abc
def _export(model):
    for sub in model.modules():
        if "QuantDbrxExperts" in type(sub.experts).__name__:
            handle_dbrx()
        elif has_fused_experts_quantizers:
            break
        elif ("QuantGptOssExperts" in type(sub.experts).__name__
              or "QuantLlama4TextExperts" in type(sub.experts).__name__):
            handle_fused()
        elif isinstance(sub.experts, collections.abc.Iterable):
            handle_iterable()
        else:
            raise NotImplementedError(
                f"MoE model with experts type '{type(sub.experts).__name__}' is not supported in export.")
        if "QuantFP8Linear" in type(sub).__name__:  # not an experts check
            pass
'''

QUANT_SRC = '''
class _QuantDbrxExperts(QuantModule): pass
class _QuantGptOssExperts(Base): pass
class _QuantLlama4TextExperts(Base): pass
class _QuantQwen3VLMoeTextExperts(QuantModule): pass
class _QuantFusedExperts(Mixin): pass
class _QuantNonGatedFusedExperts(_QuantFusedExperts): pass
class _QuantFP8Linear(Base): pass  # not experts
'''


def test_export_named_experts_only_experts():
    named = cap.export_named_experts(EXPORT_SRC)
    assert named == {"QuantDbrxExperts", "QuantGptOssExperts", "QuantLlama4TextExperts"}
    assert "QuantFP8Linear" not in named  # filtered: not an *Experts check


def test_export_structural_fallbacks_detected():
    fb = cap.export_structural_fallbacks(EXPORT_SRC)
    assert any("fused" in f for f in fb) and any("iterable" in f for f in fb)


def test_quant_experts_classes():
    qc = cap.quant_experts_classes(QUANT_SRC)
    assert "_QuantDbrxExperts" in qc and "_QuantNonGatedFusedExperts" in qc
    assert "_QuantFP8Linear" not in qc  # not *Experts


def test_screen_flags_unnamed_quant_experts():
    named = {"QuantDbrxExperts", "QuantGptOssExperts", "QuantLlama4TextExperts"}
    qc = {"_QuantDbrxExperts", "_QuantNonGatedFusedExperts", "_QuantQwen3VLMoeTextExperts"}
    cands = cap.screen(named, qc)
    # explicitly-named one is covered; the other two are candidates to verify
    assert "_QuantDbrxExperts" not in cands
    assert "_QuantNonGatedFusedExperts" in cands and "_QuantQwen3VLMoeTextExperts" in cands


def test_screen_report_shape():
    rep = cap.screen_sources(EXPORT_SRC, QUANT_SRC)
    assert set(rep) >= {"export_named", "export_fallbacks", "quant_experts", "candidates"}
    assert "_QuantNonGatedFusedExperts" in rep["candidates"]
    # fused-named candidates are annotated as possibly covered by a structural fallback
    assert any(c["name"] == "_QuantNonGatedFusedExperts" and c["maybe_fallback"]
               for c in rep["candidates_detail"])
