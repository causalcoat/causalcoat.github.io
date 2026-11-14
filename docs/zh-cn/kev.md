<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# 部署本地 Kev

使用 Kev 可以让因子标注、定义审核和概念去重在本机执行。Kev 是独立的决策模型，不是聊天模型；它回答给定规则下的分类、评分和是非问题。下面启动与本包 `kev9b` 预设匹配的服务，再从分析进程连接它。

本指南使用 NVIDIA CUDA、支持 BF16 的 GPU，以及独立的 Python 3.12 环境。需要为基础模型、适配器和推理留出足够显存及磁盘空间。若不准备本地硬件，可以改用[托管 Jev](<models.md#连接托管模型>)。

## 1. 准备独立环境

下面从 PyPI 安装 coatlearn 的 GPU 依赖。`KEV_WORK` 是自行选择的模型工作目录，不是项目要求的固定路径。需要系统已安装 Python 3.12 和 Git。

```bash
export KEV_WORK="$HOME/coatlearn-kev"
mkdir -p "$KEV_WORK"
python3.12 -m venv "$KEV_WORK/.venv"
git clone https://github.com/jaredpalmer/kev.git "$KEV_WORK/source"
"$KEV_WORK/.venv/bin/python" -m pip install \
  "coatlearn[kev]" "$KEV_WORK/source"
export HF_HOME="$KEV_WORK/cache"
```

Kev 从[上游源码](https://github.com/jaredpalmer/kev)安装。不要执行 `pip install kev`，PyPI 上的同名包是其他项目。这里不安装上游的 `serve` extra，也不使用 TypeSafe SDK；服务由本包的 HTTP 入口提供。

分析进程仍可使用原来的 Python 环境。只有加载 Kev 权重的独立进程需要 GPU 依赖。

## 2. 下载匹配权重

Kev-9B 使用基础模型加适配器。**基础模型**提供通用语言表示，**适配器**是 Kev 训练得到的附加权重。这一步从 Hugging Face 下载 Kev 发布权重，以及其元数据指定的基础模型快照，需要联网。

```bash
"$KEV_WORK/.venv/bin/python" - <<'PY'
import os
from pathlib import Path
from huggingface_hub import snapshot_download
from kev.checkpoint import Checkpoint

work = Path(os.environ["KEV_WORK"])
snapshot_download("jaredpalmer/kev-9b", revision="v1.0", local_dir=work / "adapter")
checkpoint = Checkpoint(str(work / "adapter"))
snapshot_download(
    checkpoint.meta.base,
    revision=checkpoint.meta.base_revision,
    local_dir=work / "base",
)
PY
```

`v1.0` 选择上游已经发布的一份模型权重；它不是需要你维护的项目版本。按元数据下载基础模型，避免把 Kev 适配器配到另一份基础权重上。权重说明见 [Kev-9B 模型卡](https://github.com/jaredpalmer/kev/blob/main/docs/model-cards/kev-9b.md)。

## 3. 启动服务

在同一终端启动服务，并让它在分析期间保持运行：

```bash
"$KEV_WORK/.venv/bin/python" - <<'PY'
import os
from pathlib import Path
from coatlearn.models.kev_server import serve

work = Path(os.environ["KEV_WORK"])
serve(
    checkpoint=str(work / "adapter"),
    base_model=str(work / "base"),
    source_dir=str(work / "source"),
    model="kev-9b-v1.0",
    port=8019,
)
PY
```

加载完成后，终端会打印包含 `"ready": true` 的记录。入口只使用准备好的本地权重，以 CUDA BF16 执行，并在 `127.0.0.1:8019` 提供 `POST /v1/systemone`。它不负责下载，不会退回托管模型。

在另一个终端查看服务信息：

```bash
curl --fail http://127.0.0.1:8019/health
```

响应中的 `model` 应为 `kev-9b-v1.0`。`/health` 是本包服务的地址，不是上游所有 Kev 服务都具有的接口。

## 4. 从分析进程连接

回到安装了 coatlearn 的分析环境，在[安装指南](<installation.md>)准备的 `coat-example` 目录执行：

```bash
python -m coatlearn mb --config config/mb.toml
# 准备 DEEPSEEK_API_KEY，并确认允许向主模型发送提议示例后：
python -m coatlearn mb --config config/mb.toml --run --output-dir runs/apple-kev
```

默认配置把标注、审核和去重指向刚启动的 Kev-9B。主模型仍为托管 DeepSeek Flash，因此仍需 `DEEPSEEK_API_KEY`，提议示例仍会发往 DeepSeek。本地 Kev 不需要 TypeSafe 密钥。

8019 是本项目给 Kev-9B 选用的端口，8014 是 Kev-4B 的示例端口，都可以修改。修改时，服务的 `port`、TOML 中对应模型的 `base_url`，或 Python 预设覆盖值必须一致。端口不是模型权重的一部分，也不是 Kev 固定要求。

## 使用 Kev-4B

若选择 Kev-4B，在单独工作目录中按相同步骤下载 `jaredpalmer/kev-4b` 的发布权重及其元数据指定的基础模型。启动时使用 `model="kev-4b-v1.0"`、`port=8014`，再通过 `--decision-model kev4b` 选择它。不能只把 9B 服务的名称改为 4B，却仍加载 9B 权重。

## 与上游服务的区别

本指南使用的是 coatlearn 的服务入口，它要求请求的模型标识与启动时的标识一致。上游 `python -m kev.serve` 使用 `kev-latest` 等服务别名；本包 `KevConfig` 接受的是 `kev-9b-v1.0` 或 `kev-4b-v1.0`。因此，直接启动上游示例命令并不等于启动了与本包预设匹配的服务。

本包入口在 GPU 上串行执行请求，状态文本预算为 8192 token，不启用量化或 CUDA graphs。返回的概率保留计算精度，不在 HTTP 序列化时额外舍入；这不表示权重使用 FP32，也不表示标注没有误差。

上游还提供其他设备与部署方式，见 [Kev 文档](https://github.com/jaredpalmer/kev)。这些能力与本页 CUDA 本地入口的行为分开理解。
