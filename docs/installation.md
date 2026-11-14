<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# Install and prepare an analysis

Install the Python package first, then prepare a working directory for your data and task configuration. Installing coatlearn does not download model weights, start a server or send data to a model.

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

```bash
python -m pip install coatlearn
python -m coatlearn --help
```

`python -m pip` ensures installation uses the selected Python. The package provides both Python interfaces and a `coatlearn` command. `python -m coatlearn` invokes the same command through that interpreter.

You can view the installed release without calling a model:

```bash
python -m pip show coatlearn
```

A standard installation supports hosted chat models, hosted Jev and connections to an already running local Kev server. It does not require a local GPU. Most users do not need additional dependencies.

| Additional task | Installation | Next step |
| --- | --- | --- |
| Use LiNGAM instead of the usual graph procedure | `python -m pip install "coatlearn[lingam]"` | Explicitly select the corresponding analysis option. |
| Load and serve Kev weights on your own GPU | `python -m pip install "coatlearn[kev]"` | Follow the [separate GPU environment and deployment guide](<kev.md>), including upstream Kev installation. |

For a later update, use `python -m pip install --upgrade coatlearn`. To modify the library itself, use the separate [contributor setup](<https://github.com/causalcoat/COAT-Learn/tree/main/CONTRIBUTING.md>); source installation is not needed for analysis.

## 3. Prepare the example working directory

The installed package contains the library and CLI. It does not place example data or configuration files in your current directory. Download the three task configurations, two CSV files and their data attribution into a new `coat-example` directory. You do not need Git or a repository clone.

Run this Python code once, for example by saving it as `prepare_example.py` and running `python prepare_example.py`, or in a notebook cell. It downloads public files from the project's GitHub repository; it does not execute downloaded code or call a model.

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

Use a new directory name if `coat-example` already exists. The two CSV files use CC BY 4.0; keep the downloaded data attribution and license when sharing them.

In the terminal, enter the directory that was just created:

```bash
cd coat-example
python -m coatlearn mb --config config/mb.toml --decision-model jev
```

This reads local data and configuration. It reports 1,000 rows and makes no model calls. The working directory now contains:

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

The example files define hosted DeepSeek Flash for factor proposal and several decision-model connections. `--decision-model jev` selects hosted Jev for annotation, definition review and deduplication; no local model server is needed. The default decision connection is local Kev-9B, which requires a running server.

For hosted execution, prepare `DEEPSEEK_API_KEY` and `TYPESAFE_API_KEY` using the [model connection guide](<models.md#credentials>). Keep actual keys in environment variables or a private dotenv file, not in TOML. The CLI reads an explicitly selected dotenv file only when executing with `--run`.

Continue with [your first analysis](<quickstart.md>) to connect those models, run MB and read its result. Adding `--run` sends the selected texts to the configured services and may incur charges; installation and local inspection do not.
