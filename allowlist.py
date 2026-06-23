"""The fixed set of modelopt PTQ source files to scan (data, not logic)."""

QUANT_FILES = [
    "modelopt/torch/quantization/plugins/huggingface.py",
    "modelopt/torch/quantization/plugins/transformers.py",
    "modelopt/torch/quantization/plugins/attention.py",
]

EXPORT_FILES = [
    "modelopt/torch/export/unified_export_hf.py",
    "modelopt/torch/export/layer_utils.py",
    "modelopt/torch/export/tensorrt_llm_utils.py",
]

# Export plugins that may import transformers are matched by glob (relative to modelopt root).
EXPORT_PLUGIN_GLOB = "modelopt/torch/export/plugins/*.py"

ROLE_OF = {f: "quant" for f in QUANT_FILES}
ROLE_OF.update({f: "export" for f in EXPORT_FILES})
