<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# Install and prepare an analysis

Install coatlearn and prepare a working directory for the example analysis.

## 1. Create a Python environment

Use Python 3.11 or newer. A virtual environment keeps this analysis's packages separate from other projects. In a terminal on macOS or Linux:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, use PowerShell:

```powershell
py -3 --version
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

After activation, `python` and `pip` refer to this environment. Use the same environment when installing the package and running an analysis. In a notebook, select this environment as the notebook kernel.

## 2. Install from PyPI

Install the package in the active environment and open its command help:

```bash
python -m pip install coatlearn
python -m coatlearn --help
```

`python -m pip` ensures installation uses the selected Python. The package provides both Python interfaces and a `coatlearn` command. `python -m coatlearn` invokes the same command through that interpreter.

You can view the installed release without calling a model:

```bash
python -m pip show coatlearn
```

The published PyPI package may precede the workspace commands below. Use a package built from a revision that includes `coatlearn setup prepare` for this guide.

A standard installation supports hosted chat models, hosted Jev and connections to an already running local Kev server. It does not require a local GPU. Most users do not need additional dependencies.

| Additional task | Installation | Next step |
| --- | --- | --- |
| Use LiNGAM instead of the usual graph procedure | `python -m pip install "coatlearn[lingam]"` | Explicitly select the corresponding analysis option. |
| Load and serve Kev weights on your own GPU | `python -m pip install "coatlearn[kev]"` | Follow the [separate GPU environment and deployment guide](<kev.md>), including upstream Kev installation. |

For a later update, use `python -m pip install --upgrade coatlearn`. To modify the library itself, use the separate [contributor setup](<https://github.com/causalcoat/COAT-Learn/tree/main/CONTRIBUTING.md>); source installation is not needed for analysis.

## 3. Prepare the example working directory

Create and enter a working directory, then prepare the example files explicitly:

```bash
mkdir -p coat-example
cd coat-example
coatlearn setup prepare --method all --directory . --decision-kind llm
```

Choose `mb`, `pag`, or `adj` instead of `all` to prepare one example. The command downloads or copies the example configuration and data, including their attribution and license. Existing files are reused. Keep the attribution and license when sharing the data.

LLM annotation also needs the WordNet dictionary. The command downloads it by default for `--decision-kind llm`; `--decision-kind model` does not download it by default. Use `--wordnet` or `--no-wordnet` to choose explicitly. With your own data, use `--method none --decision-kind llm` to prepare WordNet without example files. Preparing resources does not call a model. Run the command again when needed; existing resources are reused.

## 4. Understand the configuration

A **task configuration** is a TOML text file describing the data, model connections and analysis settings. It is separate from Python installation and from model credentials. You choose it explicitly with `--config`.

Start with the closest downloaded task. MB asks about one target, PAG starts with measured variables, and ADJ asks about a specified treatment and outcome. Keep the example unchanged for the first tutorial. For your own data, copy a task to a new file and edit its `[task]` section, for example:

```toml
[task]
method = "mb"
data = "../data/my_reviews.csv"
target = "rating"
text_col = "review"
```

This is one section, not a complete configuration. Retain the model and analysis sections from your copied file. `data` resolves relative to the configuration file: a task under `config/` reaches a file under `data/` through `../data/`. Keep column names consistent with the CSV. See [data preparation](<data.md>) and the [configuration reference](<configuration.md>) for mappings, model roles and statistical settings.

## 5. Connect models before execution

The example files define hosted DeepSeek Flash for factor proposal and several decision-model connections. A named Jev connection selects hosted Jev for annotation, definition review and deduplication; no local model server is needed. The default decision connection is local Kev-9B, which requires a running server.

For hosted execution, prepare `DEEPSEEK_API_KEY` and `TYPESAFE_API_KEY` using the [model connection guide](<models.md#credentials>). Keep actual keys in environment variables or a private dotenv file, not in TOML. The CLI reads an explicitly selected dotenv file during execution.

Continue with [your first analysis](<quickstart.md>) to connect those models, run MB and read its result. Executing the analysis sends the selected texts to the configured services and may incur charges; installation and local inspection do not.
