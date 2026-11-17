<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# 配置和运行工作区

工作区保存带名称的模型连接，供多次分析复用。请先[安装软件并准备示例文件](<installation.md>)，再进入示例工作目录运行以下命令。工作区命令需要使用包含该接口的代码版本构建的软件包。

## 使用终端向导

运行 `coatlearn setup`，选择模型来源并保存连接。分别为主模型和标注模型创建连接。运行 `coatlearn run`，选择分析方法、数据列和连接。运行向导先检查计划，再询问是否执行。

主模型是提出因子的大语言模型（LLM）。标注可以使用 LLM、托管的 Jev，或本地及已有服务中的 Kev。Jev 只连接已有的托管服务。本地安装和启动 Kev 请看[部署本地 Kev](<kev.md>)；`coatlearn setup local prepare` 需要 `--execute` 才会安装依赖和下载权重，`coatlearn setup local start` 会在前台运行。

## 使用非交互命令

将 DeepSeek 保存为主连接，Jev 保存为决策连接，准备示例并查看分析计划：

```bash
coatlearn setup connection main --backend openai --provider deepseek --model deepseek-flash --address https://api.deepseek.com --api-key-env DEEPSEEK_API_KEY --replace
coatlearn setup connection decision --backend jev --model jev-1.14.0 --address https://api.typesafe.ai --api-key-env TYPESAFE_API_KEY --replace
coatlearn setup prepare --method mb --directory . --decision-kind model
coatlearn run mb --config config/mb.toml --main-connection main --decision-kind model --decision-connection decision
```

准备命令在首次运行前下载或复制示例文件，重复运行时复用已有文件。`--replace` 在连接名称已存在时保存更新。最后一条命令只检查计划，不调用模型。加上 `--execute` 才会执行。PAG 和 ADJ 分别使用 `coatlearn run pag` 和 `coatlearn run adj` 及对应配置。`--data`、`--text-col`、任务数据列、`--rounds`、`--concurrency` 和 `--output` 可以覆盖配置中的值。PAG 使用多个 `--known-variable` 指定已有变量。`--connections` 可以选择其他连接文件。运行 `coatlearn run --help` 查看所有选项。[首页规划器](https://causalcoat.github.io/index-zh.html#use)可以按选择生成命令；按钮只复制，不执行。

不指定输出目录时，每次执行都会在 `runs/` 下自动创建以方法命名的唯一目录。只有需要指定目录时才填写 `--output`。

Python 先准备资源，再使用相同的命名连接：

```python
from coatlearn.preparation import prepare_resources
from coatlearn.workspace import run_task

prepare_resources(method="mb", decision_kind="model")
result = run_task("mb", config="config/mb.toml", main_connection="main",
                  decision_kind="model", decision_connection="decision", execute=True)
```

省略 `execute=True` 时只检查，不执行。PAG 的 `known_variables` 覆盖值是列名列表。

## 设置密钥

连接只保存环境变量名，不保存密钥。执行前请在终端设置变量。DeepSeek 使用 `DEEPSEEK_API_KEY`，Jev 使用 `TYPESAFE_API_KEY`，也可以在连接中指定其他变量名。vLLM 连接默认同样要求非空的 `VLLM_API_KEY`；使用服务配置的值，如果服务允许占位值，也可使用占位值。

可以通过 `--env-file` 或 `run_task(..., env_file=".env")` 明确选择私有 dotenv 文件。不要上传 `.env` 文件或日志，因为其中可能包含密钥或私有数据。更多信息请看[模型密钥](<models.md#凭据>)。
