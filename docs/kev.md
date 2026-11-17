<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# Deploy local Kev

Kev lets you run factor annotation, definition review and concept deduplication on your own machine. This independent decision model answers classification, rating and yes/no questions under supplied rules. This guide starts a server matching the package's `kev9b` preset and connects from the analysis process.

This guide uses NVIDIA CUDA, a GPU supporting BF16 and a separate Python 3.12 environment. Allow enough GPU memory and disk space for the base model, adapter and inference. If you do not want to prepare local hardware, use [hosted Jev](<models.md#connect-hosted-models>).

## 1. Prepare a separate environment

Install coatlearn’s GPU dependencies from PyPI. `KEV_WORK` is your chosen model directory. Python 3.12 and Git must already be installed.

```bash
export KEV_WORK="$HOME/coatlearn-kev"
mkdir -p "$KEV_WORK"
python3.12 -m venv "$KEV_WORK/.venv"
git clone https://github.com/jaredpalmer/kev.git "$KEV_WORK/source"
"$KEV_WORK/.venv/bin/python" -m pip install \
  "coatlearn[kev]" "$KEV_WORK/source"
export HF_HOME="$KEV_WORK/cache"
```

Install Kev from its [upstream source](https://github.com/jaredpalmer/kev). Do not run `pip install kev`: the PyPI name belongs to another project. This setup does not install the upstream `serve` extra or use the TypeSafe SDK. The HTTP runner comes from this package.

The analysis process can keep its original Python environment. Only the separate process loading Kev weights needs GPU dependencies.

## 2. Download matching weights

Kev-9B uses a base model and an adapter. The **base model** provides general language representations; the **adapter** contains additional weights trained for Kev. This step downloads the released Kev weights and the base-model snapshot specified in their metadata from Hugging Face. It requires network access.

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

`v1.0` selects a published upstream weight release. Downloading the base from metadata avoids pairing the adapter with different base weights. See the [Kev-9B model card](https://github.com/jaredpalmer/kev/blob/main/docs/model-cards/kev-9b.md).

## 3. Start the server

Start the server in the same terminal and leave it running during analysis:

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

Once loading finishes, the terminal prints a record containing `"ready": true`. The runner uses the prepared local weights with CUDA BF16 and serves `POST /v1/systemone` at `127.0.0.1:8019`. It does not download weights or fall back to a hosted model.

From another terminal, inspect the server information:

```bash
curl --fail http://127.0.0.1:8019/health
```

The response's `model` should be `kev-9b-v1.0`. `/health` belongs to this package's runner; it is not an endpoint provided by every upstream Kev server.

## 4. Connect from analysis

Return to your coatlearn analysis environment and run from the `coat-example` directory prepared in the [installation guide](<installation.md>):

```bash
python -m coatlearn mb --config config/mb.toml
# Prepare DEEPSEEK_API_KEY and permit proposal examples to reach the main model:
python -m coatlearn mb --config config/mb.toml --run --output-dir runs/apple-kev
```

The default configuration directs annotation, review and deduplication to the Kev-9B server you started. The main model remains hosted DeepSeek Flash, so `DEEPSEEK_API_KEY` is still required and proposal examples still go to DeepSeek. Local Kev requires no TypeSafe key.

8019 is the project's chosen Kev-9B port; 8014 is its example Kev-4B port. Both can change. Keep the server's `port` consistent with the corresponding TOML model's `base_url` or Python preset override. A port is neither part of the weights nor a fixed Kev requirement.

## Use Kev-4B

In a separate working directory, follow the same steps with the released `jaredpalmer/kev-4b` weights and the base model identified in their metadata. Start with `model="kev-4b-v1.0"` and `port=8014`, then select `--decision-model kev4b`. Do not rename a server to 4B while still loading 9B weights.

## Difference from the upstream server

This guide uses coatlearn's runner, which requires the requested model identifier to match its startup identifier. Upstream `python -m kev.serve` uses service aliases such as `kev-latest`; this package's `KevConfig` accepts `kev-9b-v1.0` or `kev-4b-v1.0`. Starting the upstream example command therefore does not by itself produce a server matching this package's presets.

This runner serializes GPU work, uses an 8,192-token state budget and enables neither quantization nor CUDA graphs. Answer probabilities retain their computed precision without extra rounding for HTTP serialization. The runner uses BF16 weights, and annotation can contain errors.

Upstream provides other devices and deployment options; see [Kev documentation](https://github.com/jaredpalmer/kev). Distinguish those capabilities from the CUDA loopback runner described here.
