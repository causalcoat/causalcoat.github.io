<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# 安装与准备分析

安装 coatlearn，并为示例分析准备工作目录。

## 1. 创建 Python 环境

使用 Python 3.11 或更新版本。虚拟环境把这次分析需要的依赖与其他项目分开。在 macOS 或 Linux 终端中执行：

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
```

Windows 使用 PowerShell：

```powershell
py -3 --version
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

激活后，`python` 和 `pip` 指向这个环境。安装包和执行分析时使用同一个环境。在 notebook 中，将该环境选为 notebook 内核。

## 2. 从 PyPI 安装

在当前环境中安装软件包，并打开命令帮助：

```bash
python -m pip install coatlearn
python -m coatlearn --help
```

`python -m pip` 确保使用选中的 Python 安装。本包同时提供 Python 接口和 `coatlearn` 命令；`python -m coatlearn` 通过该解释器调用相同命令。

查看已安装版本，不会调用模型：

```bash
python -m pip show coatlearn
```

PyPI 已发布的软件包可能早于下文的工作区命令。本指南需要使用包含 `coatlearn setup prepare` 的代码版本构建的软件包。

普通安装可以使用托管聊天模型、托管 Jev，也能连接已经运行的本地 Kev 服务，不要求本机有 GPU。大多数使用者无需安装额外依赖。

| 额外工作 | 安装方式 | 下一步 |
| --- | --- | --- |
| 使用 LiNGAM 代替通常的图学习流程 | `python -m pip install "coatlearn[lingam]"` | 在分析选项中明确选择对应方法。 |
| 在自己的 GPU 上加载并部署 Kev | `python -m pip install "coatlearn[kev]"` | 按[独立 GPU 环境与部署指南](<kev.md>)完成设置，包括安装上游 Kev。 |

以后更新时使用 `python -m pip install --upgrade coatlearn`。只有修改库本身时才需要[开发者安装](<https://github.com/causalcoat/COAT-Learn/tree/main/CONTRIBUTING.md>)，普通分析无需源码安装。

## 3. 准备示例工作目录

创建并进入工作目录，再明确准备示例文件：

```bash
mkdir -p coat-example
cd coat-example
coatlearn setup prepare --method all --directory . --decision-kind llm
```

将 `all` 换成 `mb`、`pag` 或 `adj`，可以只准备一种示例。命令下载或复制示例配置、数据、署名和许可文件。已有文件会复用。分享数据时请保留署名和许可文件。

LLM 标注还需要 WordNet 词库。`--decision-kind llm` 默认下载词库；`--decision-kind model` 默认不下载。也可以用 `--wordnet` 或 `--no-wordnet` 明确选择。使用自有数据时，指定 `--method none --decision-kind llm`，只准备词库，不下载示例文件。准备资源不会调用模型。以后需要时可以再次运行，已有资源会复用。

## 4. 理解配置文件

**任务配置**是保存数据、模型连接与分析设置的 TOML 文本文件，与 Python 安装和模型凭据分开。使用 `--config` 明确选择它。

从最接近问题的下载任务开始：MB 研究一个目标，PAG 从已有测量变量出发，ADJ 研究指定处理与结果。首次教程直接保留示例。分析自己的数据时，复制任务为新文件，再修改 `[task]` 部分，例如：

```toml
[task]
method = "mb"
data = "../data/my_reviews.csv"
target = "rating"
text_col = "review"
```

这只是一个区段，不是完整配置；保留复制文件中的模型和分析部分。`data` 相对于配置文件解析：`config/` 中的任务通过 `../data/` 读取 `data/` 中的文件。列名要与 CSV 一致。数值映射、模型角色与统计参数见[准备数据](<data.md>)及[配置参考](<configuration.md>)。

## 5. 执行前连接模型

示例用托管 DeepSeek Flash 提出因子，并声明多个决策模型连接。使用命名 Jev 连接，让托管 Jev 负责标注、定义审核和去重，无需本地模型服务。默认决策连接为本地 Kev-9B，需要先启动对应服务。

使用托管模型时，按[模型连接指南](<models.md#凭据>)准备 `DEEPSEEK_API_KEY` 与 `TYPESAFE_API_KEY`。实际密钥放在环境变量或私有 dotenv 文件中，不写进 TOML。CLI 执行分析时读取明确指定的 dotenv 文件。

接着跟随[第一个分析](<quickstart.md>)连接模型、运行 MB 并读取结果。执行分析会把所选文本发送给配置的服务，也可能产生费用；安装和本地查看都不会。
