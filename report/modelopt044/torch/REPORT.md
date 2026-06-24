# modelopt PTQ ↔ transformers compatibility matrix

> Version columns show only the versions the bisection actually probed (a sample, not every version in range). The **compatible** column is the authoritative result.

> ⚠️ Some versions failed to build/probe and are unreliable: 2.1.0, 2.1.1, 2.1.2. Compatible ranges adjacent to these versions may be understated.

| symbol | role | compatible | 2.1.0 | 2.1.1 | 2.1.2 | 2.2.0 | 2.2.1 | 2.2.2 | 2.3.0 | 2.3.1 | 2.4.0 | 2.4.1 | 2.5.0 | 2.5.1 | 2.6.0 | 2.7.0 | 2.7.1 | 2.8.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `torch.autograd:Function` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.compiler:is_compiling` | quant | 2.3.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.cuda:device` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.cuda:empty_cache` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.distributed.fsdp:FSDPModule` | export | 2.6.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ |
| `torch.distributed.tensor:DTensor` 🛡 | quant | 2.5.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.distributed.tensor:Shard` 🛡 | quant | 2.5.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.nn.functional:linear` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.nn.functional:normalize` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.nn.functional:one_hot` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.nn:Linear` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.nn:Module` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.nn:Parameter` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.nn:Sequential` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.nn:functional` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.onnx._globals:GLOBALS` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.onnx._internal.torchscript_exporter._globals:GLOBALS` | quant | never | 🛠 | 🛠 | 🛠 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `torch.ops.aten.bmm:out` | quant | never | 🛠 | 🛠 | 🛠 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `torch.ops.aten:bmm` | quant | never | 🛠 | 🛠 | 🛠 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `torch.ops.aten:matmul` | quant | never | 🛠 | 🛠 | 🛠 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `torch:LongTensor` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:Size` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:Tensor` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:_matmul` | quant | never | 🛠 | 🛠 | 🛠 | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| `torch:abs` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:all` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:any` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:bincount` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:bmm` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:cat` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:chunk` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:concat` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:device` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:dtype` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:empty` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:equal` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:finfo` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:float` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:float32` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:float8_e4m3fn` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:get_default_dtype` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:greater` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:int32` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:is_floating_point` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:isinf` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:isnan` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:long` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:max` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:mean` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:nan_to_num` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:nn` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:no_grad` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:ones` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:onnx` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:stack` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:tensor` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:topk` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:uint8` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:where` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:zeros` | export | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:zeros_like` | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

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
- `original_cls` — modelopt/torch/quantization/conversion.py:616

Legend: ✅ OK · ⚠️ symbol missing · ❌ module missing · 🛠 env error · 💥 probe error · 🛡 import is try/except-guarded · ⚇ signature changed within compatible window
