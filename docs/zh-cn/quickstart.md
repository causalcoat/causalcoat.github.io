<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# 第一个分析

本次分析要得到一组关于顾客评分的评论属性，以及每个属性的测量定义。我们使用所附 1000 条合成苹果评论，不需要先准备自己的数据。方法采用 COAT-MB，它通过统计反馈寻找共同提供目标信息的变量集合，称为马尔可夫毯。

本指南采用 DeepSeek Flash 提出因子、托管 Jev 完成标注和定义检查，因此不需要本地 GPU。执行前准备两个服务的 API 密钥。若要使用本地 Kev，请按[本地部署指南](<kev.md>)将它连接为决策模型。

## 1. 准备示例

按[安装指南](<installation.md>)创建 Python 环境并准备示例文件。下面的命令都在 `coat-example` 目录执行。工作区命令需要使用包含该接口的代码版本构建的软件包。

[MB 配置](<https://github.com/causalcoat/COAT-Learn/tree/main/config/mb.toml>)以 `Score` 为目标、`Review` 为文本，最多执行五轮，并使用显著性阈值为 0.001 的 Fisher-Z 条件独立性检验。

## 2. 保存连接

将 DeepSeek 保存为提出因子的模型，将 Jev 保存为标注、定义审核和去重的模型。连接保存密钥环境变量名；`--replace` 更新同名连接。

```bash
coatlearn setup connection main --backend openai --provider deepseek --model deepseek-flash --address https://api.deepseek.com --api-key-env DEEPSEEK_API_KEY --replace
coatlearn setup connection decision --backend jev --model jev-1.14.0 --address https://api.typesafe.ai --api-key-env TYPESAFE_API_KEY --replace
coatlearn setup prepare --method mb --directory . --decision-kind model
```

准备命令复制或下载示例配置、数据和许可文件，并复用已有文件。

## 3. 准备凭据

把 DeepSeek 与 TypeSafe 提供的密钥分别保存在当前 shell 的 `DEEPSEEK_API_KEY` 和 `TYPESAFE_API_KEY` 环境变量中。用下列命令输入密钥：

```bash
read -rsp 'DeepSeek API key: ' DEEPSEEK_API_KEY; printf '\n'
export DEEPSEEK_API_KEY
read -rsp 'TypeSafe API key: ' TYPESAFE_API_KEY; printf '\n'
export TYPESAFE_API_KEY
```

环境变量只对当前 shell 及其启动的程序生效。也可以使用显式选择的 dotenv 文件，设置方法见[凭据说明](<models.md#凭据>)。

## 4. 执行发现

运行 MB 分析：

```bash
coatlearn run mb --config config/mb.toml --main-connection main --decision-kind model --decision-connection decision --output runs/apple-mb --execute
```

COAT 将选中的评论示例交给主模型提出因子，再为评论逐条赋值，用统计检验更新所选集合，并构造下一轮反馈。每轮结果和筛选记录保存在运行目录中。

输出保存在你指定的新目录中。再次执行时选择另一个目录名，也可以省略 `--output`，在 `runs/` 下自动创建唯一目录。

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

`final_blanket` 也包含目标 `Score`。其余名称表示本次选中的因子，`factors` 中的定义说明它们如何赋值。已有目标可能没有文字定义。

同一目录中的 `config.resolved.json` 保存实际模型与参数，`input_mapping.json` 保存使用列及输入映射。逐轮记录和因子测量文件帮助追溯过程，可能包含原始评论，应与结果一起私下保存。字段含义见[结果参考](<results.md>)。

## 接下来做什么

若想了解 `Taste` 和 `Score` 的结构，查看 [PAG 示例配置](<https://github.com/causalcoat/COAT-Learn/tree/main/config/pag.toml>)。它使用同一份评论，从这两个已有变量出发寻找更多因子，以细化图的端点信息。使用 `coatlearn run pag --config config/pag.toml --main-connection main --decision-kind model --decision-connection decision` 查看计划；加 `--execute` 执行。

若想研究行动的效应，查看 [ADJ 示例配置](<https://github.com/causalcoat/COAT-Learn/tree/main/config/adj.toml>)。它使用另一份合成顾客数据，研究发送邮件对访问的影响，包含需要理解的[研究假设](<configuration.md#研究假设>)。使用自有数据时，按研究设计设置这些假设。

准备自己的分析时，先阅读[数据要求](<data.md>)，再按问题选择[发现接口](<discovery.md>)。已经确定属性定义时，从[独立标注](<annotation.md>)开始即可。
