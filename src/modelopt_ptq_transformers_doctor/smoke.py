"""Runtime smoke probe: load → quantize → export, classifying the failing stage.

This is the *verdict* layer that static screening cannot provide. It runs the
real modelopt PTQ pipeline on a model and reports exactly which stage fails and
why — catching both:

- **load** failures (e.g. transformers-internal ``AttributeError`` such as
  ``'NemotronHConfig' object has no attribute 'moe_latent_size'``), and
- **export** failures (e.g. ``NotImplementedError`` for an unsupported MoE
  experts type like ``NemotronHExperts``).

``run_smoke`` is dependency-free orchestration (the stage callables are injected,
so it is unit-testable without torch/modelopt). The real stage callables live in
``smoke_prober.py``, which runs inside an environment that has modelopt +
transformers + torch installed.
"""
from __future__ import annotations

STAGES = ("load", "quantize", "export")
_MAX_ERR = 500


def run_smoke(stages: dict) -> dict:
    """Run the pipeline stages in order; stop at the first failure.

    ``stages`` maps each name in :data:`STAGES` to a callable. ``load()`` takes
    no model and returns one; ``quantize(model)`` returns the quantized model;
    ``export(model)`` writes the checkpoint. Returns a dict::

        {"reached": <stage|"done">, "status": "OK"|"<STAGE>_ERROR",
         "error_type": str|None, "error": str|None}
    """
    model = None
    for name in STAGES:
        try:
            result = stages[name]() if name == "load" else stages[name](model)
            if name != "export":
                model = result
        except Exception as exc:  # noqa: BLE001 — we classify every failure mode
            return {
                "reached": name,
                "status": f"{name.upper()}_ERROR",
                "error_type": type(exc).__name__,
                "error": str(exc)[:_MAX_ERR],
            }
    return {"reached": "done", "status": "OK", "error_type": None, "error": None}


def build_real_stages(model_id: str, recipe: str, device: str = "cuda",
                      trust_remote_code: bool = False) -> dict:
    """Real load→quantize→export stage callables (lazy-imports torch/transformers/
    modelopt, so importing this module needs none of them).

    ``recipe`` is a ``modelopt.torch.quantization`` config attribute name, e.g.
    ``FP8_DEFAULT_CFG`` or ``NVFP4_DEFAULT_CFG``.
    """
    def load():
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=trust_remote_code)
        dtype = torch.float16 if device.startswith("cuda") else torch.float32
        model = AutoModelForCausalLM.from_pretrained(
            model_id, trust_remote_code=trust_remote_code, torch_dtype=dtype)
        return (model.to(device).eval(), tok)

    def quantize(state):
        import torch
        import modelopt.torch.quantization as mtq

        model, tok = state
        cfg = getattr(mtq, recipe)

        def forward_loop(m):
            ids = tok("The quick brown fox jumps over the lazy dog.",
                      return_tensors="pt").to(device)
            with torch.no_grad():
                m(**ids)

        mtq.quantize(model, cfg, forward_loop=forward_loop)
        return (model, tok)

    def export(state):
        import tempfile
        from modelopt.torch.export import export_hf_checkpoint

        model, _ = state
        with tempfile.TemporaryDirectory() as out_dir:
            export_hf_checkpoint(model, export_dir=out_dir)

    return {"load": load, "quantize": quantize, "export": export}


def format_result(model: str, recipe: str, result: dict) -> str:
    """One-line human summary of a smoke result."""
    head = f"smoke: model={model} recipe={recipe} → {result['status']}"
    if result["status"] == "OK":
        return head + " (load + quantize + export all succeeded)"
    return f"{head} at '{result['reached']}': {result['error_type']}: {result['error']}"
