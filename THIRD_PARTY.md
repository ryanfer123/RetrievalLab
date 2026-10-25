# Asset and dependency provenance

All browser assets are served locally. No font CDN, telemetry, external model
endpoint, imagery service, or icon runtime is used by the application.

| Asset | Source package | Version | License / attribution |
| --- | --- | --- | --- |
| Manrope variable Latin font | `@fontsource-variable/manrope` | 5.3.0 | SIL Open Font License; see `retrieval_lab/web/vendor/fontsource-variable-manrope-LICENSE.txt` |
| GSAP core and ScrollTrigger | `gsap` | 3.15.0 | [GSAP Standard License](https://gsap.com/standard-license/); bundled copyright notices retained |
| Lenis JS and CSS | `lenis` | 1.3.27 | MIT; see bundled license |
| Solar line icons | `@iconify-json/solar` | 1.2.13 | Solar by [480 Design](https://www.figma.com/community/file/1166831539721848736), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), distributed through [Iconify](https://iconify.design/) |

Solar icons embedded in `index.html`: `widget-2-linear`, `add-square-linear`,
`play-circle-linear`, and `download-linear`. Colors and dimensions adapt to the
interface. The small `rl` brand mark is original. The rank-connection graphic is
an original data visualization derived from the current experiment. It is not
an illustration of invented results. No photographs, avatars, testimonials,
third-party company logos, or marketing endorsements are included.

The application source is MIT licensed; the assets above retain their own terms.

## Homepage evidence and assets

`retrieval_lab/web/home-assets/workspace.jpg` is an actual capture of the existing
RetrievalLab workspace from `docs/screenshots/desktop.jpg`. It shows the bundled
hand-authored demonstration corpus and is captioned as such; its visible scores
are not presented as external benchmark results.

The interactive homepage preview is precomputed from `web/demo.json` by the
production `compare` function at k = 3. The complete input, configuration, dataset
hash, rankings, and measured results are preserved in `web/home-demo.json`.
Displayed rankings and metrics were checked against a fresh engine evaluation.
Latency values are not displayed in the homepage preview.

Homepage icons reuse Solar via the same credited Iconify package. Additional
icons: `arrow-right-up-linear`, `arrow-down-linear`, `hamburger-menu-linear`,
`layers-linear`, `document-text-linear`, `sort-horizontal-linear`, `eye-linear`,
`settings-linear`, and `check-circle-linear`. The original `rl` mark and local
Manrope, GSAP, ScrollTrigger, and Lenis bundles are reused. No new media provider,
font CDN, invented testimonial, or third-party company logo is introduced.
