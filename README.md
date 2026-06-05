# BetterCode GenAI Summit 2026

Static conference bundle for the BetterCode GenAI Summit 2026.

The repository is intentionally HTML-only for the presentation layer: every deck
can be opened directly in a browser and deployed to GitHub Pages without Bun,
Vite, Node, or a build step.

Deployed site: [https://telekom.github.io/better-code/](https://telekom.github.io/better-code/)

## Presentations

| Page | Speakers | Source talk title |
| --- | --- | --- |
| [KI-Agenten f&uuml;r Legacy-Analyse](https://telekom.github.io/better-code/presentations/ki-agenten-legacy-analyse.html) | Adit & Lars | KI-Agenten f&uuml;r Legacy-Analyse: MCP, Skills und dynamischer Kontext in der Praxis |
| [Context Engineering](https://telekom.github.io/better-code/presentations/context-engineering.html) | Adit & Lars | Supporting context material for the main talk |
| [KI in der Praxis: Legacy-Systeme modernisieren](https://telekom.github.io/better-code/presentations/ki-modernisierung-legacy-systeme.html) | Laura & Sigrid | KI in der Praxis: Strategien zur Modernisierung komplexer Legacy-Systeme |
| [Catalog Migration Run Overview](https://telekom.github.io/better-code/presentations/migration-run-overview.html) | Demo artifact | Visual overview of the one-modernizer migration run |

Start from the [deployed overview page](https://telekom.github.io/better-code/).

## Live Demo

The [`demo/`](./demo/) folder contains the modernization demo:

- [`demo/one-modernizer/`](./demo/one-modernizer/) - the Claude Code plugin
  for the pipeline: discover -> assess -> decompose -> architect -> implement -> validate.
- [`demo/eShopModernizing/`](./demo/eShopModernizing/) - the Microsoft
  eShopModernizing sample used as the migration target.

original Demo Repo where we cloned from: https://github.com/dotnet-architecture/eShopModernizing

The demo migrates one feature, **Catalog Item Management**, from
`eShopLegacyMVC` to a generated .NET 8 ASP.NET Core MVC + EF Core target.

Useful demo evidence:

- [Demo runbook](./demo/README.md)
- [Pipeline index](./demo/eShopModernizing/eShopLegacyMVCSolution/.migration/index.json)
- [Graph report](./demo/eShopModernizing/eShopLegacyMVCSolution/.migration/discovery/graphify-out/GRAPH_REPORT.md)
- [Migration sequence](./demo/eShopModernizing/eShopLegacyMVCSolution/.migration/assess/migration-sequence.md)
- [Decomposition summary](./demo/eShopModernizing/eShopLegacyMVCSolution/.migration/decompose/catalog-item-management/summary.md)
- [Architecture summary](./demo/eShopModernizing/eShopLegacyMVCSolution/.migration/architect/catalog-item-management/summary.md)
- [Validation report](./demo/eShopModernizing/eShopLegacyMVCSolution/.migration/validate/catalog-item-management/report.md)
- [Generated target README](./demo/eShopModernizing/eShopLegacyMVCSolution/target/catalog-item-management/README.md)
- [Root GitLab Pages CI](./.gitlab-ci.yml)
- [Preserved catalog-service build/test CI](./demo/eShopModernizing/eShopLegacyMVCSolution/target/catalog-item-management/.gitlab-ci.yml)

## Structure

```text
.
├── index.html
├── presentations/
│   ├── ki-agenten-legacy-analyse.html
│   ├── context-engineering.html
│   ├── ki-modernisierung-legacy-systeme.html
│   └── migration-run-overview.html
├── docs/
│   ├── Adit-Lars-Vortrag.md
│   ├── Laura-Sigrid-Vortrag.md
│   └── adit-lars-todo.md
└── demo/
    ├── README.md
    ├── one-modernizer/
    └── eShopModernizing/
```

## Deployment

GitHub Pages deploys the static HTML folders via
[`.github/workflows/pages.yml`](./.github/workflows/pages.yml). In a GitHub
repository, enable Pages with **Source: GitHub Actions**.

GitLab Pages deploys the same static bundle via [`.gitlab-ci.yml`](./.gitlab-ci.yml).
The root GitLab CI is Pages-only; the generated catalog build/test/package pipeline
is preserved as demo evidence under `demo/eShopModernizing/.../target/catalog-item-management/.gitlab-ci.yml`.

Large videos should stay out of the repository. Upload them to GitHub issues or
another stable host and embed the resulting URLs in the HTML decks.
