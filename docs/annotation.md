<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# Annotate existing factors

With attributes already chosen, apply their definitions to each observation to produce a numeric table without running discovery. For example, turn the sweetness described in reviews into a column for summarizing its distribution or modeling alongside existing ratings.

**Factor annotation** has two parts: write a shared assignment rule, then ask an annotation model to apply it to each observation. A definition gives a column its meaning; a value is the measurement for one row. Annotation does not determine causal relationships.

This page uses [hosted Jev](<models.md#connect-hosted-models>). Set `TYPESAFE_API_KEY` in the environment before execution. Alternatively, [start Kev](<kev.md>) and replace `jev` with `kev9b`.

## Write an assignable definition

State the attribute, its possible values and what content supports each value. The definition below measures “sweetness described in the review.” It measures explicit statements, not the apple's objective sugar content in the world:

```python
definition = """Sweetness
- Type: score
- Values: 0, 1, 2
- Mentioned when: the text describes the apple's sweetness
- 0: explicitly described as not sweet
- 1: explicitly described as mildly sweet
- 2: explicitly described as very sweet
"""
```

`Type: score` declares ordered levels, `Values` gives their original numeric values, and `Mentioned when` states what mention is sufficient for assignment. The last three lines define the levels. Discovery configurations call this the `general` format; different factors can declare different scales.

A review that does not mention sweetness should not thereby mean “not sweet.” When the mention question's yes probability is below 0.5, this interface records the measurement as missing (`NaN`). Zero already has a defined meaning here: explicitly described as not sweet.

## Annotate a batch and save it

Continue with this code. It sends the two example texts to the selected annotation service:

```python
from coatlearn.annotation import annotate
from coatlearn.models.presets import jev

annotations = annotate(
    texts=["Very sweet apples.", "The delivery arrived yesterday."],
    definitions={"Sweetness": definition},
    model=jev,
)
print(annotations.values)
print(annotations.metadata[["factor", "value", "confidence", "mention_probability"]])
annotations.values.to_csv("values.csv", index=False)
```

`annotations.values` has one row per input observation and one column per factor. `annotations.metadata` separately records probabilities, confidence and missing-value information. `annotations.specs` holds the measurement specifications actually used so you can inspect questions and value mappings later.

Under the definition, the first review supports “very sweet,” while the second supplies no sweetness information. Actual numbers are computed from the model's probabilities, not predetermined output. A pandas Series input retains its index in the measurement table so it can align with original numeric columns.

Put multiple factors in the `definitions` mapping. `batch_size` controls factors per request, up to 8; `concurrency` controls worker threads and defaults to 16. Each request uses one text, and complete definitions are translated into questions automatically.

## Use an LLM for annotation

The same `annotate` function accepts a chat-model configuration. Set `DEEPSEEK_API_KEY`, then reuse the definition above:

```python
from coatlearn import ModelConfig

model = ModelConfig(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    api_key_env="DEEPSEEK_API_KEY",
    thinking="disabled",
    temperature=None,
)
annotations = annotate(
    ["Very sweet apples.", "The delivery arrived yesterday."],
    {"Sweetness": definition},
    model=model,
    concurrency=1,
)
print(annotations.values)
```

The LLM returns a numeric answer for each text–factor pair. Missing mentions are recorded as `NaN`; probability and confidence fields remain empty. For LLM annotation, each factor uses a separate request. The probability-weighted interpretation below applies to Jev and Kev.

## Understand values and confidence

A `score` value is the probability-weighted average of the declared numbers. If levels 0, 1 and 2 have probabilities 0.1, 0.2 and 0.7, the value is `0×0.1 + 1×0.2 + 2×0.7 = 1.6`. This is not “confidence of 1.6” and need not be an integer.

Use `choice` for mutually exclusive categories. It returns the selected category's declared numeric code. For example, purchase channels below are encoded as 0 and 1. The codes do not imply an ordering of the categories:

```python
channel_definition = """PurchaseChannel
- Type: choice
- Values: online=0, store=1
- Mentioned when: the text explicitly states where the purchase was made
- online: purchased through an online shop
- store: purchased at a physical shop
"""
```

Confidence describes uncertainty in the model's answer; a factor value describes the observation's attribute. They are stored separately. Handle categorical codes according to the downstream statistical method, not as continuous quantities merely because they are numbers.

## Inspect measurement questions when needed

Ordinary `annotate` usage requires no manual parsing. Before requests, it automatically translates a definition into a `MeasurementSpec`: the model questions, mention check and numeric mapping.

To inspect exactly what the service will be asked, perform that translation alone. It does not call a model, assign values to text or ask another model to rewrite your rules:

```python
from coatlearn.annotation import factor_definition_to_spec

spec = factor_definition_to_spec("Sweetness", definition)
print(spec.to_request_questions())
```

Another supported format is `simple`, which defines criteria for three labels, `-1`, `0` and `1`, and uses the selected label directly. It fits attributes already defined on that three-level scale; it does not require every factor to have three levels. To start with this page, use the `general` definition above.

## Review and compare definitions when needed

You can annotate directly with your own definitions. To inspect wording and format first, explicitly call `review_definition` with real application examples:

```python
from coatlearn.annotation import review_definition

review = review_definition(
    "Sweetness", definition,
    examples="- The apple is very sweet.\n- This apple is not sweet.",
    model=jev,
)
print(review["decision"])
```

Review checks whether a definition is clear and meets the format requirements. Records may contain the examples you supply; keep them private.

With many candidates, use `compare_definitions` to ask whether two definitions describe the same core attribute. For example, compare sweetness with purchase channel:

```python
from coatlearn.annotation import compare_definitions

comparison = compare_definitions(
    definition, channel_definition,
    task_context="Identify attributes explicitly described in apple reviews.",
    model=jev,
)
print(comparison["decision"])
```

Concept comparison detects duplicate attributes. It does not merge variables because they are correlated or make values under different definitions interchangeable. Standalone `annotate` does not automatically run review or concept comparison. Their use in discovery depends on [model-role configuration](<configuration.md#model-roles>).
