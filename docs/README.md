<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# coatlearn documentation

coatlearn helps you discover and measure useful factors in unstructured data, then analyze causal structure and intervention effects. A factor is an attribute with a clear meaning and measurement rule, such as sweetness described in a review. The ready-to-use Python interfaces take text columns; the paper's framework also considers images and external measurement tools.

If you have ratings and reviews but no attribute columns to analyze, start with [understand COAT](<concepts.md>). It explains why to discover variables and what Markov blankets, causal graphs, adjustment sets and effect estimates are useful for. Then follow [your first analysis](<quickstart.md>) to discover factors in apple reviews and read the result.

## Learn

- [Understand COAT](<concepts.md>): connect unstructured material to causal analysis.
- [Install and prepare](<installation.md>): install from PyPI, obtain example files and prepare a task.
- [Your first analysis](<quickstart.md>): install, inspect configuration, connect models, run MB and read one result.

## Complete a task

- [Prepare data](<data.md>): select input columns and encode your own CSV.
- [Connect models](<models.md>): use hosted Jev, chat models or a vLLM server.
- [Deploy local Kev](<kev.md>): prepare weights, start a server and match the client address.
- [Annotate existing factors](<annotation.md>): turn fixed definitions into a measurement table.
- [Analyze tables and fixed graphs](<causality.md>): learn a graph, find adjustment sets and estimate effects without language-model calls.
- [Use an agent](<agents.md>): authorize an agent to assist with analysis.

## Look up interfaces and settings

- [Discovery interfaces](<discovery.md>): MB, PAG and ADJ inputs, calls and result locations.
- [Configuration reference](<configuration.md>): saved example settings and model roles.
- [Result reference](<results.md>): definitions, graph endpoints, adjustment sets and estimate fields.
- [Package structure](<architecture.md>): functional module responsibilities.

## Read the documentation

Read the [online documentation](https://causalcoat.github.io/docs/#/) in English or [中文](https://causalcoat.github.io/docs/#/zh-cn/). It includes language-local full-text search, code copying and previous/next navigation. If you have a source checkout, you can also read Markdown directly or preview it locally:

```bash
python3 -m http.server 8000
# Open http://localhost:8000/docs/
```

8000 is an example documentation-preview port, unrelated to model-server ports. The site serves its Docsify and search assets locally; it needs no CDN or hosted search service.
