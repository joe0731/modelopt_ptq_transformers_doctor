# modelopt PTQ ↔ transformers compatibility matrix

> Version columns show versions actually probed by the guarded validation scan. The **compatible** column is the authoritative set of tested OK ranges; untested versions must stay N/A in rendered artifacts.

> ⚠️ Some versions failed to build/probe and are unreliable: 5.10.1, 5.10.2, 5.10.4. Compatible ranges adjacent to these versions may be understated.

| symbol | affected models | role | compatible | 4.46.0 | 4.46.1 | 4.46.2 | 4.46.3 | 4.47.0 | 4.47.1 | 4.48.0 | 4.48.1 | 4.48.2 | 4.48.3 | 4.49.0 | 4.50.0 | 4.50.1 | 4.50.2 | 4.50.3 | 4.51.0 | 4.51.1 | 4.51.2 | 4.51.3 | 4.52.0 | 4.52.1 | 4.52.2 | 4.52.3 | 4.52.4 | 4.53.0 | 4.53.1 | 4.53.2 | 4.53.3 | 4.54.0 | 4.54.1 | 4.55.0 | 4.55.1 | 4.55.2 | 4.55.3 | 4.55.4 | 4.56.0 | 4.56.1 | 4.56.2 | 4.57.0 | 4.57.1 | 4.57.2 | 4.57.3 | 4.57.4 | 4.57.5 | 4.57.6 | 5.0.0 | 5.1.0 | 5.2.0 | 5.3.0 | 5.4.0 | 5.5.0 | 5.5.1 | 5.5.2 | 5.5.3 | 5.5.4 | 5.6.0 | 5.6.1 | 5.6.2 | 5.7.0 | 5.8.0 | 5.8.1 | 5.9.0 | 5.10.0 | 5.10.1 | 5.10.2 | 5.10.4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `transformers.activations:ACT2FN` | shared / cross-family | export | 4.46.0 – 5.10.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 💥 | 💥 | 💥 |
| `transformers.integrations.finegrained_fp8:FP8Linear` 🛡 ⚇ | shared / cross-family | quant | 4.49.0 – 5.10.0 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 💥 | 💥 | 💥 |
| `transformers.models.dbrx.modeling_dbrx:DbrxExpertGLU` 🛡 ⚇ | DBRX | quant | 4.46.0 – 5.10.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 💥 | 💥 | 💥 |
| `transformers.models.dbrx.modeling_dbrx:DbrxExperts` 🛡 ⚇ | DBRX | quant | 4.46.0 – 5.10.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 💥 | 💥 | 💥 |
| `transformers.models.dbrx.modeling_dbrx:DbrxFFN` 🛡 ⚇ | DBRX | quant | 4.46.0 – 5.10.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 💥 | 💥 | 💥 |
| `transformers.models.falcon.modeling_falcon:FalconLinear` 🛡 | Falcon | quant | 4.46.0 – 5.10.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 💥 | 💥 | 💥 |
| `transformers.models.gpt_oss.modeling_gpt_oss:GptOssExperts` 🛡 | GPT-OSS | quant | 4.55.0 – 5.10.0 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 💥 | 💥 | 💥 |
| `transformers.models.llama4.modeling_llama4:Llama4TextExperts` 🛡 ⚇ | Llama 4 | quant | 4.51.0 – 5.10.0 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 💥 | 💥 | 💥 |
| `transformers.models.qwen3_vl_moe.modeling_qwen3_vl_moe:Qwen3VLMoeTextExperts` 🛡 | Qwen3 VL MoE | quant | 4.57.0 – 5.10.0 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 💥 | 💥 | 💥 |
| `transformers.models.t5.modeling_t5:T5Attention` ⚇ | T5 | quant | 4.46.0 – 5.10.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 💥 | 💥 | 💥 |
| `transformers.pytorch_utils:Conv1D` | shared / cross-family | quant | 4.46.0 – 5.10.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 💥 | 💥 | 💥 |
| `transformers:AutoConfig` ⚇ | shared / cross-family | export | 4.46.0 – 5.10.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 💥 | 💥 | 💥 |
| `transformers:AutoFeatureExtractor` | shared / cross-family | export | 4.46.0 – 5.10.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 💥 | 💥 | 💥 |
| `transformers:PreTrainedModel` ⚇ | shared / cross-family | quant | 4.46.0 – 5.10.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 💥 | 💥 | 💥 |
| `transformers:T5Config` ⚇ | shared / cross-family | export | 4.46.0 – 5.10.0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 💥 | 💥 | 💥 |

## Dynamic registrations (not statically checkable)

