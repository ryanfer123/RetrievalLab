"use strict";
const $ = (id) => document.getElementById(id);
const escapeHtml = (value) =>
  String(value).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const runButtonContent = $("run-button").innerHTML;
let state = { datasets: [], runs: [] },
  currentRun = null,
  selectedQuery = 0,
  busy = false;

async function api(path, data) {
  const response = await fetch(
    path,
    data === undefined
      ? {}
      : {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        },
  );
  const value = await response.json();
  if (!response.ok)
    throw new Error(value.error || `Request failed (${response.status}).`);
  return value;
}
function notice(message, error = false) {
  $("notice").textContent = message;
  $("notice").hidden = !message;
  $("notice").classList.toggle("error", error);
}
function updateDataset() {
  const dataset = state.datasets.find(
    (d) => d.id === $("dataset-select").value,
  );
  $("dataset-meta").textContent = dataset
    ? `${dataset.documents.length} documents · ${dataset.queries.length} labeled queries`
    : "Your documents and relevance judgments.";
  $("run-button").disabled = !dataset || busy;
}
async function refresh(preferred) {
  const previous = preferred || $("dataset-select").value;
  state = await api("/api/state");
  $("dataset-select").innerHTML =
    '<option value="">Choose or import a dataset</option>' +
    state.datasets
      .map(
        (d) =>
          `<option value="${escapeHtml(d.id)}">${escapeHtml(d.name)}</option>`,
      )
      .join("");
  if (state.datasets.some((d) => d.id === previous))
    $("dataset-select").value = previous;
  else if (state.datasets.length)
    $("dataset-select").value = state.datasets[0].id;
  $("run-count").textContent = state.runs.length;
  $("history").innerHTML = state.runs.length
    ? state.runs
        .map(
          (r) =>
            `<button data-run="${escapeHtml(r.id)}" class="${currentRun?.id === r.id ? "active" : ""}">${escapeHtml(r.name)}<small>${escapeHtml(new Date(r.created).toLocaleString())} · k = ${r.k}</small></button>`,
        )
        .join("")
    : '<p class="muted">Your saved comparisons will appear here.</p>';
  updateDataset();
}
function renderRun() {
  if (!currentRun) return;
  const { results, dataset, created } = currentRun,
    k = results.k;
  $("empty-state").hidden = true;
  $("results").hidden = false;
  $("run-meta").textContent =
    `${dataset.name} · ${dataset.queries.length} queries · Top ${k} · ${new Date(created).toLocaleString()}`;
  $("metric-summary").innerHTML = ["bm25", "tfidf"]
    .map((method) => {
      const m = results.methods[method];
      return `<article class="method-summary ${method}"><div class="method-title"><h3><span class="method-swatch"></span>${method === "bm25" ? "BM25" : "TF-IDF cosine"}</h3><span>${m.mean_latency_ms.toFixed(3)} ms / query</span></div><div class="metric-values">${[
        ["ndcg", "nDCG"],
        ["mrr", "MRR"],
        ["recall", "Recall"],
        ["precision", "Precision"],
      ]
        .map(
          ([key, label]) =>
            `<div class="metric-value"><span>${label}@${k}</span><strong>${m[key].toFixed(3)}</strong><meter min="0" max="1" value="${m[key]}" aria-label="${label} score">${m[key]}</meter></div>`,
        )
        .join("")}</div></article>`;
    })
    .join("");
  $("query-list").innerHTML = results.queries
    .map(
      (q, i) =>
        `<button data-query="${i}" class="${i === selectedQuery ? "active" : ""}" aria-pressed="${i === selectedQuery}"><small>Query ${i + 1} / ${results.queries.length}</small>${escapeHtml(q.text)}</button>`,
    )
    .join("");
  renderQuery();
}
function renderQuery() {
  const q = currentRun.results.queries[selectedQuery];
  const left = q.results.bm25.ranking.slice(0, 3),
    right = q.results.tfidf.ranking.slice(0, 3);
  const compact = (id) =>
    escapeHtml(id.length > 18 ? id.slice(0, 17) + "…" : id);
  const links = left
    .map((item, i) => {
      const j = right.findIndex((r) => r.id === item.id);
      return j < 0
        ? ""
        : `<path class="${q.relevant_ids.includes(item.id) ? "relevant-link" : ""}" d="M 139 ${54 + i * 39} C 173 ${54 + i * 39}, 195 ${54 + j * 39}, 229 ${54 + j * 39}"/>`;
    })
    .join("");
  const labels = (items, x) =>
    items
      .map(
        (r, i) =>
          `<text class="rank-label" x="${x}" y="${58 + i * 39}">${i + 1}</text><text class="rank-doc" x="${x + 16}" y="${58 + i * 39}">${compact(r.id)}</text>`,
      )
      .join("");
  $("rank-map").innerHTML =
    `<svg class="rank-map-svg" viewBox="0 0 370 175" role="img" aria-label="Top three ranks for the selected query. Lines connect the same document across both retrievers."><text class="rank-map-title" x="13" y="24">BM25</text><text class="rank-map-title" x="241" y="24">TF-IDF cosine</text>${links}${labels(left, 13)}${labels(right, 241)}</svg>`;
  $("rank-status").textContent =
    `Query ${selectedQuery + 1} of ${currentRun.results.queries.length}`;
  $("rank-caption").textContent = q.text;
  document.dispatchEvent(new CustomEvent("lab:results"));
  $("query-description").innerHTML =
    `<h3>${escapeHtml(q.text)}</h3><div class="query-subtitle">Relevant document IDs: ${q.relevant_ids.map(escapeHtml).join(", ")}</div>`;
  $("rankings").innerHTML = ["bm25", "tfidf"]
    .map((method) => {
      const result = q.results[method];
      return `<section class="${method}"><div class="ranking-header"><h4>${method === "bm25" ? "BM25" : "TF-IDF cosine"}</h4><span>nDCG ${result.metrics.ndcg.toFixed(3)}</span></div>${result.ranking.length ? `<ol class="ranking-list">${result.ranking.map((r) => `<li><div class="result-title">${escapeHtml(r.id)}${q.relevant_ids.includes(r.id) ? '<span class="relevant-label">Relevant</span>' : ""}</div><p>${escapeHtml(r.text)}</p><span class="score">Retrieval score ${r.score.toFixed(4)}</span></li>`).join("")}</ol>` : '<p class="no-match">No matching terms. This retriever returned no documents for this query.</p>'}</section>`;
    })
    .join("");
}
function showImport() {
  $("import-error").hidden = true;
  $("import-dialog").showModal();
}
for (const id of ["import-button", "import-nav"])
  $(id).addEventListener("click", showImport);
