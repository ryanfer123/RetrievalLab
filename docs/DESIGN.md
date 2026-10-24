# Design and implementation workflow

The frontend follows the `build-awwwards-quality-sites` and `frontend-design`
workflows. The defining visual is an evidence diagram drawn from the two actual
ranked lists. The interface uses a pale blue instrument workspace, a restrained
navy navigation rail, locally served Manrope, and licensed Solar interface icons.
It contains no invented testimonials, endorsements, or benchmark claims.

GSAP introduces the heading and animates rank connections. Lenis is the sole
smooth-scroll engine, chosen to retain native document flow. Reduced motion
bypasses initialization, and page cleanup removes its ticker and listeners.
Three.js would obscure the ranked evidence, so it is omitted. Static semantic
content stays visible when motion is unavailable; a no-JavaScript notice provides
the command-line route.

The `karpathy-guidelines` workflow keeps the runtime small: standard-library
Python, SQLite, explicit algorithm definitions, and no external inference service.
The `python-testing` workflow uses hand-calculated metric examples, real temporary
SQLite databases and loopback HTTP requests, and regression tests for validation
and resource ownership. The existing unittest framework avoids an unnecessary
runtime dependency while preserving test isolation.

The `frontend-testing-debugging` workflow was applied through the available
computer/browser tools: desktop and mobile renders, primary workflow interactions,
invalid imports, console inspection, query transitions, and reduced-motion checks.
[VALIDATION.md](VALIDATION.md) records results and limits; screenshots are actual
app renders. The design quality workflow is a method, not a claim of an award.
