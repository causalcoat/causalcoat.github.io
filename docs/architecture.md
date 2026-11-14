<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# Package structure

The package is divided by function. Each module has an independent use, and discovery composes the others rather than owning every operation.

| Module | Responsibility |
| --- | --- |
| `models` | OpenAI-compatible chat and native System One HTTP calls |
| `annotation` | Definition parsing, measurement, review and concept comparison |
| `discovery` | MB, PAG and ADJ iteration |
| `causality` | Conditional independence, graph operations, adjustment and IPW |
| `cli` | Arguments for shared configuration and execution |
| `utils` | General logging and explicit sampling helpers |

The package root keeps five convenient exports: `ModelConfig`, `RunConfig`, `run_mb`, `run_pag` and `run_adj`. Independent annotation and causal operations are exported by their corresponding modules.

Model transport does not interpret factor values. Annotation owns that mapping. Causal calculations consume measured values and graph assumptions without calling a model. This makes each stage usable outside the full discovery procedure.

Configuration loading creates a task plan without creating a model client. Local checking projects the requested columns and records explicit mappings. Execution invokes the same root Python functions used by direct callers and saves their results.

The [source provenance](<https://github.com/causalcoat/COAT-Learn/tree/main/SOURCE_MAP.md>) records the research origin of the implementation. Historical run records are not required to use or install this project.
