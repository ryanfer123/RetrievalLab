# RetrievalLab

A local web workbench for comparing BM25 and TF-IDF retrieval against your own
relevance judgments. Import a corpus, run both baselines, inspect ranked evidence,
and export a reproducible experiment.

The engine and SQLite API are implemented. The comparison interface is in progress.

## Run

Python 3.10+; no runtime dependencies or API keys.

```sh
python -m retrieval_lab
```

Open http://127.0.0.1:8765. The app binds to loopback only.

## Tests

```sh
python -m unittest discover -s tests -v
```
