---
name: cn_verify_testcase_runtime_reach
description: Use when 需要证明测试或工作负载是否真正执行到特定 C/C++ 代码路径，尤其是原生覆盖率不可用、不可信，或普通断言无法证明 native runtime reach 时。
---

# cn_verify_testcase_runtime_reach

## 概览

使用 `bpftrace` 的 uprobe 证明某个测试或工作负载是否执行到了指定的
C/C++ 符号或显式追踪锚点。一次命中只能证明执行流到达了该探测点；它不能证明行为
正确、分支覆盖完整、导出成功，也不能证明端到端语义成功。

<HARD-GATE>
在证据记录包含以下内容之前，不要声称代码“已覆盖”、“已到达”或“已执行”：

- 二进制路径和探测符号
- `nm -D --defined-only` 输出，证明符号存在
- 精确的 bpftrace 程序或生成的探针文件
- 运行目标 testcase 或 workload 后得到的原始 hit count
- 每个探针的状态：`hit`、`zero-hit`、`missing-symbol` 或 `untested`
</HARD-GATE>

如果当前机器不能运行 privileged `bpftrace`，就在符号存在性证据处 STOP。不要从
`nm`、测试通过/失败、日志或源码静态阅读推断 runtime reach。

## 红旗

出现这些想法时，说明你正准备过度声明：

- “测试通过了，所以肯定执行到了这里。”
- “符号存在，所以运行时覆盖已经证明了。”
- “只是快速检查，可以不保存原始 hit count。”
- “demangle 后的 C++ 名字也可以直接挂。”
- “没有输出大概就是零命中。”必须单独确认 attach 成功。
- “优化后的 C++ 内部符号足够稳定，可以放进 CI。”

## 流程

```dot
digraph runtime_reach {
  rankdir=LR;
  need [label="需要 runtime reach 证据", shape=box];
  durable [label="是否长期 / CI 使用?", shape=diamond];
  level1 [label="Level 1\\n挂已有符号", shape=box];
  level2 [label="Level 2\\n添加 extern C 锚点", shape=box];
  build [label="构建可探测二进制", shape=box];
  nm [label="用 nm -D 验证符号", shape=box];
  trace [label="运行 bpftrace + testcase", shape=box];
  classify [label="分类 hit / zero / missing / untested", shape=box];
  report [label="记录证据 + 矩阵", shape=box];

  need -> durable;
  durable -> level2 [label="是"];
  durable -> level1 [label="否"];
  level1 -> build;
  level2 -> build;
  build -> nm -> trace -> classify -> report;
}
```

## 检查清单

非平凡验证要维护可见 checklist：

- [ ] 定义必须证明的精确代码点。
- [ ] 一次性探索选择 Level 1；长期覆盖选择 Level 2。
- [ ] 使用 probeable flags 构建，或启用 anchor 构建开关。
- [ ] 用 `nm -D --defined-only` 验证每个探针符号。
- [ ] 运行 `bpftrace`，同时执行目标 testcase 或 workload。
- [ ] 保存原始 hit count，并分类每个探针状态。
- [ ] 报告边界：这是执行证据，不是语义正确性证明。

## 决策

| 需求 | 方法 | 适用场景 |
|---|---|---|
| 一次性探索 | Level 1：挂载已有导出符号 | 快速本地实验 |
| 长期可靠覆盖信号 | Level 2：添加显式 `extern "C"` 锚点 | CI、跨分支检查 |

原则：一次性探索挂已有符号；可靠覆盖要设计显式锚点，并像公共 API 一样测试它们。

## Level 1：已有符号

先构建一个适合探测的版本：

```bash
CXXFLAGS="-O0 -g3 -fno-inline -fno-omit-frame-pointer"
LDFLAGS="-Wl,--export-dynamic"  # 必要时让可执行文件导出符号
```

查找可挂载符号。可以用 demangle 后的名字阅读，但实际挂载时要使用二进制里的精确
符号名，除非该符号本身就是 `extern "C"`：

```bash
nm -D --defined-only /abs/path/libtarget.so | rg 'symbol_or_mangled_name'
nm -D --defined-only /abs/path/libtarget.so | c++filt | rg 'Class::method'
```

挂载 uprobe，在另一个 shell 里运行 testcase，然后停止 `bpftrace`：

