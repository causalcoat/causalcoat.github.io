<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# 分析测量表与固定图

已有测量值时，可以直接做统计因果分析，不再调用语言模型。例如，你已经标注完顾客属性，想在一张明确的因果图下寻找调整集；或者已经有数值表，只想学习变量之间的图。

本页使用“顾客属性 `V`、发送邮件 `T`、网站访问 `Y`”说明接口。概念背景见[调整集与效应](<concepts.md#为什么效应估计需要调整集>)。这里的示意图是人为声明的结构，不是对示例 CSV 的发现结果。

## 声明一张固定图

先用简单的链 `V -> T -> Y` 演示图的表示：顾客属性影响邮件发送，邮件发送影响访问。在这张假设图中，没有另外声明 `V` 到 `Y` 的路径。

用 `CausalGraph` 同时保存变量名称顺序和端点矩阵：

```python
from coatlearn.causality import CausalGraph, find_adjustment_sets

graph = CausalGraph(
    node_order=("V", "T", "Y"),
    endpoint_matrix=[
        [0, -1, 0],
        [1, 0, -1],
        [0, 1, 0],
    ],
)
adjustment = find_adjustment_sets(graph, treatment="T", outcome="Y")
print(adjustment["adjustment_sets"])
```

`[i, j]` 记录边在节点 `i` 一侧的标记：`-1` 是尾线，`1` 是箭头，`2` 是未定圆圈，`0` 是无边。因此 `V -> T` 在 `V` 一侧为 `-1`，在 `T` 一侧为 `1`。更完整的读法见[端点参考](<results.md#图的端点标记>)。

`find_adjustment_sets` 使用广义调整准则，返回集合和所用图要求的诊断。方向信息不自动排除潜在混杂，因此应以该准则对输入图的实际判断为依据。

一个空调整集 `[]` 表示在相应图条件下不需要调整协变量。`adjustment_sets` 中的 `[[]]` 表示找到一个空集，而 `[]` 表示没有找到有效调整集，含义不同。

## 读取已有发现图

从保存的 PAG 或 ADJ 结果加载图，不会重新调用模型或执行发现：

```python
import json
from pathlib import Path
from coatlearn.causality import CausalGraph

result = json.loads(Path("runs/apple-pag/result.json").read_text(encoding="utf-8"))
saved_graph = CausalGraph.from_result(result)
```

图也可以来自其他发现方法或领域假设，只要转为相同的节点与端点表示。后续结论相对于输入图成立；“已有”或“固定”不代表它是真实系统的已证实结构。

## 使用测量表估计效应

准备一张包含图中变量的 pandas DataFrame，再调用 `estimate_effects`。下面是数据准备与调用形式，需换成自己的测量表及匹配图：

```python
import pandas as pd
from coatlearn.causality import estimate_effects

measured_data = pd.read_csv("measurements.csv")
estimates = estimate_effects(
    measured_data, graph,
    treatment="T", outcome="Y",
)
print(estimates["diagnostics"].get("primary_adjustment_summary"))
```

处理 `T` 使用 0/1，结果 `Y` 为数值。接口先检查图上的调整集，再对各集合使用完整观测的 IPW 估计。IPW 根据接受处理的估计概率给观测加权；没有合适调整集时，不把未调整的差异自动当作效应。

`primary_adjustment_summary` 记录选中集合、估计和样本信息，逐集记录位于 `diagnostics.sets`。二元结果的平均处理效应以概率差表示。例如 0.03 意为增加三个百分点，因果解释依赖输入图、测量与估计假设。

## 从已有数值列学习图

没有图但已有测量表时，使用 `learn_graph` 在指定列上运行 FCI。它不提出新因子，不重新标注资料：

```python
from coatlearn.causality import learn_graph, independence_test

graph = learn_graph(measured_data, columns=["V", "T", "Y"], depth=2)
p_value = independence_test(measured_data, "T", "Y", given=["V"], method="fisherz")
print(graph.to_dict())
print(p_value)
```

`independence_test` 返回条件独立性检验的 p 值，不是“因果关系为真的概率”。`given=["V"]` 表示考察在考虑 `V` 后 `T` 与 `Y` 是否仍有关联。若还需要从配对文本中发现缺少的变量，应使用[发现接口](<discovery.md>)。
