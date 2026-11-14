<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# Configuration reference

A task configuration stores data selection, model connections and statistical settings for an analysis. The supplied files use TOML, a text format organized into named sections such as `[task]`. Understand the example settings before copying the closest configuration for your question.

## Configuration sections

| Section | What it stores | When to change it |
| --- | --- | --- |
| `[task]` | Method, data path, column names and explicit encoding mappings | When changing data or question. |
| `[models.<name>]` | Backend, model identifier, address, credential variable and request settings | When changing service, model or port. |
| `[roles]` | Named model assigned to each job | When allocating proposal, annotation, review and deduplication. |
| `[role_options.<role>]` | A few connection overrides for a role | For example, to limit review concurrency separately. |
| `[analysis]` | Rounds, statistical test, significance threshold, seed and related settings | When adjusting the analysis plan. |
| `[analysis.options]` | Factor format, screening and method-specific assumptions | When explicitly choosing an analysis policy. |

Keep the top-level `schema_version = 1`: it declares the file format, not a project release version. Relative `task.data` paths start from the configuration's directory, not the shell working directory.

## Saved example settings

| Setting | [MB](<https://github.com/causalcoat/COAT-Learn/tree/main/config/mb.toml>) | [PAG](<https://github.com/causalcoat/COAT-Learn/tree/main/config/pag.toml>) | [ADJ](<https://github.com/causalcoat/COAT-Learn/tree/main/config/adj.toml>) |
| --- | --- | --- | --- |
| Rows | 1,000 | 1,000, same CSV as MB | 2,000 |
| Numeric columns | `Score` | `Taste`, `Score` | `email_type`, `visit` |
| Text column | `Review` | `Review` | `post` |
| `rounds` | 5 | 2 | 2 |
| `test_method` | `fisherz` | `fisherz` | `mv_fisherz` |
| `alpha` | 0.001 | 0.001 | 0.001 |
| `concurrency` | 32 | 16 | 16 |
| `seed` | 0 | 42 | 42 |
| `fci_depth` | 2 | 2 | 2 |

All three use DeepSeek Flash as main model and default to Kev-9B for annotation, review and deduplication, with Kev-4B and Jev connections also defined. They use `general` factors, enable definition-format repair, combine up to eight factors per text request and use VIF threshold 3 for collinearity filtering. They save factor process records but not raw conversations.

`alpha` is the conditional-independence test's significance threshold, not confidence in a causal conclusion. `fisherz` tests conditional independence through partial correlation under its distributional assumptions; `mv_fisherz` is a missing-value variant. `fci_depth` controls conditioning depth in graph search. See [discovery](<discovery.md>) for method-specific `rounds` meanings.

## Model roles

Define each connection once under `[models.<name>]`, then reference it from `[roles]`. Names are labels within the configuration; the actual service model identifier is the connection's `model` field.

```toml
[roles]
main = "main"
annotation = "kev9b"
judge = "kev9b"
dedup = "kev9b"
```

`main` proposes and revises factors, `annotation` measures them, `judge` checks clarity and format, and `dedup` compares core attributes. The last two are enabled in the supplied files, not automatic parts of every annotation call.

Switch all three enabled decision roles together without changing the proposer or statistical parameters:

```bash
bash examples/pag.sh --decision-model kev4b
bash examples/pag.sh --decision-model jev
```

These commands only display configuration; add `--run` to execute. Kev requires a matching local server; see [deployment](<kev.md>). The supplied main model uses `omit_temperature = true` to omit temperature from requests. Review and deduplication each have concurrency limited to three; deduplication also receives the task context for comparing definitions.

## Python parameters

`RunConfig` is the Python form of shared analysis parameters. Direct calls do not load TOML automatically, so Python defaults can differ from the example settings above.

| Field | Python default | Purpose |
| --- | --- | --- |
| `rounds` | 1 | Iterations or iteration cap, depending on method. |
| `concurrency` | 16 | Annotation worker threads. |
| `alpha` | 0.01 | Conditional-independence significance threshold. |
| `test_method` | `kci` | Test name passed to causal-learn. |
| `seed` | 0 | NumPy random seed. |
| `output_dir` | `None` | Process output location; otherwise chosen and recorded by the method. |
| `save_conversations` | `False` | Whether to save raw prompts and responses. |
| `options` | Empty mapping | Method-specific settings. |

Common `options` include `factor_template="general"`, which declares scales, values and mention rules. `vif_threshold` filters candidates too collinear with other variables. VIF, the variance inflation factor, measures how much a variable is linearly explained by the others. `annotation_batching` controls combining factors in requests for the same text.

## ADJ example screening and estimation

The ADJ example requires enough nonmissing candidate measurements in both treatment groups: mention rate at least 0.05 and count at least 50 per group. It also excludes a candidate if its single-factor five-fold prediction accuracy for treatment or outcome reaches 0.9. This is an explicit experimental screening policy, not a general claim that better prediction makes a variable less useful.

Each adjustment set selects complete observations separately and requires retention of at least 0.85. `cell_coverage_min=0.995` requires usable rows to cover at least that share of declared value combinations. Ordered soft scores are mapped to their nearest declared levels for this calculation. It describes combination coverage, not model accuracy or independent proof of treatment-probability overlap.

Among successfully estimated sets, selection favors more variables, then a wider treatment-probability range for ties. This policy is `size_then_propensity_range`. Summaries of graph-largest sets and the selected estimated set are stored separately; more variables do not guarantee lower estimation error.

## Research assumptions

The ADJ example sets `assume_treatment_causes_outcome=true`, supplying the treatment-to-outcome direction as known, and `assume_factors_precede_treatment=true`, supplying temporal order. These come from the study design, not directions discovered from posts in this run.

**Adjustment amenability** is a PAG requirement in the generalized adjustment criterion. It rules out unresolved latent confounding on the first edge of possibly causal paths. The synthetic ADJ configuration explicitly exempts it with `amenability_exempt=true`, recording its data-generation rationale. Results then depend on researcher assumptions and must not be called complete criterion certification on the original PAG.

`break_cycles=true` allows edge-deletion hypotheses when the final graph violates ancestral-graph conditions. It enumerates minimum-deletion alternatives, protects the known treatment edge and estimates only adjustment sets common to all alternatives. The original discovered graph is retained. Deletion does not establish from data which edge is wrong. The library default does not enable this option.

These settings belong to the authors' specific synthetic study. For new data, state your own premises rather than copying exemptions or deletion policies merely to obtain an effect number. Supplied assumptions, graph processing and estimation records are stored separately in [results](<results.md>).

## Command-line overrides

The CLI reads the same task as Python. Without `--run`, it only displays local configuration and data summaries:

```bash
coatlearn adj --config config/adj.toml
python3 -m coatlearn adj --config config/adj.toml
```

| Option | Purpose |
| --- | --- |
| `--config` | Select a task configuration. |
| `--data` | Override the data file for this run. |
| `--decision-model` | Switch enabled decision roles by a configured name. |
| `--output-dir` | Choose a new output directory. |
| `--env-file` | Read a selected private credential file during execution. |
| `--run` | Explicitly execute model calls and analysis. |

Example scripts are thin wrappers around the corresponding CLI commands and accept the same overrides. See `python3 -m coatlearn adj --help` for all options.