- `HFColumnParallelLinear` — modelopt/torch/quantization/plugins/huggingface.py:503
- `HFRowParallelLinear` — modelopt/torch/quantization/plugins/huggingface.py:508
- `Llama4TextExperts` — modelopt/torch/quantization/plugins/huggingface.py:1364
- `DbrxExperts` — modelopt/torch/quantization/plugins/huggingface.py:1374
- `DbrxExpertGLU` — modelopt/torch/quantization/plugins/huggingface.py:1377
- `DbrxFFN` — modelopt/torch/quantization/plugins/huggingface.py:1380
- `FalconLinear` — modelopt/torch/quantization/plugins/huggingface.py:1388
- `CompressedLinear` — modelopt/torch/quantization/plugins/huggingface.py:1396
- `Qwen3VLMoeTextExperts` — modelopt/torch/quantization/plugins/huggingface.py:1406
- `FP8Linear` — modelopt/torch/quantization/plugins/huggingface.py:1416
- `GptOssExperts` — modelopt/torch/quantization/plugins/huggingface.py:1511
- `moe_type` — modelopt/torch/quantization/plugins/huggingface.py:1525
- `linear_type` — modelopt/torch/quantization/plugins/huggingface.py:1538
- `mod_type` — modelopt/torch/quantization/plugins/huggingface.py:1601
- `mod_type` — modelopt/torch/quantization/plugins/huggingface.py:1672
- `moe_linear_type` — modelopt/torch/quantization/plugins/huggingface.py:1880

## Known upstream seam probes

> Static probes for historically brittle ModelOpt/transformers symbols. They may cover legacy or optional integrations and are not runtime verdicts.

| probe | symbol | note | 4.46.0 | 4.46.1 | 4.46.2 | 4.46.3 | 4.47.0 | 4.47.1 | 4.48.0 | 4.48.1 | 4.48.2 | 4.48.3 | 4.49.0 | 4.50.0 | 4.50.1 | 4.50.2 | 4.50.3 | 4.51.0 | 4.51.1 | 4.51.2 | 4.51.3 | 4.52.0 | 4.52.1 | 4.52.2 | 4.52.3 | 4.52.4 | 4.53.0 | 4.53.1 | 4.53.2 | 4.53.3 | 4.54.0 | 4.54.1 | 4.55.0 | 4.55.1 | 4.55.2 | 4.55.3 | 4.55.4 | 4.56.0 | 4.56.1 | 4.56.2 | 4.57.0 | 4.57.1 | 4.57.2 | 4.57.3 | 4.57.4 | 4.57.5 | 4.57.6 | 5.0.0 | 5.1.0 | 5.2.0 | 5.3.0 | 5.4.0 | 5.5.0 | 5.5.1 | 5.5.2 | 5.5.3 | 5.5.4 | 5.6.0 | 5.6.1 | 5.6.2 | 5.7.0 | 5.8.0 | 5.8.1 | 5.9.0 | 5.10.0 | 5.10.1 | 5.10.2 | 5.10.4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `legacy-modeling-utils-conv1d` | `transformers.modeling_utils.Conv1D` | legacy ModelOpt HF plugin path; newer transformers exposes Conv1D under pytorch_utils | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | · | · | · |
| `medusa-flash-attn-available` | `transformers.utils.is_flash_attn_available` | Medusa/speculative path import used by older ModelOpt examples | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | · | · | · |
| `pytorch-utils-conv1d` | `transformers.pytorch_utils.Conv1D` | current HF GPT-2 Conv1D location used by newer ModelOpt plugins | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | · | · | · |

## Transformers structural checks

> Static source-shape screening for known ModelOpt/transformers seams (attention dispatch, MoE expert containers, FP8 helpers). This is not a runtime verdict; verify failures with `doctor smoke`.

| check | source | 4.46.0 | 4.46.1 | 4.46.2 | 4.46.3 | 4.47.0 | 4.47.1 | 4.48.0 | 4.48.1 | 4.48.2 | 4.48.3 | 4.49.0 | 4.50.0 | 4.50.1 | 4.50.2 | 4.50.3 | 4.51.0 | 4.51.1 | 4.51.2 | 4.51.3 | 4.52.0 | 4.52.1 | 4.52.2 | 4.52.3 | 4.52.4 | 4.53.0 | 4.53.1 | 4.53.2 | 4.53.3 | 4.54.0 | 4.54.1 | 4.55.0 | 4.55.1 | 4.55.2 | 4.55.3 | 4.55.4 | 4.56.0 | 4.56.1 | 4.56.2 | 4.57.0 | 4.57.1 | 4.57.2 | 4.57.3 | 4.57.4 | 4.57.5 | 4.57.6 | 5.0.0 | 5.1.0 | 5.2.0 | 5.3.0 | 5.4.0 | 5.5.0 | 5.5.1 | 5.5.2 | 5.5.3 | 5.5.4 | 5.6.0 | 5.6.1 | 5.6.2 | 5.7.0 | 5.8.0 | 5.8.1 | 5.9.0 | 5.10.0 | 5.10.1 | 5.10.2 | 5.10.4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `attention-interface` | `modeling_utils.py` | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | · | · | · |
| `dbrx-experts` | `models/dbrx/modeling_dbrx.py` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | · | · | · |
| `experts-interface` | `integrations/moe.py` | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | · | · | · |
| `fp8-linear` | `integrations/finegrained_fp8.py` | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | · | · | · |
| `gpt-oss-experts` | `models/gpt_oss/modeling_gpt_oss.py` | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | · | · | · |
| `llama4-text-experts` | `models/llama4/modeling_llama4.py` | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | · | · | · |
| `mixtral-experts` | `models/mixtral/modeling_mixtral.py` | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | · | · | · |
| `nemotron-h-experts` | `models/nemotron_h/modeling_nemotron_h.py` | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | · | · | · |
| `qwen3-5-moe-experts` | `models/qwen3_5_moe/modeling_qwen3_5_moe.py` | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | · | · | · |
| `qwen3-moe-experts` | `models/qwen3_moe/modeling_qwen3_moe.py` | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | · | · | · |
| `qwen3-vl-moe-text-experts` | `models/qwen3_vl_moe/modeling_qwen3_vl_moe.py` | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | · | · | · |

