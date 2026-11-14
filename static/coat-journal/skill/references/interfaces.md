# Public interface reference

Use these entry points for analysis. The Python package requires Python 3.11 or newer.

## Discovery

```python
from coatlearn import ModelConfig, RunConfig, run_mb, run_pag, run_adj
from coatlearn.models.presets import dpsk41f, jev, kev9b, kev4b
```

`run_mb(data, target, text_col=..., main_model=..., annotation_model=..., config=...)` uses a numeric target and text. `run_pag(data, known_variables, ...)` starts from named numeric variables. `run_adj(data, treatment, outcome, ...)` expects an explicitly coded 0/1 treatment. Data is a local CSV path or pandas DataFrame. Only named columns enter discovery.

All three return `method`, `status`, `factors`, `graph`, `adjustment_sets`, `estimates`, `diagnostics` and `provenance`. Read MB names from `diagnostics.final_blanket`; graph rows follow `graph.node_order`; ADJ estimates and their sets are associated in `estimates.per_set`.

## Task configuration and execution

```python
from coatlearn.configuration import load_task
from coatlearn.execution import check_task, execute_task

plan = load_task("task.toml", decision_model="jev")
checked = check_task(plan)
# Only after execution permission and required environment variables:
result, output = execute_task(checked, output_dir="runs/chosen-name")
```

A TOML task uses `task`, `models`, `roles` and `analysis` sections. Paths inside it are config-relative. `decision_model` selects a model defined in that file for annotation and any enabled judge/dedup roles; it does not alter statistical settings.

```bash
python -m coatlearn mb --config task.toml
python -m coatlearn mb --config task.toml --run --output-dir runs/chosen-name
```

The same commands exist for `pag` and `adj`. `--env-file` is explicit and only used with `--run`. The CLI does not require a repository checkout when the user supplies their own task and data.

## Fixed-definition annotation

```python
from coatlearn.annotation import annotate, factor_definition_to_spec
from coatlearn.annotation import review_definition, compare_definitions
```

`annotate(texts, definitions, model=...)` measures a mapping of names to definitions. It returns `values`, `metadata` and `specs`. It does not perform automatic review, duplicate comparison or discovery. `factor_definition_to_spec` is local. The other calls use a chosen Jev/Kev decision model and require model-call authorization.

## Fixed-data causal processing

```python
from coatlearn.causality import CausalGraph, learn_graph
from coatlearn.causality import find_adjustment_sets, estimate_effects, independence_test
```

These functions use measured numeric variables and do not call language models. `CausalGraph.from_result(result)` reads a saved discovery graph. Named treatment and outcome arguments avoid manual matrix indices. Effects use the existing IPW method; no DoWhy or EconML backend is added.
