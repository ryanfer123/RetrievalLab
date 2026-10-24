# Validation record

Verified locally on macOS, 24 October 2026.

| Check | Result |
| --- | --- |
| Python engine and real HTTP/SQLite integration tests | 21 passed |
| Installable wheel | Built successfully; complete browser assets verified in archive |
| Authored JavaScript syntax | `node --check` passed for app.js and motion.js |
| Desktop browser | 1470 px viewport; app loads, comparison runs and query switching updates both lists |
| Mobile browser | 390 x 844; stacked layout, comparison action works |
| Invalid import | Missing documents rejected with visible validation feedback |
| History | Saved experiments load after refresh; persistence across server instances covered in HTTP tests |
| Export | JSON response and attachment header verified; browser download confirmed by user |
| Reduced motion | Emulated reduce: heading remains visible and Lenis is not initialized; preference restored |
| Horizontal fit | document width equals viewport width in desktop check |
| Browser console | No application errors; unrelated extension warnings excluded |
| Static first frame | Semantic heading and controls visible before motion; no-JavaScript notice and CLI alternative included |

Screenshots: [desktop](screenshots/desktop.jpg), [mobile](screenshots/mobile.jpg).

Motion uses GSAP with ScrollTrigger and one Lenis instance. Reduced motion bypasses
initialization. Page cleanup removes event listeners and ticker callbacks and
destroys Lenis. No WebGL, pointer dependency, image generator, analytics, remote
font service, or model service is required. Assets and license notices are listed
in [THIRD_PARTY.md](../THIRD_PARTY.md).

The demonstration data is tiny and hand-authored. Its scores establish neither
ranking superiority nor performance on external benchmarks. Native browser
interaction checks were performed manually through automation; there is no
committed automated browser-test runner yet. Runtime tests used Python 3.15 locally;
the CI matrix covers 3.10, 3.12 and 3.13.
