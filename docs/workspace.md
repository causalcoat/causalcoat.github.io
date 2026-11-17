<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# Set up and run a workspace

A workspace saves named model connections for reuse across analyses. First [install the package and prepare the example files](<installation.md>). Run the commands below from the example working directory with a package built from a revision that includes the workspace interface.

## Use the terminal guides

Run `coatlearn setup` to choose a model source and save a connection. Repeat it for the main model and the annotation model. Run `coatlearn run` to choose a method, data columns and connections. The run guide checks the plan first and asks before executing it.

The main model is an LLM that proposes factors. Annotation can use an LLM, hosted Jev, or a local or existing Kev service. Jev connects to an existing hosted service. To install and start a local Kev service, see [Deploy local Kev](<kev.md>); `coatlearn setup local prepare` needs `--execute` to install dependencies and download weights, and `coatlearn setup local start` runs in the foreground.

## Use commands without prompts

Save DeepSeek as the main connection and Jev as the decision connection, prepare the example, then inspect the analysis plan:

```bash
coatlearn setup connection main --backend openai --provider deepseek --model deepseek-flash --address https://api.deepseek.com --api-key-env DEEPSEEK_API_KEY --replace
coatlearn setup connection decision --backend jev --model jev-1.14.0 --address https://api.typesafe.ai --api-key-env TYPESAFE_API_KEY --replace
coatlearn setup prepare --method mb --directory . --decision-kind model
coatlearn run mb --config config/mb.toml --main-connection main --decision-kind model --decision-connection decision
```

The preparation command downloads or copies the example files before the first run and reuses existing files on later runs. `--replace` saves connection updates when a name already exists. The last command checks the plan without model calls. Add `--execute` to run it. For PAG or ADJ, use `coatlearn run pag` or `coatlearn run adj` with the matching configuration. `--data`, `--text-col`, task columns, `--rounds`, `--concurrency` and `--output` override configuration values. Use repeated `--known-variable` options for PAG. `--connections` selects a different connection file. Run `coatlearn run --help` for all options. The [homepage planner](https://causalcoat.github.io/#use) generates commands for your choices; its button only copies them.

Without an explicit output directory, each execution creates a unique directory under `runs/`, named for the method. Set `--output` only when you want a specific directory.

In Python, prepare resources and use the same named connections:

```python
from coatlearn.preparation import prepare_resources
from coatlearn.workspace import run_task

prepare_resources(method="mb", decision_kind="model")
result = run_task("mb", config="config/mb.toml", main_connection="main",
                  decision_kind="model", decision_connection="decision", execute=True)
```

Omit `execute=True` to check without executing. PAG's `known_variables` override is a list of column names.

## Set credentials

Connections store environment variable names, not keys. Set the variables in the terminal before execution. DeepSeek uses `DEEPSEEK_API_KEY`; Jev uses `TYPESAFE_API_KEY`. The chosen connection can specify another variable name. A vLLM connection also requires a nonempty `VLLM_API_KEY` by default; use the value configured for your server, including a placeholder if your server accepts one.

You may explicitly select a private dotenv file with `--env-file` or `run_task(..., env_file=".env")`. Do not upload `.env` files or logs: they can contain credentials or private data. See [model credentials](<models.md#credentials>) for more detail.
