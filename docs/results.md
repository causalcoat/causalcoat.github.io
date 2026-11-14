<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# Result reference

First distinguish a variable set, a graph and an estimate of a specified effect. MB primarily reports selected factors, PAG reports a graph, and ADJ also reports adjustment sets and set-specific estimates. Execution status describes the process, not the interpretation of these results.

## Top-level fields

The three discovery functions return JSON-serializable dictionaries with the same eight fields. Fields without applicable content can be `None`; graph availability is also recorded in `graph.available`.

| Field | Contents | What to inspect first |
| --- | --- | --- |
| `method` | `mb`, `pag` or `adj` | The method actually run. |
| `status` | Execution state | Recorded call or processing errors. |
| `factors` | Names mapped to available definitions | Factor meanings and assignment rules. |
| `graph` | Availability, node order and endpoint matrix | PAG/ADJ structural information. |
| `adjustment_sets` | ADJ's variable sets | Sets considered for adjustment. |
| `estimates` | ADJ estimates, set-specific records and criterion information | The set actually used and its assumptions. |
| `diagnostics` | Selection history and process records | How the set was updated. |
| `provenance` | Data columns, models, parameters and supplied assumptions | The basis of this analysis. |

## Selected factors

For MB, `diagnostics.final_blanket` contains selected names, including the target. `factors` maps them to available written definitions; an existing numeric target may have none. This set summarizes target information, not established direct causes.

For PAG and ADJ, `graph.node_order` lists graph variables. ADJ's `factors` primarily describes newly discovered factors and need not match the complete node list containing treatment and outcome.

## Graph endpoint marks

`graph.node_order` determines row and column order in `graph.endpoint_matrix`. Entry `[i, j]` records the mark at node `i`, not a conventional adjacency code meaning “from i to j.”

| Code | Endpoint | Meaning |
| --- | --- | --- |
| `-1` | Tail | Retains tail information in the represented structures. |
| `1` | Arrowhead | Under graph assumptions, this endpoint is not an ancestor of the other. |
| `2` | Circle | The endpoint is unresolved between tail and arrowhead. |
| `0` | None | No edge between the nodes. |

For example, `i -> j` has `matrix[i][j] == -1` and `matrix[j][i] == 1`. In a PAG, this form expresses that `i` is an ancestor of `j`, not necessarily a direct effect without hidden intermediate nodes. Two arrowheads in `i <-> j` express that neither node is an ancestor of the other, consistent with a latent common cause.

`i o-> j` leaves the `i` endpoint unresolved; `i o-o j` leaves both unresolved. Circles mean structural uncertainty, not a smaller effect or a numeric model-confidence score. A PAG represents a class of candidate structures, not one fully oriented graph.

MB returns a set rather than a graph. Its `graph` normally contains `available=false` and a reason. Check availability before reading a matrix.

## Adjustment sets and effect estimates

Interpret `adjustment_sets` together with `estimates.adjustment_criterion`. Set validity is relative to the input graph and applied criterion. Graph accuracy and additional researcher assumptions still require consideration.

| `adjustment_sets` | Interpretation |
| --- | --- |
| `[["V"]]` | A set containing `V` was found. |
| `[[]]` | An empty set was found; covariate adjustment is unnecessary under the graph conditions. |
| `[]` | The applied criterion found no adjustment set. |
| `None` | Not evaluated or not applicable. |

`estimates.per_set` associates each set with its status, estimate and actual sample information. Read it instead of pairing a list of successful estimates positionally with all adjustment sets. Graph validity and numerical estimability in the available sample are separate judgments.

`estimates.primary_adjustment_summary` describes the selected estimated set, including `adjustment_set`, `estimate`, sample size `n` and retained share `coverage`. `largest_adjustment_summary` describes all graph-valid sets with the most variables; their numerical estimates need not all be available.

Average treatment effects use the outcome's original units. For a 0/1 visit record, 0.03 means three percentage points. Numeric 0 means an estimated zero effect; `None` or an absent estimate does not.

## Supplied assumptions and graph processing

`provenance.run_config` records supplied settings; `provenance.core_effective_config` records settings applied. `provenance.direction_constraints` records researcher-provided directions separately from discovery. Model identifiers and library versions support traceability without requiring users to maintain version numbers manually.

The supplied ADJ example explicitly exempts adjustment amenability. Its rationale and criterion information accompany results. Estimates depend on those additional premises; a listed set alone does not establish full criterion certification. See [research assumptions](<configuration.md#research-assumptions>).

When cycle processing is used, `estimates.graph_postprocessing` records deletion hypotheses and common adjustment sets. `graph` retains the original discovered structure. Estimates are conditional on those additional hypotheses, not confirmation of which original edge should be deleted.

## Execution state

`status` is `completed`, `completed_with_errors` or `failed`. It describes execution visible to the package, not certification that a causal conclusion is correct. For ADJ estimation availability, inspect `estimates.adjustment_status` and set-specific records separately.

## Save and reload

The CLI writes `result.json`, `config.resolved.json` and `input_mapping.json` in the selected directory: result, effective configuration and input mappings. Load them in Python without more model calls:

```python
import json
from pathlib import Path

result = json.loads(Path("runs/apple-mb/result.json").read_text(encoding="utf-8"))
print(result["method"], result["status"])
print(result["factors"])
```

The directory may also contain factor tables, examples and process records. Raw conversations are saved only when enabled. Manage the whole directory under the source data's privacy requirements.

[Standalone annotation](<annotation.md>) returns `AnnotationResult`, not this discovery dictionary. `values` is the measurement table, `metadata` contains probabilities, confidence and mention information, and `specs` contains measurement specifications. [Fixed-graph estimation](<causality.md>) places set-specific records in `diagnostics.sets`.
