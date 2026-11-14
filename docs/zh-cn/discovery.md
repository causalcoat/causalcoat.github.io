<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# 发现接口

不知道应测量哪些属性时，使用发现接口。它们从已有数值变量和配对文本开始，组合因子提议、标注、统计筛选与反馈。三个入口都接受本地 CSV 路径或 pandas DataFrame，并返回相同结构的结果字典。

下面按研究目标列出调用方式。概念解释见[理解 COAT](<concepts.md>)；第一次完整执行见[入门指南](<quickstart.md>)。代码中的数据文件和列名需要替换为自己的输入，模型需要先按[连接说明](<models.md>)准备。

## MB：寻找关于一个目标的信息

`run_mb` 接受一个已有数值目标和文本列。它寻找马尔可夫毯，即给定这组变量后，其他候选不再提供目标额外信息的集合。

```python
from coatlearn import RunConfig, run_mb
from coatlearn.models.presets import dpsk41f, jev

result = run_mb(
    "reviews.csv", target="score", text_col="text",
    main_model=dpsk41f, annotation_model=jev,
    config=RunConfig(
        rounds=1, test_method="fisherz", alpha=0.001,
        options={"factor_template": "general"},
    ),
)
blanket = result["diagnostics"]["final_blanket"]
```

`target` 是已有数值列，`text_col` 是配对的非空文本列。`main_model` 提出因子，`annotation_model` 为观测赋值。`rounds` 控制 MB 迭代次数。

每轮都会更新当前集合。早期候选的测量仍保留在因子池中，不因先前选中过就永远入选。选中的名称位于 `diagnostics.final_blanket`，其中也含目标；定义位于 `factors`。

直接使用默认名称去重路径时，需要预先安装 WordNet 语料，见[本地依赖](<troubleshooting.md>)。若要沿用所附示例的决策模型去重、审核和其他全部设置，应加载 TOML，而不是只复制这段最小调用。

## PAG：用新变量细化结构

`run_pag` 接受一组已有数值变量，不要求预先提供图。它从这些变量的马尔可夫毯搜索开始，在有助于细化结构的位置继续补充因子，再用 causal-learn 的 FCI 算法学习部分祖先图。

```python
from coatlearn import RunConfig, run_pag
from coatlearn.models.presets import dpsk41f, jev

result = run_pag(
    "reviews.csv", known_variables=["taste", "score"], text_col="text",
    main_model=dpsk41f, annotation_model=jev,
    config=RunConfig(
        rounds=2, test_method="fisherz", alpha=0.001,
        options={"factor_template": "general", "fci_depth": 2},
    ),
)
graph = result["graph"]
```

`known_variables` 指已有的测量列，不是已知因果方向。图存放在 `graph` 中，包括节点顺序和端点矩阵。圆圈端点保留结构不确定性，不能将每条边都读成已经确定的直接因果关系。

`rounds` 同时限制每个目标的连续 MB 迭代与外层扩展批次。`fci_depth` 控制 FCI 图搜索的条件变量深度，不是所有 MB 检验的条件变量数上限。

## ADJ：为指定效应寻找调整变量

`run_adj` 接受已有处理、结果与配对文本。它组合处理和结果的马尔可夫毯搜索，扩展相关路径及其可能后代，细化 PAG，再按广义调整准则寻找调整集和计算效应。

```python
from coatlearn import RunConfig, run_adj
from coatlearn.models.presets import dpsk41f, jev

result = run_adj(
    "customers.csv", treatment="sent", outcome="visited", text_col="post",
    main_model=dpsk41f, annotation_model=jev,
    config=RunConfig(
        rounds=2, test_method="mv_fisherz", alpha=0.001,
        options={"factor_template": "general"},
    ),
)
print(result["adjustment_sets"])
print(result["estimates"])
```

直接 Python 调用中，处理列必须已编码为 0 和 1；结果列是数值列。TOML 可以显式声明原始标签的转换。方法寻找的是在当前图与假设下有效的调整集，不保证任何输入都能得到效应数值。

效应计算采用完整观测的逆概率加权，按每个调整集选择可用行。所附 ADJ 配置另有因子支持度、预测筛选、覆盖率与研究先验，这些具体阈值和政策不适用于所有 `run_adj` 调用。

## 从 Python 运行完整示例配置

使用 TOML 可以让 Python 与 CLI 采用相同数据、模型角色和分析设置：

```python
from coatlearn.configuration import load_task
from coatlearn.execution import check_task, execute_task

plan = load_task("config/pag.toml", decision_model="jev")
checked = check_task(plan)
print(checked.summary["columns_used"])
# 准备模型凭据并确认执行后：
result, directory = execute_task(checked, output_dir="runs/python-pag")
```

`load_task` 读取设置，`check_task` 只检查本地输入，`execute_task` 才执行发现。直接构造 `RunConfig` 不会自动读取示例 TOML。可调字段见[配置参考](<configuration.md>)。

## 测量缺失如何进入统计计算

`general` 定义把未提及与属性值分开，标注表中未提及记为缺失。统计输入随后由方法决定：`mv_fisherz` 保留缺失参与其条件独立性计算；当前 Fisher-Z 等不支持该缺失路径的计算在输入处填零。效应估计则对每个调整集单独选择完整观测。

这几步含义不同。保存的缺失不等于测得零，统计计算中的填零也是明确的分析政策。选择方法时，应结合自己的测量量表理解它。输出与研究假设的对应关系见[结果参考](<results.md>)。