for (const id of ["close-import", "cancel-import"])
  $(id).addEventListener("click", () => $("import-dialog").close());
$("dataset-select").addEventListener("change", updateDataset);
$("dataset-file").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  if (file.size > 2 * 1024 * 1024) {
    $("import-error").textContent = "File exceeds 2 MiB.";
    $("import-error").hidden = false;
    return;
  }
  $("dataset-json").value = await file.text();
});
$("import-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("save-import").disabled = true;
  $("import-error").hidden = true;
  try {
    const dataset = await api(
      "/api/datasets",
      JSON.parse($("dataset-json").value),
    );
    await refresh(dataset.id);
    $("import-dialog").close();
    notice(`Imported “${dataset.name}”. Run a comparison when you’re ready.`);
  } catch (error) {
    $("import-error").textContent = error.message;
    $("import-error").hidden = false;
  } finally {
    $("save-import").disabled = false;
  }
});
$("demo-button").addEventListener("click", async () => {
  $("demo-button").disabled = true;
  try {
    const demo = await api("/demo.json");
    const dataset = await api("/api/datasets", demo);
    await refresh(dataset.id);
    notice(
      "Demo corpus loaded. These are hand-authored documents and labels, not an external benchmark.",
    );
    $("run-button").focus();
  } catch (error) {
    notice(error.message, true);
  } finally {
    $("demo-button").disabled = false;
  }
});
$("run-button").addEventListener("click", async () => {
  busy = true;
  updateDataset();
  $("run-button").textContent = "Running comparison…";
  notice("");
  try {
    currentRun = await api("/api/runs", {
      dataset_id: $("dataset-select").value,
      k: Number($("cutoff").value),
    });
    selectedQuery = 0;
    renderRun();
    await refresh();
    notice(
      "Comparison saved. Inspect a query or export the complete experiment.",
    );
  } catch (error) {
    notice(error.message, true);
  } finally {
    busy = false;
    $("run-button").innerHTML = runButtonContent;
    updateDataset();
  }
});
$("query-list").addEventListener("click", (event) => {
  const button = event.target.closest("[data-query]");
  if (!button) return;
  selectedQuery = Number(button.dataset.query);
  $("query-list")
    .querySelectorAll("[data-query]")
    .forEach((b) => {
      const active = Number(b.dataset.query) === selectedQuery;
      b.classList.toggle("active", active);
      b.setAttribute("aria-pressed", active);
    });
  renderQuery();
  $("query-list").querySelector(`[data-query="${selectedQuery}"]`).focus();
});
$("history").addEventListener("click", async (event) => {
  const button = event.target.closest("[data-run]");
  if (!button) return;
  try {
    currentRun = await api("/api/runs/" + button.dataset.run);
    selectedQuery = 0;
    renderRun();
    await refresh();
    notice("Saved experiment loaded.");
  } catch (error) {
    notice(error.message, true);
  }
});
$("export-button").addEventListener("click", () => {
  if (!currentRun) return;
  const anchor = document.createElement("a");
  anchor.href = `/api/runs/${encodeURIComponent(currentRun.id)}?download=1`;
  anchor.download = `retrieval-lab-${currentRun.id}.json`;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  notice(
    "Export requested. Your download includes the dataset, labels, parameters, and measured results.",
  );
});

(async () => {
  try {
    await refresh();
    if (state.runs.length) {
      currentRun = await api("/api/runs/" + state.runs[0].id);
      renderRun();
      await refresh();
    }
  } catch (error) {
    notice(`Could not load the workspace: ${error.message}`, true);
  }
})();
