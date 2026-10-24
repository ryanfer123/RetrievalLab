# Contributing

Start with a reproducible problem and a small change. The Python runtime uses only
the standard library, and the browser loads self-hosted assets.

```sh
python -m unittest discover -s tests -v
python -m retrieval_lab
```

For retrieval changes, include a hand-calculated example and explain any impact
on tokenizer behavior, tie ordering, the export schema, or metric definitions.
For UI changes, test desktop and narrow mobile widths, keyboard operation,
validation feedback, and reduced motion. Keep every displayed score derived from
a real run. Label demonstration data clearly. Do not commit local databases,
private corpora, model credentials, or generated experiment history.

Useful extensions include importing external retrieval results for comparison,
adding a judged public corpus with a clear license, document-level score
explanations, and a richer relevance-label editor. Keep new methods separate from
the two baseline definitions so old exports remain understandable.
