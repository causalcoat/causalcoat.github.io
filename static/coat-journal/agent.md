# Use coatlearn with an agent

For analysis requests, load the public [coatlearn skill](skill/SKILL.md) and keep its references directory alongside it. The skill is copied from the package source when this site is built.

Use the [current documentation](../../docs/) to select annotation, MB, PAG or ADJ, configure models and interpret results. Read [api.json](api.json) for a compact interface inventory, not an execution service.

Before model execution, agree on the data columns, mappings, model endpoints, assumptions and output directory. Explain where text will be sent and obtain permission for that plan. Local CLI inspection without `--run` does not call models. Keep keys in named environment variables or an explicitly selected private dotenv file.

Report factor values separately from confidence and missingness. Interpret graphs and adjustment sets relative to their assumptions. A completed run does not establish causal correctness; no estimate is not a zero effect. Use per-set records for effect estimates and identify researcher-supplied priors, exemptions or graph-processing hypotheses.

The website is static. It neither receives datasets nor runs models. Software is licensed under Apache-2.0; the two example CSV files use CC BY 4.0. See the source repository for attribution and license terms.