Structural check details:

- `attention-interface` @ `4.46.0`: AttentionInterface, ALL_ATTENTION_FUNCTIONS, class AttentionInterface
- `attention-interface` @ `4.46.1`: AttentionInterface, ALL_ATTENTION_FUNCTIONS, class AttentionInterface
- `attention-interface` @ `4.46.2`: AttentionInterface, ALL_ATTENTION_FUNCTIONS, class AttentionInterface
- `attention-interface` @ `4.46.3`: AttentionInterface, ALL_ATTENTION_FUNCTIONS, class AttentionInterface
- `attention-interface` @ `4.47.0`: AttentionInterface, ALL_ATTENTION_FUNCTIONS, class AttentionInterface
- `attention-interface` @ `4.47.1`: AttentionInterface, ALL_ATTENTION_FUNCTIONS, class AttentionInterface
- `attention-interface` @ `4.48.0`: AttentionInterface, class AttentionInterface
- `attention-interface` @ `4.48.1`: AttentionInterface, class AttentionInterface
- `attention-interface` @ `4.48.2`: AttentionInterface, class AttentionInterface
- `attention-interface` @ `4.48.3`: AttentionInterface, class AttentionInterface
- `attention-interface` @ `4.49.0`: AttentionInterface, class AttentionInterface
- `attention-interface` @ `4.50.0`: AttentionInterface, class AttentionInterface
- `attention-interface` @ `4.50.1`: AttentionInterface, class AttentionInterface
- `attention-interface` @ `4.50.2`: AttentionInterface, class AttentionInterface
- `attention-interface` @ `4.50.3`: AttentionInterface, class AttentionInterface
- `attention-interface` @ `4.51.0`: AttentionInterface.get_interface
- `attention-interface` @ `4.51.1`: AttentionInterface.get_interface
- `attention-interface` @ `4.51.2`: AttentionInterface.get_interface
- `attention-interface` @ `4.51.3`: AttentionInterface.get_interface
- `attention-interface` @ `4.52.0`: AttentionInterface.get_interface
- `attention-interface` @ `4.52.1`: AttentionInterface.get_interface
- `attention-interface` @ `4.52.2`: AttentionInterface.get_interface
- `attention-interface` @ `4.52.3`: AttentionInterface.get_interface
- `attention-interface` @ `4.52.4`: AttentionInterface.get_interface
- `attention-interface` @ `4.53.0`: AttentionInterface.get_interface
- `attention-interface` @ `4.53.1`: AttentionInterface.get_interface
- `attention-interface` @ `4.53.2`: AttentionInterface.get_interface
- `attention-interface` @ `4.53.3`: AttentionInterface.get_interface
- `attention-interface` @ `4.54.0`: AttentionInterface.get_interface
- `attention-interface` @ `4.54.1`: AttentionInterface.get_interface
- `attention-interface` @ `4.55.0`: AttentionInterface.get_interface
- `attention-interface` @ `4.55.1`: AttentionInterface.get_interface
- `attention-interface` @ `4.55.2`: AttentionInterface.get_interface
- `attention-interface` @ `4.55.3`: AttentionInterface.get_interface
- `attention-interface` @ `4.55.4`: AttentionInterface.get_interface
- `attention-interface` @ `4.56.0`: AttentionInterface.get_interface
- `attention-interface` @ `4.56.1`: AttentionInterface.get_interface
- `attention-interface` @ `4.56.2`: AttentionInterface.get_interface
- `attention-interface` @ `4.57.0`: AttentionInterface.get_interface
- `attention-interface` @ `4.57.1`: AttentionInterface.get_interface
- `attention-interface` @ `4.57.2`: AttentionInterface.get_interface
- `attention-interface` @ `4.57.3`: AttentionInterface.get_interface
- `attention-interface` @ `4.57.4`: AttentionInterface.get_interface
- `attention-interface` @ `4.57.5`: AttentionInterface.get_interface
- `attention-interface` @ `4.57.6`: AttentionInterface.get_interface
- `attention-interface` @ `5.0.0`: AttentionInterface.get_interface
- `experts-interface` @ `4.46.0`: integrations/moe.py
- `experts-interface` @ `4.46.1`: integrations/moe.py
- `experts-interface` @ `4.46.2`: integrations/moe.py
- `experts-interface` @ `4.46.3`: integrations/moe.py
- `experts-interface` @ `4.47.0`: integrations/moe.py
- `experts-interface` @ `4.47.1`: integrations/moe.py
- `experts-interface` @ `4.48.0`: integrations/moe.py
- `experts-interface` @ `4.48.1`: integrations/moe.py
- `experts-interface` @ `4.48.2`: integrations/moe.py
- `experts-interface` @ `4.48.3`: integrations/moe.py
- `experts-interface` @ `4.49.0`: integrations/moe.py
- `experts-interface` @ `4.50.0`: integrations/moe.py
- `experts-interface` @ `4.50.1`: integrations/moe.py
- `experts-interface` @ `4.50.2`: integrations/moe.py
- `experts-interface` @ `4.50.3`: integrations/moe.py
- `experts-interface` @ `4.51.0`: integrations/moe.py
- `experts-interface` @ `4.51.1`: integrations/moe.py
- `experts-interface` @ `4.51.2`: integrations/moe.py
- `experts-interface` @ `4.51.3`: integrations/moe.py
- `experts-interface` @ `4.52.0`: integrations/moe.py
- `experts-interface` @ `4.52.1`: integrations/moe.py
- `experts-interface` @ `4.52.2`: integrations/moe.py
- `experts-interface` @ `4.52.3`: integrations/moe.py
- `experts-interface` @ `4.52.4`: integrations/moe.py
- `experts-interface` @ `4.53.0`: integrations/moe.py
- `experts-interface` @ `4.53.1`: integrations/moe.py
- `experts-interface` @ `4.53.2`: integrations/moe.py
- `experts-interface` @ `4.53.3`: integrations/moe.py
- `experts-interface` @ `4.54.0`: integrations/moe.py
- `experts-interface` @ `4.54.1`: integrations/moe.py
- `experts-interface` @ `4.55.0`: integrations/moe.py
- `experts-interface` @ `4.55.1`: integrations/moe.py
- `experts-interface` @ `4.55.2`: integrations/moe.py
- `experts-interface` @ `4.55.3`: integrations/moe.py
- `experts-interface` @ `4.55.4`: integrations/moe.py
- `experts-interface` @ `4.56.0`: integrations/moe.py
- `experts-interface` @ `4.56.1`: integrations/moe.py
- `experts-interface` @ `4.56.2`: integrations/moe.py
- `experts-interface` @ `4.57.0`: integrations/moe.py
- `experts-interface` @ `4.57.1`: integrations/moe.py
- `experts-interface` @ `4.57.2`: integrations/moe.py
- `experts-interface` @ `4.57.3`: integrations/moe.py
- `experts-interface` @ `4.57.4`: integrations/moe.py
- `experts-interface` @ `4.57.5`: integrations/moe.py
- `experts-interface` @ `4.57.6`: integrations/moe.py
- `experts-interface` @ `5.0.0`: ExpertsInterface.get_interface
- `fp8-linear` @ `4.46.0`: integrations/finegrained_fp8.py
- `fp8-linear` @ `4.46.1`: integrations/finegrained_fp8.py
- `fp8-linear` @ `4.46.2`: integrations/finegrained_fp8.py
- `fp8-linear` @ `4.46.3`: integrations/finegrained_fp8.py
- `fp8-linear` @ `4.47.0`: integrations/finegrained_fp8.py
- `fp8-linear` @ `4.47.1`: integrations/finegrained_fp8.py
- `fp8-linear` @ `4.48.0`: integrations/finegrained_fp8.py
- `fp8-linear` @ `4.48.1`: integrations/finegrained_fp8.py
- `fp8-linear` @ `4.48.2`: integrations/finegrained_fp8.py
- `fp8-linear` @ `4.48.3`: integrations/finegrained_fp8.py
- `fp8-linear` @ `4.49.0`: self.weight, self.weight_scale_inv, self.activation_scale
- `fp8-linear` @ `4.50.0`: self.weight, self.weight_scale_inv, self.activation_scale
- `fp8-linear` @ `4.50.1`: self.weight, self.weight_scale_inv, self.activation_scale
- `fp8-linear` @ `4.50.2`: self.weight, self.weight_scale_inv, self.activation_scale
- `fp8-linear` @ `4.50.3`: self.weight, self.weight_scale_inv, self.activation_scale
- `fp8-linear` @ `4.51.0`: self.activation_scale
- `fp8-linear` @ `4.51.1`: self.activation_scale
- `fp8-linear` @ `4.51.2`: self.activation_scale
- `fp8-linear` @ `4.51.3`: self.activation_scale
- `fp8-linear` @ `4.52.0`: self.activation_scale
- `fp8-linear` @ `4.52.1`: self.activation_scale
- `fp8-linear` @ `4.52.2`: self.activation_scale
- `fp8-linear` @ `4.52.3`: self.activation_scale
- `fp8-linear` @ `4.52.4`: self.activation_scale
- `fp8-linear` @ `4.53.0`: self.activation_scale
- `fp8-linear` @ `4.53.1`: self.activation_scale
- `fp8-linear` @ `4.53.2`: self.activation_scale
- `fp8-linear` @ `4.53.3`: self.activation_scale
- `fp8-linear` @ `4.54.0`: self.activation_scale
- `fp8-linear` @ `4.54.1`: self.activation_scale
- `fp8-linear` @ `4.55.0`: self.activation_scale
- `fp8-linear` @ `4.55.1`: self.activation_scale
- `fp8-linear` @ `4.55.2`: self.activation_scale
- `fp8-linear` @ `4.55.3`: self.activation_scale
- `fp8-linear` @ `4.55.4`: self.activation_scale
- `fp8-linear` @ `4.56.0`: self.activation_scale
- `fp8-linear` @ `4.56.1`: self.activation_scale
- `fp8-linear` @ `4.56.2`: self.activation_scale
- `fp8-linear` @ `4.57.0`: self.activation_scale
- `fp8-linear` @ `4.57.1`: self.activation_scale
- `fp8-linear` @ `4.57.2`: self.activation_scale
- `fp8-linear` @ `4.57.3`: self.activation_scale
- `fp8-linear` @ `4.57.4`: self.activation_scale
- `fp8-linear` @ `4.57.5`: self.activation_scale
- `fp8-linear` @ `4.57.6`: self.activation_scale
- `gpt-oss-experts` @ `4.46.0`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.46.1`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.46.2`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.46.3`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.47.0`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.47.1`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.48.0`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.48.1`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.48.2`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.48.3`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.49.0`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.50.0`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.50.1`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.50.2`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.50.3`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.51.0`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.51.1`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.51.2`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.51.3`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.52.0`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.52.1`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.52.2`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.52.3`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.52.4`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.53.0`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.53.1`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.53.2`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.53.3`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.54.0`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.54.1`: models/gpt_oss/modeling_gpt_oss.py
- `gpt-oss-experts` @ `4.55.0`: method _apply_gate
- `gpt-oss-experts` @ `4.55.1`: method _apply_gate
- `gpt-oss-experts` @ `4.55.2`: method _apply_gate
- `gpt-oss-experts` @ `4.55.3`: method _apply_gate
- `gpt-oss-experts` @ `4.55.4`: method _apply_gate
- `gpt-oss-experts` @ `4.56.0`: method _apply_gate
- `gpt-oss-experts` @ `4.56.1`: method _apply_gate
- `gpt-oss-experts` @ `4.56.2`: method _apply_gate
- `gpt-oss-experts` @ `4.57.0`: method _apply_gate
- `gpt-oss-experts` @ `4.57.1`: method _apply_gate
- `gpt-oss-experts` @ `4.57.2`: method _apply_gate
- `gpt-oss-experts` @ `4.57.3`: method _apply_gate
- `gpt-oss-experts` @ `4.57.4`: method _apply_gate
- `gpt-oss-experts` @ `4.57.5`: method _apply_gate
- `gpt-oss-experts` @ `4.57.6`: method _apply_gate
- `llama4-text-experts` @ `4.46.0`: models/llama4/modeling_llama4.py
- `llama4-text-experts` @ `4.46.1`: models/llama4/modeling_llama4.py
- `llama4-text-experts` @ `4.46.2`: models/llama4/modeling_llama4.py
- `llama4-text-experts` @ `4.46.3`: models/llama4/modeling_llama4.py
- `llama4-text-experts` @ `4.47.0`: models/llama4/modeling_llama4.py
- `llama4-text-experts` @ `4.47.1`: models/llama4/modeling_llama4.py
- `llama4-text-experts` @ `4.48.0`: models/llama4/modeling_llama4.py
- `llama4-text-experts` @ `4.48.1`: models/llama4/modeling_llama4.py
- `llama4-text-experts` @ `4.48.2`: models/llama4/modeling_llama4.py
- `llama4-text-experts` @ `4.48.3`: models/llama4/modeling_llama4.py
- `llama4-text-experts` @ `4.49.0`: models/llama4/modeling_llama4.py
- `llama4-text-experts` @ `4.50.0`: models/llama4/modeling_llama4.py
- `llama4-text-experts` @ `4.50.1`: models/llama4/modeling_llama4.py
- `llama4-text-experts` @ `4.50.2`: models/llama4/modeling_llama4.py
- `llama4-text-experts` @ `4.50.3`: models/llama4/modeling_llama4.py
- `mixtral-experts` @ `4.46.0`: class MixtralExperts
- `mixtral-experts` @ `4.46.1`: class MixtralExperts
- `mixtral-experts` @ `4.46.2`: class MixtralExperts
- `mixtral-experts` @ `4.46.3`: class MixtralExperts
- `mixtral-experts` @ `4.47.0`: class MixtralExperts
- `mixtral-experts` @ `4.47.1`: class MixtralExperts
- `mixtral-experts` @ `4.48.0`: class MixtralExperts
- `mixtral-experts` @ `4.48.1`: class MixtralExperts
- `mixtral-experts` @ `4.48.2`: class MixtralExperts
- `mixtral-experts` @ `4.48.3`: class MixtralExperts
- `mixtral-experts` @ `4.49.0`: class MixtralExperts
- `mixtral-experts` @ `4.50.0`: class MixtralExperts
- `mixtral-experts` @ `4.50.1`: class MixtralExperts
- `mixtral-experts` @ `4.50.2`: class MixtralExperts
- `mixtral-experts` @ `4.50.3`: class MixtralExperts
- `mixtral-experts` @ `4.51.0`: class MixtralExperts
- `mixtral-experts` @ `4.51.1`: class MixtralExperts
- `mixtral-experts` @ `4.51.2`: class MixtralExperts
- `mixtral-experts` @ `4.51.3`: class MixtralExperts
- `mixtral-experts` @ `4.52.0`: class MixtralExperts
- `mixtral-experts` @ `4.52.1`: class MixtralExperts
- `mixtral-experts` @ `4.52.2`: class MixtralExperts
- `mixtral-experts` @ `4.52.3`: class MixtralExperts
- `mixtral-experts` @ `4.52.4`: class MixtralExperts
- `mixtral-experts` @ `4.53.0`: class MixtralExperts
- `mixtral-experts` @ `4.53.1`: class MixtralExperts
- `mixtral-experts` @ `4.53.2`: class MixtralExperts
- `mixtral-experts` @ `4.53.3`: class MixtralExperts
- `mixtral-experts` @ `4.54.0`: class MixtralExperts
- `mixtral-experts` @ `4.54.1`: class MixtralExperts
- `mixtral-experts` @ `4.55.0`: class MixtralExperts
- `mixtral-experts` @ `4.55.1`: class MixtralExperts
- `mixtral-experts` @ `4.55.2`: class MixtralExperts
- `mixtral-experts` @ `4.55.3`: class MixtralExperts
- `mixtral-experts` @ `4.55.4`: class MixtralExperts
- `mixtral-experts` @ `4.56.0`: class MixtralExperts
- `mixtral-experts` @ `4.56.1`: class MixtralExperts
- `mixtral-experts` @ `4.56.2`: class MixtralExperts
- `mixtral-experts` @ `4.57.0`: class MixtralExperts
- `mixtral-experts` @ `4.57.1`: class MixtralExperts
- `mixtral-experts` @ `4.57.2`: class MixtralExperts
- `mixtral-experts` @ `4.57.3`: class MixtralExperts
- `mixtral-experts` @ `4.57.4`: class MixtralExperts
- `mixtral-experts` @ `4.57.5`: class MixtralExperts
- `mixtral-experts` @ `4.57.6`: class MixtralExperts
- `nemotron-h-experts` @ `4.46.0`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.46.1`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.46.2`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.46.3`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.47.0`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.47.1`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.48.0`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.48.1`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.48.2`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.48.3`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.49.0`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.50.0`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.50.1`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.50.2`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.50.3`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.51.0`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.51.1`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.51.2`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.51.3`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.52.0`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.52.1`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.52.2`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.52.3`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.52.4`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.53.0`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.53.1`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.53.2`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.53.3`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.54.0`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.54.1`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.55.0`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.55.1`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.55.2`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.55.3`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.55.4`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.56.0`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.56.1`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.56.2`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.57.0`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.57.1`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.57.2`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.57.3`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.57.4`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.57.5`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `4.57.6`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `5.0.0`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `5.1.0`: models/nemotron_h/modeling_nemotron_h.py
- `nemotron-h-experts` @ `5.2.0`: models/nemotron_h/modeling_nemotron_h.py
- `qwen3-5-moe-experts` @ `4.46.0`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.46.1`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.46.2`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.46.3`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.47.0`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.47.1`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.48.0`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.48.1`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.48.2`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.48.3`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.49.0`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.50.0`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.50.1`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.50.2`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.50.3`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.51.0`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.51.1`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.51.2`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.51.3`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.52.0`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.52.1`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.52.2`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.52.3`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.52.4`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.53.0`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.53.1`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.53.2`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.53.3`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.54.0`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.54.1`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.55.0`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.55.1`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.55.2`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.55.3`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.55.4`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.56.0`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.56.1`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.56.2`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.57.0`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.57.1`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.57.2`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.57.3`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.57.4`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.57.5`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `4.57.6`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `5.0.0`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-5-moe-experts` @ `5.1.0`: models/qwen3_5_moe/modeling_qwen3_5_moe.py
- `qwen3-moe-experts` @ `4.46.0`: models/qwen3_moe/modeling_qwen3_moe.py
- `qwen3-moe-experts` @ `4.46.1`: models/qwen3_moe/modeling_qwen3_moe.py
- `qwen3-moe-experts` @ `4.46.2`: models/qwen3_moe/modeling_qwen3_moe.py
- `qwen3-moe-experts` @ `4.46.3`: models/qwen3_moe/modeling_qwen3_moe.py
- `qwen3-moe-experts` @ `4.47.0`: models/qwen3_moe/modeling_qwen3_moe.py
- `qwen3-moe-experts` @ `4.47.1`: models/qwen3_moe/modeling_qwen3_moe.py
- `qwen3-moe-experts` @ `4.48.0`: models/qwen3_moe/modeling_qwen3_moe.py
- `qwen3-moe-experts` @ `4.48.1`: models/qwen3_moe/modeling_qwen3_moe.py
- `qwen3-moe-experts` @ `4.48.2`: models/qwen3_moe/modeling_qwen3_moe.py
- `qwen3-moe-experts` @ `4.48.3`: models/qwen3_moe/modeling_qwen3_moe.py
- `qwen3-moe-experts` @ `4.49.0`: models/qwen3_moe/modeling_qwen3_moe.py
- `qwen3-moe-experts` @ `4.50.0`: models/qwen3_moe/modeling_qwen3_moe.py
- `qwen3-moe-experts` @ `4.50.1`: models/qwen3_moe/modeling_qwen3_moe.py
- `qwen3-moe-experts` @ `4.50.2`: models/qwen3_moe/modeling_qwen3_moe.py
- `qwen3-moe-experts` @ `4.50.3`: models/qwen3_moe/modeling_qwen3_moe.py
- `qwen3-moe-experts` @ `4.51.0`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.51.1`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.51.2`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.51.3`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.52.0`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.52.1`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.52.2`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.52.3`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.52.4`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.53.0`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.53.1`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.53.2`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.53.3`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.54.0`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.54.1`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.55.0`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.55.1`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.55.2`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.55.3`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.55.4`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.56.0`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.56.1`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.56.2`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.57.0`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.57.1`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.57.2`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.57.3`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.57.4`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.57.5`: class Qwen3MoeExperts
- `qwen3-moe-experts` @ `4.57.6`: class Qwen3MoeExperts
- `qwen3-vl-moe-text-experts` @ `4.46.0`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.46.1`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.46.2`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.46.3`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.47.0`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.47.1`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.48.0`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.48.1`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.48.2`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.48.3`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.49.0`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.50.0`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.50.1`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.50.2`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.50.3`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.51.0`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.51.1`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.51.2`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.51.3`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.52.0`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.52.1`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.52.2`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.52.3`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.52.4`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.53.0`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.53.1`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.53.2`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.53.3`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.54.0`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.54.1`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.55.0`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.55.1`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.55.2`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.55.3`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.55.4`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.56.0`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.56.1`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py
- `qwen3-vl-moe-text-experts` @ `4.56.2`: models/qwen3_vl_moe/modeling_qwen3_vl_moe.py

