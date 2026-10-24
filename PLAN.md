# RetrievalLab implementation

Build a local, complete retrieval evaluation workbench that answers: which lexical
retriever finds the documents marked relevant to these questions?

1. Implement deterministic BM25 and cosine TF-IDF with binary relevance metrics.
2. Validate imported corpora and judgments before writing to SQLite.
3. Serve a local web app with corpus import, comparison, history, and JSON export.
4. Test metric calculations, persistence, HTTP errors, and the rendered workflow.

Design: a slate-blue instrument panel on a pale blue workspace; navy #14283F,
blue #245FDB, teal #087E80, background #F1F5FA, white #FFFFFF, muted #5B6D83.
Use the system humanist sans stack for controls and Georgia only for the product
headline. A two-column ranking comparison is the defining visual; scores sit
beside the ranked evidence. On mobile, stack both result lists and collapse the
navigation to a top row. Avoid decorative charts, invented metrics, and startup
marketing copy. Every number must come from the current saved run.

Success: a fresh Python installation can launch the app with no runtime packages;
a user can import a valid dataset, run both retrievers, inspect query results,
reload saved experiments, and export a self-contained run. Demo data is explicitly
identified as a hand-authored fixture, not an external benchmark.
