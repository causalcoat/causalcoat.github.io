<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# Analyze tables and fixed graphs

With measured values already available, perform statistical causal analysis without more language-model calls. For example, after annotating customer attributes, you may want adjustment sets under an explicit graph. Or you may have a numeric table and only want to learn its graph.

This page uses customer attribute `V`, email sending `T` and website visit `Y` to explain the interfaces. See [adjustment sets and effects](<concepts.md#why-effect-estimation-needs-adjustment-sets>) for background. The illustrative graph is a declared structure, not a discovery result from the supplied CSV.

## Declare a fixed graph

Start with a simple chain `V -> T -> Y`: the customer attribute affects email sending, which affects visits. This assumed graph includes no separate `V` to `Y` path. The purpose here is to pass an explicit structure to the interface.

Use `CausalGraph` to keep node-name order together with an endpoint matrix:

```python
from coatlearn.causality import CausalGraph, find_adjustment_sets

graph = CausalGraph(
    node_order=("V", "T", "Y"),
    endpoint_matrix=[
        [0, -1, 0],
        [1, 0, -1],
        [0, 1, 0],
    ],
)
adjustment = find_adjustment_sets(graph, treatment="T", outcome="Y")
print(adjustment["adjustment_sets"])
```

Entry `[i, j]` records the edge mark at node `i`: `-1` is a tail, `1` an arrowhead, `2` an unresolved circle and `0` no edge. Thus `V -> T` has `-1` at `V` and `1` at `T`. See [endpoint reference](<results.md#graph-endpoint-marks>) for more detail.

`find_adjustment_sets` applies the generalized adjustment criterion and returns sets plus diagnostics for its graph requirements. Direction information alone does not rule out latent confounding, so use the criterion's actual judgment on the input graph.

An empty adjustment set `[]` means no covariates need adjustment under the graph conditions. In `adjustment_sets`, `[[]]` contains an empty set, whereas `[]` means no valid set was found. These are different results.

## Read an existing discovery graph

Loading a graph from a saved PAG or ADJ result neither calls models nor reruns discovery:

```python
import json
from pathlib import Path
from coatlearn.causality import CausalGraph

result = json.loads(Path("runs/apple-pag/result.json").read_text(encoding="utf-8"))
saved_graph = CausalGraph.from_result(result)
```

A graph can also come from another discovery method or domain assumptions if converted to the same node and endpoint representation. Later conclusions are conditional on the input graph. “Existing” or “fixed” does not mean established as the real system's structure.

## Estimate effects from a measured table

Prepare a pandas DataFrame containing the graph variables, then call `estimate_effects`. This shows the data-loading and call pattern; substitute your measurement table and matching graph:

```python
import pandas as pd
from coatlearn.causality import estimate_effects

measured_data = pd.read_csv("measurements.csv")
estimates = estimate_effects(
    measured_data, graph,
    treatment="T", outcome="Y",
)
print(estimates["diagnostics"].get("primary_adjustment_summary"))
```

Treatment `T` uses 0/1 and outcome `Y` is numeric. The interface checks graph adjustment sets, then uses complete-case IPW for each set. IPW weights observations by their estimated treatment probabilities. Without a suitable set, it does not automatically treat an unadjusted difference as an effect.

`primary_adjustment_summary` records the selected set, estimate and sample information. Set-specific records appear in `diagnostics.sets`. A binary outcome's average treatment effect is a probability difference: 0.03 means three percentage points. Causal interpretation depends on the input graph, measurements and estimation assumptions.

## Learn a graph from numeric columns

With measurements but no graph, use `learn_graph` to run FCI on selected columns. It proposes no factors and does not annotate source material again:

```python
from coatlearn.causality import learn_graph, independence_test

graph = learn_graph(measured_data, columns=["V", "T", "Y"], depth=2)
p_value = independence_test(measured_data, "T", "Y", given=["V"], method="fisherz")
print(graph.to_dict())
print(p_value)
```

`independence_test` returns a conditional-independence p-value, not the probability that a causal relationship is true. `given=["V"]` asks whether `T` and `Y` remain related after considering `V`. To discover missing variables in paired text as well, use [discovery](<discovery.md>).