## Signature changes (within compatible ranges)

- `transformers.integrations.finegrained_fp8:FP8Linear`: 4.49.0 `(in_features: int, out_features: int, bias: bool = False, dtype=None, block_size: Optional[Tuple[int, int]] = None, device=None, activation_scheme='dynamic')` → 4.53.0 `(in_features: int, out_features: int, bias: bool = False, dtype=None, block_size: Optional[tuple[int, int]] = None, device=None, activation_scheme='dynamic')` → 5.0.0 `(in_features: int, out_features: int, bias: bool = False, dtype=torch.float8_e4m3fn, block_size: tuple[int, int] | None = None, activation_scheme='dynamic')` → 5.4.0 `(in_features: int, out_features: int, block_size: tuple[int, int] | None = None, activation_scheme: str = 'dynamic', has_bias: bool = False, dtype=torch.float8_e4m3fn)` → 5.8.0 `(in_features: 'int', out_features: 'int', block_size: 'tuple[int, int] | None' = None, activation_scheme: 'str' = 'dynamic', has_bias: 'bool' = False, dtype=torch.float8_e4m3fn)`
- `transformers.models.dbrx.modeling_dbrx:DbrxExpertGLU`: 4.46.0 `(hidden_size: int, ffn_hidden_size: int, moe_num_experts: int, ffn_act_fn: dict)` → 5.0.0 `(config)`
- `transformers.models.dbrx.modeling_dbrx:DbrxExperts`: 4.46.0 `(hidden_size: int, ffn_hidden_size: int, moe_num_experts: int, ffn_act_fn: dict)` → 5.0.0 `(config)`
- `transformers.models.dbrx.modeling_dbrx:DbrxFFN`: 4.46.0 `(config: transformers.models.dbrx.configuration_dbrx.DbrxConfig)` → 5.0.0 `(config, **kwargs)`
- `transformers.models.llama4.modeling_llama4:Llama4TextExperts`: 4.51.0 `(config: transformers.models.llama4.configuration_llama4.Llama4Config)` → 4.52.0 `(config: transformers.models.llama4.configuration_llama4.Llama4TextConfig)`
- `transformers.models.t5.modeling_t5:T5Attention`: 4.46.0 `(config: transformers.models.t5.configuration_t5.T5Config, has_relative_attention_bias=False, layer_idx: Optional[int] = None)` → 5.0.0 `(config: transformers.models.t5.configuration_t5.T5Config, has_relative_attention_bias=False, layer_idx: int | None = None)`
- `transformers:AutoConfig`: 4.46.0 `()` → 4.53.0 `() -> None`
- `transformers:PreTrainedModel`: 4.46.0 `(config: transformers.configuration_utils.PretrainedConfig, *inputs, **kwargs)` → 5.0.0 `(config: transformers.configuration_utils.PreTrainedConfig, *inputs, **kwargs)`
- `transformers:T5Config`: 4.46.0 `(vocab_size=32128, d_model=512, d_kv=64, d_ff=2048, num_layers=6, num_decoder_layers=None, num_heads=8, relative_attention_num_buckets=32, relative_attention_max_distance=128, dropout_rate=0.1, layer_norm_epsilon=1e-06, initializer_factor=1.0, feed_forward_proj='relu', is_encoder_decoder=True, use_cache=True, pad_token_id=0, eos_token_id=1, classifier_dropout=0.0, **kwargs)` → 5.0.0 `(vocab_size=32128, d_model=512, d_kv=64, d_ff=2048, num_layers=6, num_decoder_layers=None, num_heads=8, relative_attention_num_buckets=32, relative_attention_max_distance=128, dropout_rate=0.1, layer_norm_epsilon=1e-06, initializer_factor=1.0, feed_forward_proj='relu', is_encoder_decoder=True, use_cache=True, pad_token_id=0, eos_token_id=1, classifier_dropout=0.0, tie_word_embeddings=True, is_decoder=False, **kwargs)` → 5.4.0 `(transformers_version: str | None = None, architectures: list[str] | None = None, output_hidden_states: bool | None = False, return_dict: bool | None = True, dtype: Union[str, ForwardRef('torch.dtype'), NoneType] = None, chunk_size_feed_forward: int = 0, is_encoder_decoder: bool = True, id2label: dict[int, str] | dict[str, str] | None = None, label2id: dict[str, int] | dict[str, str] | None = None, problem_type: Optional[Literal['regression', 'single_label_classification', 'multi_label_classification']] = None, vocab_size: int = 32128, d_model: int = 512, d_kv: int = 64, d_ff: int = 2048, num_layers: int = 6, num_decoder_layers: int | None = None, num_heads: int = 8, relative_attention_num_buckets: int = 32, relative_attention_max_distance: int = 128, dropout_rate: float = 0.1, layer_norm_epsilon: float = 1e-06, initializer_factor: float = 1.0, feed_forward_proj: str = 'relu', use_cache: bool = True, pad_token_id: int | None = 0, eos_token_id: int | list[int] | None = 1, classifier_dropout: float | int = 0.0, is_decoder: bool = False) -> None` → 5.5.0 `(transformers_version: str | None = None, architectures: list[str] | None = None, output_hidden_states: bool | None = False, return_dict: bool | None = True, dtype: Union[str, ForwardRef('torch.dtype'), NoneType] = None, chunk_size_feed_forward: int = 0, is_encoder_decoder: bool = True, id2label: dict[int, str] | dict[str, str] | None = None, label2id: dict[str, int] | dict[str, str] | None = None, problem_type: Optional[Literal['regression', 'single_label_classification', 'multi_label_classification']] = None, vocab_size: int = 32128, d_model: int = 512, d_kv: int = 64, d_ff: int = 2048, num_layers: int = 6, num_decoder_layers: int | None = None, num_heads: int = 8, relative_attention_num_buckets: int = 32, relative_attention_max_distance: int = 128, dropout_rate: float | int = 0.1, layer_norm_epsilon: float = 1e-06, initializer_factor: float = 1.0, feed_forward_proj: str = 'relu', use_cache: bool = True, pad_token_id: int | None = 0, eos_token_id: int | list[int] | None = 1, classifier_dropout: float | int = 0.0, is_decoder: bool = False) -> None` → 5.5.1 `(transformers_version: str | None = None, architectures: list[str] | None = None, output_hidden_states: bool | None = False, return_dict: bool | None = True, dtype: Union[str, ForwardRef('torch.dtype'), NoneType] = None, chunk_size_feed_forward: int = 0, id2label: dict[int, str] | dict[str, str] | None = None, label2id: dict[str, int] | dict[str, str] | None = None, problem_type: Optional[Literal['regression', 'single_label_classification', 'multi_label_classification']] = None, *, is_encoder_decoder: bool = True, vocab_size: int = 32128, d_model: int = 512, d_kv: int = 64, d_ff: int = 2048, num_layers: int = 6, num_decoder_layers: int | None = None, num_heads: int = 8, relative_attention_num_buckets: int = 32, relative_attention_max_distance: int = 128, dropout_rate: float | int = 0.1, layer_norm_epsilon: float = 1e-06, initializer_factor: float = 1.0, feed_forward_proj: str = 'relu', use_cache: bool = True, pad_token_id: int | None = 0, eos_token_id: int | list[int] | None = 1, classifier_dropout: float | int = 0.0, is_decoder: bool = False) -> None`

Legend: ✅ OK · ⚠️ symbol missing · ❌ module missing · 🛠 env error · 💥 probe error · 🛡 import is try/except-guarded · ⚇ signature changed within compatible ranges
