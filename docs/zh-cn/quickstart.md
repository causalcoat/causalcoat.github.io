<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# 第一个分析

本次分析要得到一组关于顾客评分的评论属性，以及每个属性的测量定义。我们使用所附 1000 条合成苹果评论，不需要先准备自己的数据。方法采用 COAT-MB，它通过统计反馈寻找共同提供目标信息的变量集合，称为马尔可夫毯。

本指南采用 DeepSeek Flash 提出因子、托管 Jev 完成标注和定义检查，因此不需要本地 GPU。实际执行需要两个服务的 API 访问权限，并会发送文本、产生相应调用费用。若要使用本地 Kev，先完成[本地部署](<kev.md>)，再去掉下文的 `--decision-model jev`。

## 1. 安装

使用 Python 3.11 或更新版本。在包含[项目配置](<https://github.com/causalcoat/COAT-Learn/tree/main/pyproject.toml>)的项目目录中运行本页所有命令：

```bash
git clone https://github.com/causalcoat/COAT-Learn.git
cd COAT-Learn
python3 -m pip install -e .
```

安装的是 Python 库和命令行工具，不会自动启动模型服务。

## 2. 查看输入与设置

先只查看任务，不执行模型调用：

```bash
bash examples/mb.sh --decision-model jev
```

摘要应显示 `method` 为 `mb`、`rows` 为 1000、`columns_used` 为 `Score` 和 `Review`，以及 `network_requests` 为 0。此时尚未检查密钥。

[MB 配置](<https://github.com/causalcoat/COAT-Learn/tree/main/config/mb.toml>)中，`Score` 是已有数值目标，`Review` 是每条观测的评论。虽然 CSV 还有其他列，这次分析不使用它们。配置允许五轮提出、标注和筛选，使用 Fisher-Z 条件独立性检验，显著性阈值为 0.001。因子采用带明确取值和提及条件的 `general` 定义格式。

`--decision-model jev` 还会让定义审核和概念去重使用 Jev。定义审核检查规则是否清楚；概念去重避免反复测量同一属性。它们都不判断某个属性是否为原因。

## 3. 准备凭据

把 DeepSeek 与 TypeSafe 提供的密钥分别保存在当前 shell 的 `DEEPSEEK_API_KEY` 和 `TYPESAFE_API_KEY` 环境变量中。下列命令让你交互输入，不把密钥直接写进命令历史：

```bash
read -rsp 'DeepSeek API key: ' DEEPSEEK_API_KEY; printf '\n'
export DEEPSEEK_API_KEY
read -rsp 'TypeSafe API key: ' TYPESAFE_API_KEY; printf '\n'
export TYPESAFE_API_KEY
```

环境变量只对当前 shell 及其启动的程序生效。也可以使用显式选择的 dotenv 文件，设置方法见[凭据说明](<models.md#凭据>)。

## 4. 执行发现

确认允许把示例文本发给上述服务后，执行：

```bash
bash examples/mb.sh --decision-model jev --run --output-dir runs/apple-mb
```

COAT 将选中的评论示例交给主模型提出因子，再为评论逐条赋值，用统计检验更新所选集合，并构造下一轮反馈。具体名称和运行时长取决于模型回答与发现过程，示例不预设必须发现某几个因子。

输出保存在你指定的新目录中。再次执行时选择另一个目录名，保留每次分析的设置与结果。

## 5. 阅读结果

读取保存的结果，先看执行状态，再看所选变量及其定义：

```python
import json
from pathlib import Path

result = json.loads(Path("runs/apple-mb/result.json").read_text(encoding="utf-8"))
print(result["status"])
for name in result["diagnostics"].get("final_blanket", []):
    print(name, result["factors"].get(name))
```

`final_blanket` 也包含目标 `Score`。其余名称表示本次选中的因子，`factors` 中的定义说明它们如何赋值。已有目标可能没有文字定义。马尔可夫毯是信息集合，不等于一份已经证实的直接原因清单。

同一目录中的 `config.resolved.json` 保存实际模型与参数，`input_mapping.json` 保存使用列及输入映射。逐轮记录和因子测量文件帮助追溯过程，可能包含原始评论，应与结果一起私下保存。字段含义见[结果参考](<results.md>)。

## 接下来做什么

若想了解 `Taste` 和 `Score` 的结构，查看 [PAG 示例配置](<https://github.com/causalcoat/COAT-Learn/tree/main/config/pag.toml>)。它使用同一份评论，从这两个已有变量出发寻找更多因子，以细化图的端点信息。命令为 `bash examples/pag.sh --decision-model jev`；加 `--run` 才会执行。

若想研究行动的效应，查看 [ADJ 示例配置](<https://github.com/causalcoat/COAT-Learn/tree/main/config/adj.toml>)。它使用另一份合成顾客数据，研究发送邮件对访问的影响，包含需要理解的[研究假设](<configuration.md#研究假设>)。不要把这些假设直接复制到自己的数据。

准备自己的分析时，先阅读[数据要求](<data.md>)，再按问题选择[发现接口](<discovery.md>)。已经确定属性定义时，从[独立标注](<annotation.md>)开始即可。
