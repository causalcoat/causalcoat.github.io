<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# 标注已有因子

如果你已经知道要测量哪些属性，可以直接把定义应用到每条观测，得到数值表，不必运行因子发现。例如，你想把评论中的甜度整理成一列，用于汇总分布或与已有评分一起建模。

**因子标注**包含两件事：先写明统一的赋值规则，再让标注模型按规则逐条判断。定义是列的含义，标注值是某一行的测量结果。标注不等于判断因果关系。

本页示例使用[托管 Jev](<models.md#连接托管模型>)，执行前需要在环境变量中准备 `TYPESAFE_API_KEY`。也可以在[启动 Kev](<kev.md>)后将 `jev` 换为 `kev9b`。

## 写一份可以赋值的定义

定义应说明属性是什么、可以取哪些值，以及什么内容支持每个值。下面定义“评论描述的甜度”，只测量评论中的明确表达，不要求模型判断苹果在现实中的客观含糖量：

```python
definition = """Sweetness
- Type: score
- Values: 0, 1, 2
- Mentioned when: the text describes the apple's sweetness
- 0: explicitly described as not sweet
- 1: explicitly described as mildly sweet
- 2: explicitly described as very sweet
"""
```

`Type: score` 表示有顺序的档位，`Values` 是各档对应的原始数值，`Mentioned when` 是足以赋值的提及条件。最后三行规定各档的判断标准。发现配置将这种格式称为 `general`，可以为不同因子声明不同量表。

未提到甜度的评论不应因此变成“不甜”。提及问题的 yes 概率低于 0.5 时，本接口把该条测量记为缺失值 `NaN`。这里的零已经有明确含义：评论明确说不甜。

## 批量标注并保存

接着运行以下代码。它会将两条示例文本发给选定的标注服务：

```python
from coatlearn.annotation import annotate
from coatlearn.models.presets import jev

annotations = annotate(
    texts=["Very sweet apples.", "The delivery arrived yesterday."],
    definitions={"Sweetness": definition},
    model=jev,
)
print(annotations.values)
print(annotations.metadata[["factor", "value", "confidence", "mention_probability"]])
annotations.values.to_csv("values.csv", index=False)
```

`annotations.values` 每行对应输入观测，每列对应一个因子。`annotations.metadata` 单独保存概率、置信度和缺失说明。`annotations.specs` 保存实际使用的测量规范，便于之后检查题目与数值映射。

根据定义，第一条评论支持“很甜”，第二条没有提供甜度信息。具体数值由模型返回的概率计算，不预设为固定输出。输入为 pandas Series 时，测量表保留原索引，可以与原始数值列对齐。

多个因子可以一起放入 `definitions` 映射。`batch_size` 控制一次请求包含多少个因子，最多为 8；`concurrency` 控制并行工作线程数，默认 16。每次请求使用一条文本，完整定义会被自动转为问题。

## 理解数值与置信度

`score` 的值是各档概率对声明数值的加权平均。若 0、1、2 的概率分别为 0.1、0.2、0.7，测量值就是 `0×0.1 + 1×0.2 + 2×0.7 = 1.6`。它不是“有 1.6 的置信度”，也不一定是整数。

`choice` 用于互斥类别，返回选中类别在定义中声明的数值编码。例如，下面将购买渠道编码为 0 和 1。编码不表示两个类别具有大小关系：

```python
channel_definition = """PurchaseChannel
- Type: choice
- Values: online=0, store=1
- Mentioned when: the text explicitly states where the purchase was made
- online: purchased through an online shop
- store: purchased at a physical shop
"""
```

置信度描述模型回答的不确定性，因子值描述观测的属性，两者分开保存。分类编码应按后续统计方法的需要处理，不能仅因使用数字就将类别视为连续量。

## 按需检查测量题目

一般使用 `annotate` 不需要手工解析定义。它会在发请求前，自动把定义转为 `MeasurementSpec`，即模型题目、提及判断和数值映射的说明。

如果你想先检查服务究竟会被问什么，可以只做这一步转换。它不调用模型，不为文本赋值，也不让另一个模型改写你的规则：

```python
from coatlearn.annotation import factor_definition_to_spec

spec = factor_definition_to_spec("Sweetness", definition)
print(spec.to_request_questions())
```

另一个可用格式是 `simple`：为每个因子规定 `-1`、`0`、`1` 三个标签及对应条件，按选中标签直接取值。它适合已按三档定义的属性，不要求所有因子都改用三档；从本页开始时使用上面的 `general` 定义即可。

## 按需审核和比较定义

自写定义可以直接用于标注。如果希望先检查规则表达与格式，可以显式调用 `review_definition`，提供真实的应用示例：

```python
from coatlearn.annotation import review_definition

review = review_definition(
    "Sweetness", definition,
    examples="- The apple is very sweet.\n- This apple is not sweet.",
    model=jev,
)
print(review["decision"])
```

审核检查定义是否清楚、格式是否满足要求，不证明属性客观可测或与结果有因果关系。记录中可能包含提供的示例，应私下保存。

如果候选定义很多，可用 `compare_definitions` 判断两个定义是否描述同一核心属性。例如，比较甜度与购买渠道：

```python
from coatlearn.annotation import compare_definitions

comparison = compare_definitions(
    definition, channel_definition,
    task_context="Identify attributes explicitly described in apple reviews.",
    model=jev,
)
print(comparison["decision"])
```

概念比较用于识别属性重复，不因相关就合并变量，也不会让两个不同定义下的取值自动互换。独立 `annotate` 不自动运行审核或概念比较；完整发现流程是否启用它们，由[模型角色配置](<configuration.md#模型角色>)决定。
