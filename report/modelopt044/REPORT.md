# modelopt PTQ ↔ transformers compatibility matrix

> Version columns show only the versions the bisection actually probed (a sample, not every version in range). The **compatible** column is the authoritative result.

| symbol | role | compatible | 4.46.0 | 4.46.1 | 4.46.2 | 4.46.3 | 4.47.0 | 4.47.1 | 4.48.0 | 4.48.1 | 4.48.2 | 4.48.3 | 4.49.0 | 4.50.0 | 4.50.1 | 4.50.2 | 4.50.3 | 4.51.0 | 4.51.1 | 4.51.2 | 4.51.3 | 4.52.0 | 4.52.1 | 4.52.2 | 4.52.3 | 4.52.4 | 4.53.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `transformers.activations:ACT2FN` | export | 4.46.0 – 4.53.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `transformers.integrations.finegrained_fp8:FP8Linear` 🛡 ⚇ | quant | 4.49.0 – 4.53.0 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `transformers.models.dbrx.modeling_dbrx:DbrxExpertGLU` 🛡 | quant | 4.46.0 – 4.53.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `transformers.models.dbrx.modeling_dbrx:DbrxExperts` 🛡 | quant | 4.46.0 – 4.53.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `transformers.models.dbrx.modeling_dbrx:DbrxFFN` 🛡 | quant | 4.46.0 – 4.53.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `transformers.models.falcon.modeling_falcon:FalconLinear` 🛡 | quant | 4.46.0 – 4.53.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `transformers.models.gpt_oss.modeling_gpt_oss:GptOssExperts` 🛡 | quant | never | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `transformers.models.llama4.modeling_llama4:Llama4TextExperts` 🛡 ⚇ | quant | 4.51.0 – 4.53.0 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `transformers.models.qwen3_vl_moe.modeling_qwen3_vl_moe:Qwen3VLMoeTextExperts` 🛡 | quant | never | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `transformers.models.t5.modeling_t5:T5Attention` | quant | 4.46.0 – 4.53.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `transformers.pytorch_utils:Conv1D` | quant | 4.46.0 – 4.53.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `transformers:AutoConfig` ⚇ | export | 4.46.0 – 4.53.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `transformers:AutoFeatureExtractor` | export | 4.46.0 – 4.53.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `transformers:PreTrainedModel` | quant | 4.46.0 – 4.53.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `transformers:T5Config` | export | 4.46.0 – 4.53.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

## Dynamic registrations (not statically checkable)

- `HFColumnParallelLinear` — modelopt/torch/quantization/plugins/huggingface.py:414
- `HFRowParallelLinear` — modelopt/torch/quantization/plugins/huggingface.py:419
- `Llama4TextExperts` — modelopt/torch/quantization/plugins/huggingface.py:1176
- `DbrxExperts` — modelopt/torch/quantization/plugins/huggingface.py:1186
- `DbrxExpertGLU` — modelopt/torch/quantization/plugins/huggingface.py:1189
- `DbrxFFN` — modelopt/torch/quantization/plugins/huggingface.py:1192
- `FalconLinear` — modelopt/torch/quantization/plugins/huggingface.py:1200
- `CompressedLinear` — modelopt/torch/quantization/plugins/huggingface.py:1208
- `Qwen3VLMoeTextExperts` — modelopt/torch/quantization/plugins/huggingface.py:1218
- `FP8Linear` — modelopt/torch/quantization/plugins/huggingface.py:1228
- `GptOssExperts` — modelopt/torch/quantization/plugins/huggingface.py:1323
- `moe_type` — modelopt/torch/quantization/plugins/huggingface.py:1337
- `linear_type` — modelopt/torch/quantization/plugins/huggingface.py:1350
- `mod_type` — modelopt/torch/quantization/plugins/huggingface.py:1413
- `mod_type` — modelopt/torch/quantization/plugins/huggingface.py:1465
- `moe_linear_type` — modelopt/torch/quantization/plugins/huggingface.py:1673

## Signature changes (within compatible window)

- `transformers.integrations.finegrained_fp8:FP8Linear`: 4.49.0 `(in_features: int, out_features: int, bias: bool = False, dtype=None, block_size: Optional[Tuple[int, int]] = None, device=None, activation_scheme='dynamic')` → 4.53.0 `(in_features: int, out_features: int, bias: bool = False, dtype=None, block_size: Optional[tuple[int, int]] = None, device=None, activation_scheme='dynamic')`
- `transformers.models.llama4.modeling_llama4:Llama4TextExperts`: 4.51.0 `(config: transformers.models.llama4.configuration_llama4.Llama4Config)` → 4.52.0 `(config: transformers.models.llama4.configuration_llama4.Llama4TextConfig)`
- `transformers:AutoConfig`: 4.46.0 `()` → 4.53.0 `() -> None`

Legend: ✅ OK · ⚠️ symbol missing · ❌ module missing · 🛠 env error · 💥 probe error · 🛡 import is try/except-guarded · ⚇ signature changed within compatible window
