# modelopt PTQ ↔ torch compatibility matrix

> Version columns show versions actually probed by the guarded validation scan. The **compatible** column is the authoritative set of tested OK ranges; untested versions must stay N/A in rendered artifacts.

> ⚠️ Some versions failed to build/probe and are unreliable: 2.1.0, 2.1.1, 2.1.2. Compatible ranges adjacent to these versions may be understated.

| symbol | affected models | role | compatible | 2.1.0 | 2.1.1 | 2.1.2 | 2.2.0 | 2.2.1 | 2.2.2 | 2.3.0 | 2.3.1 | 2.4.0 | 2.4.1 | 2.5.0 | 2.5.1 | 2.6.0 | 2.7.0 | 2.7.1 | 2.8.0 | 2.9.0 | 2.9.1 | 2.10.0 | 2.11.0 | 2.12.0 | 2.12.1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `torch.autograd:Function` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.compiler:is_compiling` | all torch-backed models | quant | 2.3.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.cuda:device` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.cuda:empty_cache` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.distributed.fsdp:FSDPModule` | all torch-backed models | export | 2.6.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.distributed.tensor:DTensor` 🛡 ⚇ | all torch-backed models | quant | 2.5.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.distributed.tensor:Shard` 🛡 ⚇ | all torch-backed models | quant | 2.5.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.nn.functional:linear` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.nn.functional:normalize` ⚇ | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.nn.functional:one_hot` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.nn:Linear` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.nn:Module` ⚇ | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.nn:Parameter` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.nn:Sequential` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.nn:functional` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.onnx._globals:GLOBALS` | all torch-backed models | quant | 2.2.0 – 2.8.0 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `torch.onnx._internal.torchscript_exporter._globals:GLOBALS` | all torch-backed models | quant | 2.9.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch.ops.aten.bmm:out` | all torch-backed models | quant | never | 🛠 | 🛠 | 🛠 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `torch.ops.aten:bmm` | all torch-backed models | quant | never | 🛠 | 🛠 | 🛠 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `torch.ops.aten:matmul` | all torch-backed models | quant | never | 🛠 | 🛠 | 🛠 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `torch:LongTensor` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:Size` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:Tensor` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:_matmul` | all torch-backed models | quant | never | 🛠 | 🛠 | 🛠 | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| `torch:abs` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:all` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:any` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:bincount` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:bmm` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:cat` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:chunk` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:concat` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:device` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:dtype` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:empty` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:equal` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:finfo` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:float` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:float32` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:float8_e4m3fn` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:get_default_dtype` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:greater` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:int32` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:is_floating_point` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:isinf` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:isnan` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:long` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:max` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:mean` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:nan_to_num` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:nn` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:no_grad` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:ones` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:onnx` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:stack` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:tensor` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:topk` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:uint8` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:where` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:zeros` | all torch-backed models | export | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `torch:zeros_like` | all torch-backed models | quant | 2.2.0 – 2.12.1 | 🛠 | 🛠 | 🛠 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

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
- `original_cls` — modelopt/torch/quantization/conversion.py:644

## Signature changes (within compatible ranges)

- `torch.distributed.tensor:DTensor`: 2.5.0 `(local_tensor: torch.Tensor, spec: torch.distributed.tensor._dtensor_spec.DTensorSpec, *, requires_grad: bool) -> 'DTensor'` → 2.10.0 `(*args, **kwargs)`
- `torch.distributed.tensor:Shard`: 2.5.0 `(dim: int) -> None` → 2.10.0 `<no-signature>`
- `torch.nn.functional:normalize`: 2.2.0 `(input: torch.Tensor, p: float = 2.0, dim: int = 1, eps: float = 1e-12, out: Optional[torch.Tensor] = None) -> torch.Tensor` → 2.12.0 `(input: torch.Tensor, p: float = 2.0, dim: int = 1, eps: float = 1e-12, out: torch.Tensor | None = None) -> torch.Tensor`
- `torch.nn:Module`: 2.2.0 `(*args, **kwargs) -> None` → 2.10.0 `(*args: Any, **kwargs: Any) -> None`

Legend: ✅ OK · ⚠️ symbol missing · ❌ module missing · 🛠 env error · 💥 probe error · 🛡 import is try/except-guarded · ⚇ signature changed within compatible ranges
