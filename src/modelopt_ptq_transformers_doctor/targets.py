"""Registry of libraries the doctor can probe modelopt PTQ against."""
from __future__ import annotations

from dataclasses import dataclass

from . import allowlist

# Fixed co-dependency pins for isolation (edit here to retune the known-good set).
PIN_TORCH = "torch==2.6.0"
PIN_TRANSFORMERS = "transformers==4.56.0"
PIN_ACCELERATE = "accelerate==1.10.0"


@dataclass(frozen=True)
class Target:
    name: str
    pypi: str
    import_roots: tuple[str, ...]
    quant_files: tuple[str, ...]
    export_files: tuple[str, ...]
    export_plugin_glob: str | None
    pinned_deps: tuple[str, ...]

    @property
    def files(self) -> tuple[str, ...]:
        return self.quant_files + self.export_files

    def role_of(self, rel: str) -> str:
        return "quant" if rel in self.quant_files else "export"


TARGETS: dict[str, Target] = {
    "transformers": Target(
        name="transformers", pypi="transformers", import_roots=("transformers",),
        quant_files=tuple(allowlist.QUANT_FILES), export_files=tuple(allowlist.EXPORT_FILES),
        export_plugin_glob=allowlist.EXPORT_PLUGIN_GLOB, pinned_deps=(PIN_TORCH,),
    ),
    "torch": Target(
        name="torch", pypi="torch", import_roots=("torch",),
        quant_files=(
            "modelopt/torch/quantization/plugins/huggingface.py",
            "modelopt/torch/quantization/plugins/transformers.py",
            "modelopt/torch/quantization/plugins/attention.py",
            "modelopt/torch/quantization/nn/modules/tensor_quantizer.py",
            "modelopt/torch/quantization/conversion.py",
        ),
        export_files=(
            "modelopt/torch/export/unified_export_hf.py",
            "modelopt/torch/export/layer_utils.py",
        ),
        export_plugin_glob=None, pinned_deps=(PIN_TRANSFORMERS, PIN_ACCELERATE),
    ),
    "vllm": Target(
        name="vllm", pypi="vllm", import_roots=("vllm",),
        quant_files=(
            "modelopt/torch/quantization/plugins/vllm.py",
            "modelopt/torch/sparsity/attention_sparsity/plugins/vllm.py",
        ),
        export_files=("modelopt/torch/export/plugins/vllm_fakequant_megatron.py",),
        export_plugin_glob=None, pinned_deps=(),
    ),
    "accelerate": Target(
        name="accelerate", pypi="accelerate", import_roots=("accelerate",),
        quant_files=(
            "modelopt/torch/quantization/plugins/accelerate.py",
            "modelopt/torch/quantization/plugins/transformers_trainer.py",
            "modelopt/torch/quantization/utils/core_utils.py",
        ),
        export_files=(),
        export_plugin_glob=None, pinned_deps=(PIN_TORCH, PIN_TRANSFORMERS),
    ),
}
