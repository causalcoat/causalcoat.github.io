---
name: coatlearn
description: Use COAT to measure user-defined factors in text, discover factors related to a target, build a partial ancestral graph, or find adjustment sets and estimate a treatment effect. Use when a user asks to analyze text with coatlearn or choose among its annotation, MB, PAG and ADJ methods.
---

# Analyze data with coatlearn

Act for the data analyst through the public Python interfaces or CLI. The models inside COAT propose and measure factors; your role is to choose an appropriate task with the user, prepare it and explain its result.

## 1. Establish the question

Identify the user's question and the local dataset they permit you to inspect. Record the observation represented by each row, the text column and the existing measured variables. Read headers and the necessary sample only; keep private text out of public output.

Choose the smallest sufficient method:

- **Annotation:** the user already has definitions and wants measured values.
- **MB:** the user wants factors that summarize information about a named target.
- **PAG:** the user wants a relationship graph starting from measured variables.
- **ADJ:** the user has a defined treatment and outcome and wants adjustment sets and effect estimates.

Define the chosen method in ordinary language. Resolve ambiguous treatment, outcome or coding choices with the user before preparing the run. A factor is a measured attribute, not an established cause.

## 2. Prepare an explicit plan

Use [the interface reference](references/interfaces.md) for callable entry points. When working from a source checkout, use its documentation for the full configuration and result definitions. When using an installed package, inspect `python -m coatlearn --help` and the installed public signatures rather than assuming a source-tree layout.

Write down the selected columns, required value mappings, model identities and addresses, analysis settings, causal assumptions and a fresh output directory. Use the supplied TOML examples as examples of settings, not as universal causal assumptions. Keep all credentials in named environment variables or a user-selected dotenv file.

For CLI tasks, run the command without `--run` and inspect its local summary. For standalone annotation, parse every definition locally first. This step is complete when the task inputs and settings match the user's stated question.

## 3. Obtain execution permission

Before any model call, tell the user:

- which models and endpoints will be called;
- which text or proposal examples will leave the machine;
- that hosted calls may incur charges, with annotation work scaling with factors, rows and rounds;
- where private run artifacts will be saved.

Ask for permission for this specific plan. A request to inspect data or prepare configuration is not permission to call models. Do not print keys, read unrelated credential files, start GPU processes or change model providers on the user's behalf without explicit authorization.

## 4. Execute the approved task

Use the checked configuration and the approved model selection. Retain row order, explicit mappings and the run settings. Preserve the result and its provenance. Use the package as a library; do not edit discovery code, factor rules or statistical settings to obtain a preferred result.

If execution stops, report the recorded stage and exception type without exposing prompts or credentials. Request new permission before a new model run, parameter change or provider substitution. Use existing saved outputs for further explanation when possible.

## 5. Explain the analysis

Report the chosen question, data columns and models, then the relevant output: measured values, MB names, graph marks, or adjustment sets and estimates. Link the saved result and identify supplied assumptions separately from discoveries.

For annotation, distinguish factor value from confidence and unmentioned text from value zero. For graphs, explain circles as retained direction uncertainty. For ADJ, distinguish no estimated effect from a numeric zero, and distinguish an empty adjustment set from finding no set. Use per-set records to associate each estimate with its adjustment variables.

Execution status describes whether the software ran, not whether its causal claims are established. End with a plain-language answer that states the assumptions needed for its interpretation. The task is complete when the user can locate the output and understand what it does and does not establish.
