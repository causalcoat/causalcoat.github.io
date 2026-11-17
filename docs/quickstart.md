<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# Your first analysis

This analysis produces a set of review attributes that provide information about customer ratings, with a measurement definition for each attribute. We use the supplied 1,000 synthetic apple reviews, so you do not need your own data yet. The method is COAT-MB, which uses statistical feedback to seek a set of variables jointly sufficient for information about the target, called a Markov blanket.

This guide uses DeepSeek Flash to propose factors and hosted Jev for annotation and definition checks, so no local GPU is needed. Prepare an API key for each service before execution. To use local Kev, follow [local deployment](<kev.md>) and connect it as the decision model.

## 1. Prepare the example

Follow [installation](<installation.md>) to create a Python environment and prepare the example files. Run the commands below from `coat-example`. These workspace commands require a package built from a revision that includes the workspace interface.

The [MB configuration](<https://github.com/causalcoat/COAT-Learn/tree/main/config/mb.toml>) uses `Score` as the target and `Review` as the text. It allows five rounds and uses Fisher-Z conditional-independence tests at significance threshold 0.001.

## 2. Save connections

Save DeepSeek for factor proposal and Jev for annotation, definition review and deduplication. Connections store credential variable names; `--replace` updates an existing connection with the same name.

```bash
coatlearn setup connection main --backend openai --provider deepseek --model deepseek-flash --address https://api.deepseek.com --api-key-env DEEPSEEK_API_KEY --replace
coatlearn setup connection decision --backend jev --model jev-1.14.0 --address https://api.typesafe.ai --api-key-env TYPESAFE_API_KEY --replace
coatlearn setup prepare --method mb --directory . --decision-kind model
```

Preparation copies or downloads the example configuration, data and license, and reuses existing files.

## 3. Prepare credentials

Store the keys issued by DeepSeek and TypeSafe in the shell environment variables `DEEPSEEK_API_KEY` and `TYPESAFE_API_KEY`. Enter the keys with these commands:

```bash
read -rsp 'DeepSeek API key: ' DEEPSEEK_API_KEY; printf '\n'
export DEEPSEEK_API_KEY
read -rsp 'TypeSafe API key: ' TYPESAFE_API_KEY; printf '\n'
export TYPESAFE_API_KEY
```

The variables apply to this shell and programs it starts. You can also select a dotenv file explicitly; see [credentials](<models.md#credentials>).

## 4. Run discovery

Run the MB analysis:

```bash
coatlearn run mb --config config/mb.toml --main-connection main --decision-kind model --decision-connection decision --output runs/apple-mb --execute
```

COAT sends selected review examples to the main model for factor proposal, assigns values across reviews, updates the selected set using statistical tests and constructs feedback for the next round. Each round's results and selection records are saved in the run directory.

Output is saved in the new directory you specified. Choose another directory for another run, or omit `--output` to create a unique directory under `runs/`.

## 5. Read the result

Load the saved result. Inspect execution status, then selected variables and their definitions:

```python
import json
from pathlib import Path

result = json.loads(Path("runs/apple-mb/result.json").read_text(encoding="utf-8"))
print(result["status"])
for name in result["diagnostics"].get("final_blanket", []):
    print(name, result["factors"].get(name))
```

`final_blanket` includes the target `Score`. Other names are factors selected in this run; their definitions in `factors` explain value assignment. An existing target may have no written definition.

The same directory contains `config.resolved.json` with the actual models and parameters and `input_mapping.json` with selected columns and input mappings. Round records and factor measurement files help trace the process and can contain original reviews. Keep them private with the result. See [result reference](<results.md>) for field meanings.

## What to do next

To investigate structure between `Taste` and `Score`, inspect the [PAG example configuration](<https://github.com/causalcoat/COAT-Learn/tree/main/config/pag.toml>). It uses the same reviews, starting from those two measured variables and seeking additional factors to refine graph endpoint information. Use `coatlearn run pag --config config/pag.toml --main-connection main --decision-kind model --decision-connection decision` to inspect it; add `--execute` to run it.

To study an action's effect, inspect the [ADJ example configuration](<https://github.com/causalcoat/COAT-Learn/tree/main/config/adj.toml>). It uses a separate synthetic customer dataset to study email sending and visits, with [research assumptions](<configuration.md#research-assumptions>) that need interpretation. For your own data, set these assumptions according to your research design.

For your own analysis, first read [data requirements](<data.md>), then choose a [discovery interface](<discovery.md>) for your question. With attribute definitions already chosen, start with [standalone annotation](<annotation.md>).
