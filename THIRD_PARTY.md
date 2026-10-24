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
