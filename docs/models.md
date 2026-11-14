<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# Connect models

Before running discovery, connect coatlearn to a model that proposes factors and a model that assigns values to individual observations. These jobs can use different services. Installing the Python package neither downloads weights nor starts a model.

## Distinguish models from serving software

A **chat model** generates factor names, definitions and revisions from prompts. A **decision model** answers yes/no, classification or rating questions under written rules. It supports annotation, definition review and concept deduplication. Neither role directly certifies causal relationships.

| Name | What it is | How this project uses it |
| --- | --- | --- |
| DeepSeek Flash | A hosted chat model | The supplied configurations use it to propose and revise factors. Requires `DEEPSEEK_API_KEY`. |
| Jev | A hosted decision model from TypeSafe | No local weights to deploy. Call it with `TYPESAFE_API_KEY`. |
| Kev | An independent decision model you can run yourself, with a request format compatible with Jev's System One | Start it in another process and connect over local HTTP. See [deployment](<kev.md>). |
| vLLM | Inference software for serving language models | Can provide a local chat model through an OpenAI-compatible API. It is not a model name or the way this project starts Kev. |

**OpenAI-compatible** means the service accepts requests compatible with OpenAI's chat API, not that requests necessarily go to OpenAI. Jev and Kev use a different interface: `POST /v1/systemone`. This package calls that official request format directly over HTTP without the TypeSafe SDK. See the [TypeSafe API](https://docs.typesafe.ai/api).

## Connect hosted models

For a first run, use existing presets without entering a model version. A **preset** is a named connection configuration containing a model identifier, address and credential-variable name. It is not a running model.

From the `coat-example` directory prepared in the [installation guide](<installation.md>), prepare `DEEPSEEK_API_KEY` and `TYPESAFE_API_KEY` in your shell, then switch the example's three decision roles to Jev:

```bash
python -m coatlearn mb --config config/mb.toml --decision-model jev
# Execute after confirming the configuration and where text will be sent:
python -m coatlearn mb --config config/mb.toml --decision-model jev --run --output-dir runs/apple-jev
```

For a direct Jev call from Python, use the preset's configuration. This sends the example text below to TypeSafe:

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

System One calls the content to analyze `state` and the questions to answer `questions`. `noul` returns the probability of yes; `choice` selects a category; `score` returns probabilities over ordered levels. To assign values in batches using factor definitions, use [annotation](<annotation.md>) without constructing these questions yourself.

## Use presets and model identifiers

Presets hold identifiers that match the project's examples. Import them directly:

| Preset | Saved model identifier | Address | Credential variable |
| --- | --- | --- | --- |
| `dpsk41f` | `deepseek-flash` | `https://api.deepseek.com` | `DEEPSEEK_API_KEY` |
| `jev` | `jev-1.14.0` | `https://api.typesafe.ai` | `TYPESAFE_API_KEY` |
| `kev9b` | `kev-9b-v1.0` | `http://127.0.0.1:8019` | none |
| `kev4b` | `kev-4b-v1.0` | `http://127.0.0.1:8014` | none |

A model identifier tells the service which model a request should use. It is not a coatlearn version you must maintain. With a preset, you do not repeat it. When connecting another service or serving your own weights, set `model` to an identifier the service accepts. Results record it to trace which model was used. `deepseek-flash` is a provider-managed alias, not a fixed local weight snapshot.

Customize a preset to produce an independent configuration, for example to reduce main-model concurrency or change a local Kev port:

```python
from coatlearn.models.presets import dpsk41f, kev9b

main = dpsk41f(max_concurrency=3, env_file=None)
annotation = kev9b(base_url="http://127.0.0.1:8020")
```

8020 is a user-chosen example port and must match the server's startup port. 8019 and 8014 are also project conventions, not fixed Kev ports. Changing a configuration neither starts nor moves a server. `127.0.0.1` means the machine running the client. The package's Kev client uses loopback HTTP and reads no provider credentials.

Python presets can read the required key from `.env` in the working directory by default. Set `env_file=None` to disable that. Each execution creates an independent client with separate measurement caches and counters.

## Connect another chat service

Use `ModelConfig` for the model identifier, chat API address and credential-variable name supplied by your service. This creates a connection description without sending a request:

```python
from coatlearn.models import ModelConfig

main = ModelConfig(
    model="your-served-model",
    base_url="https://your-provider.example/v1",
    api_key_env="MY_MODEL_API_KEY",
)
```

Pass `main` as `main_model` to `run_mb`, `run_pag` or `run_adj`. Replace the address and identifier with real service values; keep the key value in the environment.

### Connect vLLM

An existing vLLM chat deployment uses the same interface. vLLM loads weights in a separate terminal; coatlearn requests it over HTTP. The following is the startup form. Replace `/path/to/chat-model` with a supported chat-model path:

```bash
vllm serve /path/to/chat-model \
  --served-model-name coat-chat --host 127.0.0.1 --port 8001
```

Set `VLLM_API_KEY` in the terminal running coatlearn. If server authentication is disabled, this client still requires a nonempty placeholder such as `local`. With authentication enabled, use the matching key. Match the connection to the startup arguments:

```python
from coatlearn.models import ModelConfig

main = ModelConfig(
    model="coat-chat",
    base_url="http://127.0.0.1:8001/v1",
    api_key_env="VLLM_API_KEY",
)
```

`coat-chat` matches `--served-model-name`, 8001 matches `--port`, and `/v1` is the chat API prefix. See [vLLM documentation](https://docs.vllm.ai/en/latest/serving/online_serving/openai_compatible_server/) for installation, hardware and supported models. This package neither loads vLLM weights in the analysis process nor manages its GPU process.

## Credentials

Provide keys through environment variables, not TOML, Python source or results. For example, `api_key_env="TYPESAFE_API_KEY"` stores the variable name; execution reads its value.

The CLI uses exported variables by default. You can instead explicitly select a private dotenv file:

```bash
python -m coatlearn mb --config config/mb.toml --decision-model jev --env-file .env --run --output-dir runs/apple-env
```

A dotenv file is a local text file with `NAME=value` entries. The CLI reads the selected file only with `--run`, after local data checks, and loads only keys required for that execution. It does not search parent directories. Existing process values take precedence.

Explicit Python configurations (`ModelConfig`, `JevConfig`) read environment variables only; presets also support their selected dotenv file. A hosted main model receives proposal examples; a hosted annotator receives the texts to measure. Local Kev keeps decision requests local but does not automatically make a hosted main model local too.
