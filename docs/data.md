<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# Prepare data

Discovery needs text for each observation and target variables you have already measured. A row may contain a review and its rating, or a customer's post, email receipt and website visit. Text need not repeat the numeric columns; both must refer to the same observation.

## Select columns for your question

| Method | Existing numeric columns | Unstructured content | Purpose |
| --- | --- | --- | --- |
| MB | One target, such as `score` | Such as `text` | Seek factors jointly providing target information. |
| PAG | Initial variables, such as `taste` and `score` | Such as `text` | Discover factors to refine structural information about the initial variables. |
| ADJ | Treatment and outcome, such as `sent` and `visited` | Such as `post` | Seek adjustment variables and estimate the specified effect. |

The package's ready-to-use interfaces take string text columns, not images or external databases. Existing numeric analysis columns should contain finite, nonmissing values; text columns should contain nonempty strings. Factors annotated later can be missing when not mentioned.

Only named columns enter discovery; other columns can stay in the CSV. In particular, true factor values recorded in synthetic data do not automatically enter analysis merely because they exist in the file. Row order and duplicate texts are preserved.

## Understand the two examples

The [apple graph1 CSV](<https://github.com/causalcoat/COAT-Learn/tree/main/data/apple_reviews_PAG_graph1.csv>) has 1,000 rows from the authors' synthetic apple-review research data. MB reads `Score` and `Review`; PAG reads `Taste`, `Score` and `Review`. They share data but ask different questions: target-information selection versus structural refinement through additional variables. These are not real customer reviews collected from an online shop.

The [Hillstrom posts CSV](<https://github.com/causalcoat/COAT-Learn/tree/main/data/hillstrom_email_visit_post.csv>) has 2,000 rows with synthetic customer posts and email/visit records. It uses the study's confounded setting, not the original randomized Hillstrom customer table. ADJ reads only `email_type`, `visit` and `post`, not hidden customer attributes directly.

In that file, `Yes` in `email_type` means sent and an empty cell means not sent; `visit` uses `Yes/No` for visits. The [ADJ configuration](<https://github.com/causalcoat/COAT-Learn/tree/main/config/adj.toml>) explicitly maps them to 1/0. “Empty cell means control” is a convention of this dataset, not a general missing-value policy. See the [data inventory](<https://github.com/causalcoat/COAT-Learn/tree/main/data/README.md>) for provenance records and file hashes.

## Use your own table

Input can be a local CSV with a header or a pandas DataFrame. Define the observation unit and column meanings before selecting columns. If treatment and outcome are not numeric yet, encode them explicitly before calling discovery:

```python
import pandas as pd

frame = pd.read_csv("customers.csv")
frame["sent"] = frame["email_label"].map({"sent": 1, "not_sent": 0})
frame["visited"] = frame["visit_label"].map({"yes": 1, "no": 0})
print(frame[["sent", "visited"]].value_counts())
```

`sent=1` defines treatment and `sent=0` the comparison. Outcome timing should match the question, for example visits after email sending. Pass the prepared `frame` to a [discovery interface](<discovery.md>). For TOML, copy the closest task configuration and change data paths and column names under `[task]`; data paths resolve relative to that file.

Do not copy the supplied ADJ example's direction priors and adjustment exemption directly to new data. They depend on its data-generating setup; see [research assumptions](<configuration.md#research-assumptions>).

## Confirm where text goes

Hosted models receive text in requests. The main model receives selected proposal examples, the annotator receives each text to measure, and review records may include proposal examples. Local Kev keeps decision requests local, but a hosted main model still receives proposal examples.

The output directory can also contain original content. Factor process records may include examples and answers; conversation saving adds raw prompts and responses. Store the whole output directory according to the source data's sensitivity. Keep credentials out of data, configuration and results.

The two supplied example CSV files use [CC BY 4.0](<https://github.com/causalcoat/COAT-Learn/tree/main/data/LICENSE>), separately from the software's [Apache-2.0 license](<https://github.com/causalcoat/COAT-Learn/tree/main/LICENSE>). Retain their [source and attribution information](<https://github.com/causalcoat/COAT-Learn/tree/main/data/README.md>) and describe any changes when redistributing them.
