# Source and publishing policy

- Edit graph content and generators in `work/*.py`, course templates in `src/`, and teaching documentation in `docs/`.
- Never commit rendered HTML, PDF, generated diagrams/catalogs, `dist/`, `outputs/`, screenshots, QA reports or history backup bundles. Editable `.html.in` templates and authored source assets are allowed.
- Build with `python3 scripts/build_site.py`. Keep `/patterns/atlas/`, `/patterns/course/`, and `/patterns/lab/` portable under GitHub Pages project hosting.
- Run `python3 scripts/check_site.py --before-pdf`, `npm run qa`, then `python3 scripts/check_site.py` after site changes. Inspect affected course PDF pages for layout issues.
- Deploy through GitHub Actions and Pages artifacts only. Do not create a build-output branch or commit artifacts to fix deployment.
- Keep synthetic-case boundaries explicit. This repository contains course materials; the independent `agentic-styles/labs` repository supplies the baseline, synthetic materials, contracts and scoring. Course links pin `v0.1.0/booking-precheck`. Do not imply that offline rule/protocol checks prove real-LLM accuracy, safety or an implemented Multi-Agent solution.
- Keep website builds independent of `labs`: do not fetch its code, install its dependencies or add it as a submodule to render or deploy the course.
