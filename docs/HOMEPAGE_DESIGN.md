# RetrievalLab homepage direction

Preserve the implemented tool as `workspace.html` and make `/` a complete product
introduction. Main CTAs lead to the actual `/workspace` route. Root owns routing,
Supabase, and authentication; this page adds no account controls or cloud claims.

## Direction before code

- **Thesis:** a small research studio where retrieval results are evidence, not
  decorative dashboard numbers. The hero's focal asset is a real, inspectable
  ranking from the bundled demonstration corpus.
- **Palette:** midnight ink `#14283F`, cobalt `#245FDB`, muted teal `#087E80`, pale
  blue `#F1F5FA`, paper `#FFFFFF`, and secondary ink `#65768D`.
- **Type:** local Manrope throughout. Large, deliberate sans-serif headlines and
  compact document labels keep the identity distinct from GeoTrace's editorial
  landscape treatment.
- **Sequence:** clear product introduction and interactive actual-demo preview;
  three-step experiment workflow; precise method/metric explanation; real
  workspace screenshot and import contract; reproducibility details; FAQ; final CTA.
- **Hero evidence:** precompute the included corpus with the production engine,
  display real top-three rankings and relevance labels, and label it as a tiny
  hand-authored fixture. No fabricated differences or quality/benchmark claims.
- **Motion:** GSAP introduces headline words and the preview. Major headings get
  restrained word reveals as sections enter. Lenis is the sole smooth-scroll
  engine, selected over Locomotive for native layout. Reduced motion bypasses
  initialization. No continuous animation, pointer-only feature, or WebGL scene.
- **Assets:** actual existing workspace screenshot, original data presentation,
  local Manrope/GSAP/Lenis, and attributed Solar icons from Iconify. No stock
  photography, invented endorsements, or generic brand wall.

## Review

A general-purpose AI-chatbot landing page was rejected because the product does
not generate answers or measure their correctness. The homepage centers the
implemented operation: comparing lexical rankings against supplied judgments.
Metric definitions and import format are visible, and every illustration of a
result comes from the actual code or an actual recorded workspace screenshot.

## Prepared verification

- Authored homepage JavaScript passes `node --check`.
- Static HTML checks pass for unique IDs, internal anchor targets, and form labels.
- Every precomputed demonstration ranking and metric matches a fresh call to the
  production engine; its dataset SHA256 also matches.
- The product preview is byte-identical to the existing actual workspace capture.
- Root must add `web/home-assets/*` to package data, serve `/home-demo.json`,
  `/home.css`, `/home.js`, and homepage assets, and map `/workspace` to the
  preserved tool. Rendered desktop/mobile/reduced-motion checks follow routing.

No server, cloud module, existing app.js, or backend test was changed by this
homepage subtask.
