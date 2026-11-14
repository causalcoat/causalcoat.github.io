<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# 安装与准备分析

先安装 Python 包，再为数据和任务配置准备工作目录。安装 coatlearn 不会下载模型权重、启动服务或向模型发送数据。

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

```bash
python -m pip install coatlearn
python -m coatlearn --help
```

`python -m pip` 确保使用选中的 Python 安装。本包同时提供 Python 接口和 `coatlearn` 命令；`python -m coatlearn` 通过该解释器调用相同命令。

查看已安装版本，不会调用模型：

```bash
python -m pip show coatlearn
```

普通安装可以使用托管聊天模型、托管 Jev，也能连接已经运行的本地 Kev 服务，不要求本机有 GPU。大多数使用者无需安装额外依赖。

| 额外工作 | 安装方式 | 下一步 |
| --- | --- | --- |
| 使用 LiNGAM 代替通常的图学习流程 | `python -m pip install "coatlearn[lingam]"` | 在分析选项中明确选择对应方法。 |
| 在自己的 GPU 上加载并部署 Kev | `python -m pip install "coatlearn[kev]"` | 按[独立 GPU 环境与部署指南](<kev.md>)完成设置，包括安装上游 Kev。 |

以后更新时使用 `python -m pip install --upgrade coatlearn`。只有修改库本身时才需要[开发者安装](<https://github.com/causalcoat/COAT-Learn/tree/main/CONTRIBUTING.md>)，普通分析无需源码安装。

## 3. 准备示例工作目录

安装包包含库和 CLI，不会把示例数据、配置自动放进当前目录。把三份任务配置、两份 CSV 及数据署名说明下载到新的 `coat-example` 目录即可，不需要 Git 或克隆仓库。

运行下面的 Python 代码一次。可以保存为 `prepare_example.py` 后运行 `python prepare_example.py`，也可以放在 notebook 单元格中执行。代码从项目 GitHub 仓库下载公开文件，不执行下载的代码，也不调用模型。

```python
from pathlib import Path
from urllib.request import urlretrieve

root = Path("coat-example")
root.mkdir(exist_ok=False)
base = "https://raw.githubusercontent.com/causalcoat/COAT-Learn/main/"
files = [
    "config/mb.toml",
    "config/pag.toml",
    "config/adj.toml",
    "data/apple_reviews_PAG_graph1.csv",
    "data/hillstrom_email_visit_post.csv",
    "data/README.md",
    "data/LICENSE",
]
for name in files:
    destination = root / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(base + name, destination)
print(root.resolve())
```

如果已有 `coat-example`，请换一个新目录名。两份 CSV 采用 CC BY 4.0，分享时保留下载的数据来源和许可说明。

在终端进入刚创建的目录：

```bash
cd coat-example
python -m coatlearn mb --config config/mb.toml --decision-model jev
```

命令只读取本地数据和配置，显示 1000 行，不调用模型。此时工作目录为：

```text
coat-example/
├── config/
│   ├── mb.toml
│   ├── pag.toml
│   └── adj.toml
└── data/
    ├── apple_reviews_PAG_graph1.csv
    ├── hillstrom_email_visit_post.csv
    ├── README.md
    └── LICENSE
```

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

示例用托管 DeepSeek Flash 提出因子，并声明多个决策模型连接。`--decision-model jev` 让托管 Jev 负责标注、定义审核和去重，无需本地模型服务。默认决策连接为本地 Kev-9B，需要先启动对应服务。

使用托管模型时，按[模型连接指南](<models.md#凭据>)准备 `DEEPSEEK_API_KEY` 与 `TYPESAFE_API_KEY`。实际密钥放在环境变量或私有 dotenv 文件中，不写进 TOML。CLI 只有加上 `--run` 执行时才读取明确指定的 dotenv 文件。

接着跟随[第一个分析](<quickstart.md>)连接模型、运行 MB 并读取结果。加上 `--run` 会把所选文本发送给配置的服务，也可能产生费用；安装和本地查看都不会。
