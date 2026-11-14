<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# Discovery interfaces

Use discovery when you do not yet know which attributes to measure. These interfaces start with numeric variables and paired text, combining factor proposal, annotation, statistical selection and feedback. All three accept a local CSV path or pandas DataFrame and return the same result-dictionary structure.

Calls below are organized by research goal. See [understand COAT](<concepts.md>) for concepts and [your first analysis](<quickstart.md>) for a complete run. Replace data paths and column names with your input, and prepare models using [connection setup](<models.md>).

## MB: seek information about one target

`run_mb` takes an existing numeric target and a text column. It seeks a Markov blanket: a set that makes the remaining candidates provide no additional target information once that set is given.

```python
from coatlearn import RunConfig, run_mb
from coatlearn.models.presets import dpsk41f, jev

result = run_mb(
    "reviews.csv", target="score", text_col="text",
    main_model=dpsk41f, annotation_model=jev,
    config=RunConfig(
        rounds=1, test_method="fisherz", alpha=0.001,
        options={"factor_template": "general"},
    ),
)
blanket = result["diagnostics"]["final_blanket"]
```

`target` names an existing numeric column; `text_col` names the paired, nonempty text column. `main_model` proposes factors and `annotation_model` assigns values to observations. `rounds` controls the number of MB iterations.

The selected set is updated each round. Earlier candidates remain measured in the factor pool but do not stay selected merely because they were selected before. Selected names appear in `diagnostics.final_blanket`, including the target; definitions appear in `factors`.

The default name-overlap comparison path needs a previously installed WordNet corpus; see [local dependencies](<troubleshooting.md>). To retain the supplied example's decision-model deduplication, review and all other settings, load its TOML rather than copying only this minimal call.

## PAG: refine structure with new variables

`run_pag` takes existing numeric variables without requiring an initial graph. It starts with their blanket searches, adds factors where they can help refine structure and uses causal-learn's FCI algorithm to learn a partial ancestral graph.

```python
from coatlearn import RunConfig, run_pag
from coatlearn.models.presets import dpsk41f, jev

result = run_pag(
    "reviews.csv", known_variables=["taste", "score"], text_col="text",
    main_model=dpsk41f, annotation_model=jev,
    config=RunConfig(
        rounds=2, test_method="fisherz", alpha=0.001,
        options={"factor_template": "general", "fci_depth": 2},
    ),
)
graph = result["graph"]
```

`known_variables` names existing measured columns, not known causal directions. `graph` holds node order and an endpoint matrix. Circle endpoints retain structural uncertainty; not every edge is an established direct causal relationship.

`rounds` limits consecutive MB iterations per target and outer extension batches. `fci_depth` limits conditioning depth in FCI graph search, not every MB test's conditioning-set size.

## ADJ: seek adjustment variables for a specified effect

`run_adj` takes an existing treatment, outcome and paired text. It combines their blanket searches, extends relevant paths and possible descendants, refines a PAG, then applies the generalized adjustment criterion and computes effects.

```python
from coatlearn import RunConfig, run_adj
from coatlearn.models.presets import dpsk41f, jev

result = run_adj(
    "customers.csv", treatment="sent", outcome="visited", text_col="post",
    main_model=dpsk41f, annotation_model=jev,
    config=RunConfig(
        rounds=2, test_method="mv_fisherz", alpha=0.001,
        options={"factor_template": "general"},
    ),
)
print(result["adjustment_sets"])
print(result["estimates"])
```

For direct Python calls, treatment must already be encoded as 0 and 1; outcome must be numeric. TOML can explicitly declare conversions from original labels. The method seeks sets valid under the current graph and assumptions, not a guaranteed effect number for every input.

Effect computation uses complete-case inverse probability weighting, selecting usable rows separately for each adjustment set. The supplied ADJ configuration also has factor-support, prediction-screening, coverage and researcher-prior settings. Those exact thresholds and policies do not apply to every `run_adj` call.

## Run a complete example configuration from Python

TOML lets Python and the CLI share data, model roles and analysis settings:

```python
from coatlearn.configuration import load_task
from coatlearn.execution import check_task, execute_task

plan = load_task("config/pag.toml", decision_model="jev")
checked = check_task(plan)
print(checked.summary["columns_used"])
# Execute after preparing credentials and confirming the run:
result, directory = execute_task(checked, output_dir="runs/python-pag")
```

`load_task` reads settings, `check_task` checks local input only, and `execute_task` runs discovery. Constructing `RunConfig` directly does not load example TOML settings. See [configuration reference](<configuration.md>) for fields.

## How missing measurements enter statistics

The `general` definition separates mention from attribute value, preserving unmentioned measurements as missing in the annotation table. Statistical input then depends on the method: `mv_fisherz` retains missing values for its conditional-independence calculation; current Fisher-Z and other paths without that missing-value treatment fill missing statistical inputs with zero. Effect estimation selects complete observations separately for each adjustment set.

These steps have different meanings. A saved missing value is not a measured zero, and filling statistical input with zero is an explicit analysis policy. Interpret it in light of your measurement scale when choosing a method. See [result reference](<results.md>) for outputs and their associated assumptions.
