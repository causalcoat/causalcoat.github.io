<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# Your first analysis

This analysis produces a set of review attributes that provide information about customer ratings, with a measurement definition for each attribute. We use the supplied 1,000 synthetic apple reviews, so you do not need your own data yet. The method is COAT-MB, which uses statistical feedback to seek a set of variables jointly sufficient for information about the target, called a Markov blanket.

This guide uses DeepSeek Flash to propose factors and hosted Jev for annotation and definition checks, so no local GPU is needed. Execution requires API access to both services, sends text to them and incurs their call charges. To use local Kev, complete [local deployment](<kev.md>) first and omit `--decision-model jev` below.

## 1. Install

Use Python 3.11 or newer. Run all commands on this page from the project directory containing the [project configuration](<https://github.com/causalcoat/COAT-Learn/tree/main/pyproject.toml>):

```bash
git clone https://github.com/causalcoat/COAT-Learn.git
cd COAT-Learn
python3 -m pip install -e .
```

This installs the Python library and command-line tool. It does not start model servers.

## 2. Inspect input and settings

Inspect the task without calling a model:

```bash
bash examples/mb.sh --decision-model jev
```

The summary should report `method` as `mb`, `rows` as 1000, `columns_used` as `Score` and `Review`, and `network_requests` as 0. Credentials have not been checked yet.

In the [MB configuration](<https://github.com/causalcoat/COAT-Learn/tree/main/config/mb.toml>), `Score` is the existing numeric target and `Review` is the review for each observation. Other CSV columns do not enter this analysis. The configuration allows five rounds of proposal, annotation and selection, with Fisher-Z conditional-independence tests at significance threshold 0.001. Factors use the `general` definition format with explicit values and mention conditions.

`--decision-model jev` also selects Jev for definition review and concept deduplication. Review checks whether assignment rules are clear. Deduplication avoids measuring the same attribute repeatedly. Neither decides whether an attribute is a cause.

## 3. Prepare credentials

Store the keys issued by DeepSeek and TypeSafe in the shell environment variables `DEEPSEEK_API_KEY` and `TYPESAFE_API_KEY`. These commands prompt for input without placing the key directly in command history:

```bash
read -rsp 'DeepSeek API key: ' DEEPSEEK_API_KEY; printf '\n'
export DEEPSEEK_API_KEY
read -rsp 'TypeSafe API key: ' TYPESAFE_API_KEY; printf '\n'
export TYPESAFE_API_KEY
```

The variables apply to this shell and programs it starts. You can also select a dotenv file explicitly; see [credentials](<models.md#credentials>).

## 4. Run discovery

After confirming that you permit the example texts to be sent to these services, run:

```bash
bash examples/mb.sh --decision-model jev --run --output-dir runs/apple-mb
```

COAT sends selected review examples to the main model for factor proposal, assigns values across reviews, updates the selected set using statistical tests and constructs feedback for the next round. Names and runtime depend on model responses and discovery. The example does not require a predetermined list of factors.

Output is saved in the new directory you specified. Choose a different directory for another run to retain each analysis's settings and result.

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

`final_blanket` includes the target `Score`. Other names are factors selected in this run; their definitions in `factors` explain value assignment. An existing target may have no written definition. A Markov blanket is an information set, not a list of established direct causes.

The same directory contains `config.resolved.json` with the actual models and parameters and `input_mapping.json` with selected columns and input mappings. Round records and factor measurement files help trace the process and can contain original reviews. Keep them private with the result. See [result reference](<results.md>) for field meanings.

## What to do next

To investigate structure between `Taste` and `Score`, inspect the [PAG example configuration](<https://github.com/causalcoat/COAT-Learn/tree/main/config/pag.toml>). It uses the same reviews, starting from those two measured variables and seeking additional factors to refine graph endpoint information. Run `bash examples/pag.sh --decision-model jev` to inspect it; add `--run` to execute.

To study an action's effect, inspect the [ADJ example configuration](<https://github.com/causalcoat/COAT-Learn/tree/main/config/adj.toml>). It uses a separate synthetic customer dataset to study email sending and visits, with [research assumptions](<configuration.md#research-assumptions>) that need interpretation. Do not copy those assumptions directly to your own data.

For your own analysis, first read [data requirements](<data.md>), then choose a [discovery interface](<discovery.md>) for your question. With attribute definitions already chosen, start with [standalone annotation](<annotation.md>).
