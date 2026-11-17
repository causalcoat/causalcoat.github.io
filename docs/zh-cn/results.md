<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# 结果参考

先区分本次得到的是变量集合、图，还是某项效应的估计。MB 主要报告所选因子，PAG 报告图，ADJ 还报告调整集与逐集估计。

## 顶层字段

三个发现函数返回具有相同八个字段的 JSON 可序列化字典。无适用内容的字段可以为 `None`；图是否可用还需查看 `graph.available`。

| 字段 | 内容 | 首先看什么 |
| --- | --- | --- |
| `method` | `mb`、`pag` 或 `adj` | 确认实际执行的方法。 |
| `status` | 执行状态 | 是否有记录的调用或处理错误。 |
| `factors` | 名称到可用定义的映射 | 因子含义与赋值规则。 |
| `graph` | 可用性、节点顺序和端点矩阵 | PAG/ADJ 的结构信息。 |
| `adjustment_sets` | ADJ 找到的变量集合 | 哪些集合作为调整候选。 |
| `estimates` | ADJ 的估计、逐集记录和准则说明 | 实际用了哪个集合及其假设。 |
| `diagnostics` | 筛选历史与过程记录 | 集合如何更新。 |
| `provenance` | 数据列、模型、参数和提供的假设 | 本次分析依据什么。 |

## 选中因子

MB 的集合保存在 `diagnostics.final_blanket`，其中也包含目标名称。`factors` 将这些名称映射到可用文字定义；已有数值目标可能没有文字定义。这里的变量集合用于概括目标信息，不是一份已经确认的直接原因清单。

PAG 和 ADJ 的 `graph.node_order` 列出图中的变量。ADJ 的 `factors` 主要保存新发现因子，不必与含处理、结果的完整节点列表相同。

## 图的端点标记

`graph.node_order` 决定 `graph.endpoint_matrix` 的行列顺序。元素 `[i, j]` 记录边在节点 `i` 一侧的标记，而不是通常的“从 i 指向 j”的邻接矩阵编码。

| 编码 | 端点 | 含义 |
| --- | --- | --- |
| `-1` | 尾线 | 在所表达的结构中保留尾端信息。 |
| `1` | 箭头 | 在相应图假设下，该端节点不是另一端节点的祖先。 |
| `2` | 圆圈 | 该端尚未确定为尾线还是箭头。 |
| `0` | 无 | 两节点间没有边。 |

例如 `i -> j` 对应 `matrix[i][j] == -1`、`matrix[j][i] == 1`。PAG 中这一形式表达 `i` 是 `j` 的祖先，不应一律解释为不存在隐藏中间节点的直接作用。`i <-> j` 的两个箭头表示二者都不是另一方的祖先，与潜在共同原因相容。

`i o-> j` 保留 `i` 端不确定性；`i o-o j` 的两端都未定。圆圈表达结构未定，不是效应较小或模型置信度较低的数值标记。PAG 表达一组候选结构，不是一张已经完全定向的图。

MB 返回变量集合而非图，其 `graph` 通常包含 `available=false` 和说明。先检查可用性，再读取矩阵。

## 调整集与效应估计

`adjustment_sets` 需要与 `estimates.adjustment_criterion` 一起解释。集合有效性相对于输入图和应用的准则成立；图本身的正确性及额外研究假设仍需审视。

| `adjustment_sets` | 读法 |
| --- | --- |
| `[["V"]]` | 找到包含 `V` 的调整集。 |
| `[[]]` | 找到一个空调整集，在相应图条件下无需协变量调整。 |
| `[]` | 所用准则没有找到调整集。 |
| `None` | 没有评估或不适用。 |

`estimates.per_set` 将每个集合与其状态、估计和实际样本信息关联。查看它，而不是把成功估计列表与所有调整集按位置配对。集合满足图准则，与它能否在当前样本中得到数值估计，是两个判断。

`estimates.primary_adjustment_summary` 描述实际选中估计集合，包含 `adjustment_set`、`estimate`、样本量 `n`、保留比例 `coverage` 等。`largest_adjustment_summary` 描述图上变量数最多的所有有效集合；不保证它们均能得到数值估计。

平均处理效应以结果变量的原始单位表示。若结果是 0/1 访问记录，0.03 是三个百分点。数值 0 表示估计效应为零；`None` 或没有估计值不表示零效应。

## 提供的假设与图处理

`provenance.run_config` 保存提供的设置，`provenance.core_effective_config` 保存实际应用的设置。`provenance.direction_constraints` 记录研究者提供的方向，区别于算法发现。模型标识和库版本用于追溯，不需要使用者手工维护版本号。

当前 ADJ 示例显式豁免调整可行性要求。相关原因和准则说明随结果保存，估计依赖这些额外前提，不能只因为存在调整集就宣称完整准则已经认证。详见[研究假设](<configuration.md#研究假设>)。

若使用去环政策，`estimates.graph_postprocessing` 保存删边假设与共同调整集。`graph` 保留原发现结构。估计针对这些附加假设，不表示算法确认了哪条原始边应删除。

## 执行状态

`status` 为 `completed`、`completed_with_errors` 或 `failed`。它说明包能观察到的执行情况，不给出“因果结论正确”的认证。ADJ 是否得到估计，另看 `estimates.adjustment_status` 和逐集记录。

## 保存与重新读取

CLI 在选定目录保存 `result.json`、`config.resolved.json` 和 `input_mapping.json`，分别对应结果、实际配置与输入映射。使用 Python 读取即可，不重新调用模型：

```python
import json
from pathlib import Path

result = json.loads(Path("runs/apple-mb/result.json").read_text(encoding="utf-8"))
print(result["method"], result["status"])
print(result["factors"])
```

输出目录还可能含因子测量表、示例和过程记录，原始会话仅在开启时保存。整个目录按原始数据的隐私要求管理。

[独立标注](<annotation.md>)返回 `AnnotationResult`，不是上述发现字典。其 `values` 是测量表，`metadata` 保存概率、置信度与提及信息，`specs` 保存测量规范。[固定图估计](<causality.md>)的逐集记录则位于 `diagnostics.sets`。
