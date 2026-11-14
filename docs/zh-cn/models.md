<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# 连接模型

运行发现前，需要让 coatlearn 连接能提出因子的模型和能逐条赋值的模型。两项工作可以使用不同服务。安装 Python 包不会自动下载权重，也不会启动模型。

## 先分清模型与服务

**聊天模型**根据提示生成因子名称、定义与修订。**决策模型**根据已写好的规则回答是非、分类或评分问题，用于因子标注、定义审核与概念去重。这些模型角色都不直接认证因果关系。

| 名称 | 是什么 | 在本项目中怎么用 |
| --- | --- | --- |
| DeepSeek Flash | 托管聊天模型 | 所附配置用它提出和修订因子。需要 `DEEPSEEK_API_KEY`。 |
| Jev | TypeSafe 提供的托管决策模型 | 不必部署本地权重。用 `TYPESAFE_API_KEY` 调用。 |
| Kev | 可自行运行的独立决策模型，与 Jev 的 System One 请求格式兼容 | 在另一进程中启动，再用本机 HTTP 地址连接。见[部署指南](<kev.md>)。 |
| vLLM | 部署语言模型的推理服务软件 | 可用于提供本地聊天模型的 OpenAI-compatible 接口。它不是模型名称，也不是 Kev 的启动方式。 |

**OpenAI-compatible** 表示服务接受与 OpenAI 聊天接口兼容的请求，不表示请求一定发往 OpenAI。Jev/Kev 使用另一种接口：`POST /v1/systemone`。本包通过 HTTP 直接调用这一官方请求格式，不使用 TypeSafe SDK。见 [TypeSafe 接口](https://docs.typesafe.ai/api)。

## 连接托管模型

第一次运行可直接使用已有预设，不必填写模型版本。**预设**是一份命名连接设置，包含模型标识、地址和密钥环境变量名称，并不是已启动的模型。

在[安装指南](<installation.md>)准备的 `coat-example` 目录中，先在 shell 中准备 `DEEPSEEK_API_KEY` 与 `TYPESAFE_API_KEY`，再把示例的三个决策角色一起切换为 Jev：

```bash
python -m coatlearn mb --config config/mb.toml --decision-model jev
# 确认配置和文本发送位置后再执行：
python -m coatlearn mb --config config/mb.toml --decision-model jev --run --output-dir runs/apple-jev
```

若要从 Python 直接进行一次 Jev 调用，可以使用预设中的配置。这会将下面的示例文本发给 TypeSafe：

```python
from coatlearn.models import JevClient
from coatlearn.models.presets import jev

client = JevClient(jev.config)
response = client.system_one(
    state="The apple tastes sweet.",
    questions={"sweet": {"type": "noul", "instructions": "Does the text describe a sweet taste?"}},
)
print(response["answers"])
```

System One 将待分析内容称为 `state`，待回答的问题称为 `questions`。`noul` 回答 yes 的概率；`choice` 选择类别；`score` 返回有序档位的概率。只想按因子定义批量赋值时，使用[标注接口](<annotation.md>)，无需自己构造这些题目。

## 使用预设与模型标识

预设保存了与项目示例匹配的模型标识。直接导入即可使用：

| 预设 | 保存的模型标识 | 地址 | 密钥变量 |
| --- | --- | --- | --- |
| `dpsk41f` | `deepseek-flash` | `https://api.deepseek.com` | `DEEPSEEK_API_KEY` |
| `jev` | `jev-1.14.0` | `https://api.typesafe.ai` | `TYPESAFE_API_KEY` |
| `kev9b` | `kev-9b-v1.0` | `http://127.0.0.1:8019` | 无 |
| `kev4b` | `kev-4b-v1.0` | `http://127.0.0.1:8014` | 无 |

模型标识告诉服务这次请求要用哪个模型，不是你需要手工维护的 coatlearn 版本号。使用预设时不用重复填写。连接其他服务或自己部署权重时，才需要按服务接受的标识设置 `model`。结果会记录它，便于追溯运行所用模型。`deepseek-flash` 是服务商维护的别名，不是固定的本地权重快照。

预设可以生成独立的定制配置。例如，降低主模型并发，或修改本地 Kev 端口：

```python
from coatlearn.models.presets import dpsk41f, kev9b

main = dpsk41f(max_concurrency=3, env_file=None)
annotation = kev9b(base_url="http://127.0.0.1:8020")
```

这里的 8020 是自选示例端口，需与服务启动时的端口一致。8019 和 8014 也只是项目约定，不是 Kev 的固定端口；改端口不会启动或移动服务。`127.0.0.1` 指运行客户端的本机。本包 Kev 客户端使用本机回环 HTTP 地址，不读取服务商密钥。

Python 预设默认可从当前工作目录的 `.env` 读取需要的密钥，`env_file=None` 关闭这一读取。每次执行会创建独立客户端，不共享测量缓存或计数状态。

## 连接其他聊天服务

使用 `ModelConfig` 指定服务提供的模型标识、聊天接口地址和密钥环境变量名称。下面只创建连接描述，不发请求：

```python
from coatlearn.models import ModelConfig

main = ModelConfig(
    model="your-served-model",
    base_url="https://your-provider.example/v1",
    api_key_env="MY_MODEL_API_KEY",
)
```

把 `main` 传给 `run_mb`、`run_pag` 或 `run_adj` 的 `main_model`。地址和标识应替换为实际服务值；密钥值保留在环境变量中。

### 连接 vLLM

如果已经使用 vLLM 部署聊天模型，沿用同一接口即可。vLLM 在独立终端中加载权重，coatlearn 通过 HTTP 请求它。以下是启动形式，`/path/to/chat-model` 需要替换为支持聊天的模型路径：

```bash
vllm serve /path/to/chat-model \
  --served-model-name coat-chat --host 127.0.0.1 --port 8001
```

在运行 coatlearn 的终端设置 `VLLM_API_KEY`。若服务没有开启鉴权，本客户端仍要求一个非空占位值，例如 `local`；若开启了鉴权，则应使用匹配的密钥。连接配置与启动参数对应：

```python
from coatlearn.models import ModelConfig

main = ModelConfig(
    model="coat-chat",
    base_url="http://127.0.0.1:8001/v1",
    api_key_env="VLLM_API_KEY",
)
```

`coat-chat` 对应 `--served-model-name`，8001 对应 `--port`，`/v1` 是聊天 API 前缀。安装、硬件和模型支持范围见 [vLLM 官方说明](https://docs.vllm.ai/en/latest/serving/online_serving/openai_compatible_server/)。本包不在分析进程中加载 vLLM 权重，也不管理其 GPU 进程。

## 凭据

密钥通过环境变量提供，不写入 TOML、Python 源码或结果。例如，`api_key_env="TYPESAFE_API_KEY"` 保存的是变量名称，执行时才读取其值。

CLI 默认只使用已导出的环境变量。也可以显式选择一个私有 dotenv 文件：

```bash
python -m coatlearn mb --config config/mb.toml --decision-model jev --env-file .env --run --output-dir runs/apple-env
```

dotenv 是以 `变量名=值` 保存配置的本地文本文件。CLI 只在加 `--run`、完成本地数据检查后读取选中的文件，并只加载本次需要的密钥；不会向父目录搜索。已有进程环境值优先。

Python 显式配置（`ModelConfig`、`JevConfig`）只读取环境变量；预设还支持其选定的 dotenv 文件。托管主模型会收到提议示例，托管标注模型会收到待赋值文本。本地 Kev 只让决策请求留在本机，不会把托管主模型也自动变成本地模型。
