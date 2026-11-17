<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# Local dependencies

The supplied TOML examples choose a decision model for concept comparison. They do not need WordNet for this step. Direct Python discovery calls without that comparator use a name-overlap path that requires an installed WordNet corpus.

Install the corpus explicitly in the Python environment used for analysis:

```bash
python3 -m nltk.downloader wordnet omw-1.4
```

The package does not download corpora during analysis.

For model addresses and credentials, see [connect models](<models.md>). For a matching local decision server, see [deploy Kev](<kev.md>). Command-line options are available through `python3 -m coatlearn mb --help`.