```bash
sudo bpftrace -e 'uprobe:/abs/path/libtarget.so:target_symbol { @hits["target_symbol"] = count(); }'
```

Level 1 只适合快速探索。已有 C++ 符号可能因为内联、strip、隐藏可见性、重命名、
重载或构建参数变化而消失。

## Level 2：稳定锚点

在 native 源文件中定义锚点函数，并在需要证明的代码点调用它们。锚点命名要稳定且
可读。

```cpp
#ifdef __cplusplus
#define TRACE_ANCHOR_EXTERN extern "C"
#else
#define TRACE_ANCHOR_EXTERN
#endif

#if defined(__GNUC__) || defined(__clang__)
#define TRACE_ANCHOR_ATTR __attribute__((visibility("default"), noinline, used))
#else
#define TRACE_ANCHOR_ATTR
#endif

TRACE_ANCHOR_EXTERN TRACE_ANCHOR_ATTR
void trace_anchor_module_stage(void) {}
```

如果其他 translation unit 要调用锚点，就在头文件中声明它。如果 release 构建不能
暴露锚点，就用显式构建开关保护声明和调用，例如 `ENABLE_BPFTRACE_ANCHORS`，并在
覆盖检查任务中启用该开关。

使用前先验证锚点存在：

```bash
nm -D --defined-only /abs/path/libtarget.so | rg -F 'trace_anchor_module_stage'
```

和 Level 1 一样挂载：

```bash
sudo bpftrace -e 'uprobe:/abs/path/libtarget.so:trace_anchor_module_stage { @hits["module.stage"] = count(); }'
```

## 清单和证据

维护一份 manifest，让符号关系可审计：

```json
{
  "anchors": [
    {
      "id": "module.stage",
      "binary": "build/libtarget.so",
      "symbol": "trace_anchor_module_stage",
      "file": "src/module.cc",
      "module": "module",
      "stage": "stage"
    }
  ]
}
```

从 manifest 生成 bpftrace 程序，而不是手写每个探针：

```bpftrace
BEGIN { printf("tracking anchors\n"); }
uprobe:/abs/path/libtarget.so:trace_anchor_module_stage { @hits["module.stage"] = count(); }
END { print(@hits); }
```

输出覆盖矩阵时，用测试作为行、锚点 ID 作为列。只有观察到命中的探针才标记为覆盖。
缺失符号要和零命中探针分开标记。

最小证据记录应包含：

```json
{
  "testcase": "test_name_or_command",
  "anchor": "module.stage",
  "binary": "/abs/path/libtarget.so",
  "symbol": "trace_anchor_module_stage",
  "symbol_present": true,
  "hits": 3,
  "state": "hit"
}
```

## CI 检查

- 构建可探测的 debug 二进制，或启用锚点构建开关。
- 对 manifest 中的每个符号运行 `nm -D --defined-only`，缺失就失败。
- 只有在允许 privileged tracing 的主机上运行 `bpftrace`；否则 CI 只做符号存在性
  检查，把命中采集放到专用任务或专用机器上。
- 保存原始 hit count 和覆盖矩阵，让零命中回归可见。

## 常见错误

| 错误 | 修正 |
|---|---|
| 把 uprobe 命中当作语义正确的证明 | 只说“执行到了这个探测点” |
| 长期覆盖依赖优化后的 C++ 内部符号 | 添加 `extern "C"` 锚点 |
| 用 `nm -D -C` 看 demangle 名字，然后挂 demangle 名字 | 挂精确符号名，或使用锚点 |
| 锚点被构建开关隐藏，但 CI 没启用开关 | 检查构建选项和 `nm -D` 输出 |
| 把未运行或缺失探针涂成已覆盖 | 分开标记命中、零命中、缺失符号、未测试 |

## 压力场景

- Release 构建把目标函数内联：应改用 debug/probeable 构建，或添加稳定锚点。
- 分支重命名了 C++ 方法：长期检查应使用 manifest 记录的 `extern "C"` 锚点。
- 测试命中锚点但后续失败：结果只是执行证据，不是运行时 verdict。
- CI 不能运行 privileged tracing：符号存在性检查仍能捕捉锚点丢失，命中采集移到
  合适的主机上。
