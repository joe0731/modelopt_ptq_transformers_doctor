# modelopt PTQ ↔ transformers compatibility matrix

> Version columns show only the versions the bisection actually probed (a sample, not every version in range). The **compatible** column is the authoritative result.

> ⚠️ Some versions failed to build/probe and are unreliable: 0.10.0, 0.10.1, 0.10.1.1, 0.10.2, 0.11.0, 0.7.0, 0.7.1, 0.7.2, 0.7.3, 0.8.0, 0.8.1, 0.8.2, 0.8.3, 0.8.4, 0.8.5, 0.8.5.post1, 0.9.0, 0.9.0.1, 0.9.1, 0.9.2. Compatible ranges adjacent to these versions may be understated.

| symbol | role | compatible | 0.6.0 | 0.6.1 | 0.6.1.post1 | 0.6.1.post2 | 0.6.2 | 0.6.3 | 0.6.3.post1 | 0.6.4 | 0.6.4.post1 | 0.6.5 | 0.6.6 | 0.6.6.post1 | 0.7.0 | 0.7.1 | 0.7.2 | 0.7.3 | 0.8.0 | 0.8.1 | 0.8.2 | 0.8.3 | 0.8.4 | 0.8.5 | 0.8.5.post1 | 0.9.0 | 0.9.0.1 | 0.9.1 | 0.9.2 | 0.10.0 | 0.10.1 | 0.10.1.1 | 0.10.2 | 0.11.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `vllm.attention.layers.cross_attention:CrossAttention` | quant | never | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 |
| `vllm.attention.layers.encoder_only_attention:EncoderOnlyAttention` | quant | never | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 |
| `vllm.distributed.parallel_state:get_dp_group` | quant | never | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 |
| `vllm.distributed.parallel_state:get_ep_group` | quant | never | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 |
| `vllm.distributed.parallel_state:get_tp_group` | quant | 0.6.0 – 0.6.6.post1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 |
| `vllm.model_executor.layers.attention.cross_attention:CrossAttention` 🛡 | quant | never | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 |
| `vllm.model_executor.layers.attention.encoder_only_attention:EncoderOnlyAttention` 🛡 | quant | never | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 | 💥 |

## Dynamic registrations (not statically checkable)

- `CrossAttention` — modelopt/torch/quantization/plugins/vllm.py:518
- `EncoderOnlyAttention` — modelopt/torch/quantization/plugins/vllm.py:525
- `VllmMLAAttention` — modelopt/torch/quantization/plugins/vllm.py:532

Legend: ✅ OK · ⚠️ symbol missing · ❌ module missing · 🛠 env error · 💥 probe error · 🛡 import is try/except-guarded · ⚇ signature changed within compatible window
