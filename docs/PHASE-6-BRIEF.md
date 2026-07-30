# Phase 6 Brief — Documentation Site, Packaging, Hosting

The implementation brief for Phase 6, fixed at the close of Phase 5 so that
packaging and publication are implemented against settled decisions rather
than re-designed. Companion to [ARCHITECTURE.md](ARCHITECTURE.md) §6 (the
deployment model this phase realises) and [DECISIONS.md](DECISIONS.md)
(D-035 records the design decisions; D-030 fixed the same-origin
integration this phase completes).

## Starting state

Phases 0–5 are complete at `v0.5.0`, methodology `2026.08.02`:

- The full assessment journey works end to end: questionnaire → evaluation →
  stored results → dashboard → comparison → PDF/XLSX export.
- Running the tool still takes two terminals (uvicorn + Vite dev server);
  ARCHITECTURE §6 promises "one command starts API + frontend".
- The documentation corpus (Methodology Report, evidence tables,
  architecture, decision log, UX specification, paper) lives in the
  repository only.

## Scope

| Deliverable | Realises |
|---|---|
| Single-command packaged app: one origin serving the API and the built frontend | ARCHITECTURE §6, D-030 same-origin model |
| Container image + compose file for VPS/PaaS hosting | ARCHITECTURE §6 "later hosting" |
| Documentation site publishing the existing corpus, brand-styled | D-012 (the methodology is the product and must be reviewable) |
| Release automation: tagged releases build and publish the artefacts | ARCHITECTURE §5 |

## Decided contracts (D-035 — implement, do not re-litigate)

1. **The wheel ships the app.** The production frontend build
   (`frontend/dist`) is embedded in the Python package as static assets and
   served by FastAPI at `/` from the same origin as `/api` — the packaged
   realisation of the D-030 same-origin decision, still with no CORS
   middleware. A console script (`nature-cooling serve`, wrapping uvicorn
   behind the existing `serve` extra) makes the local-first story literally
   one `pip install` and one command. CI builds the frontend and the wheel
   together so the embedded assets can never go stale.
2. **The container is packaging, not architecture.** One image built from
   the wheel (python-slim base, non-root user), plus a minimal
   `compose.yaml` mounting a named volume at the `platformdirs` data path so
   projects survive container replacement. No reverse proxy, TLS, or
   multi-user machinery in v1 — that remains the host's concern and v2's
   scope (OQ-31).
3. **The documentation site renders the existing corpus; it is not a second
   corpus.** MkDocs + Material, sourcing the current Markdown under `docs/`
   (methodology report, evidence tables, bibliography, sensitivity analysis,
   architecture, decisions, UX specification, phase briefs) with the README
   as the landing page — no page is authored twice, so the site cannot
   drift from the repository (the D-030 "one source of truth" rule applied
   to prose). Brand styling via the criterra.eu tokens and the three
   self-hosted families; no third-party requests from the published site.
   Published to GitHub Pages by CI on pushes to `main`.
4. **Releases are automated from tags.** A `vX.Y.Z` tag triggers: full
   gates, wheel build, container image pushed to GHCR, docs deploy, GitHub
   release with the wheel attached. The paper PDF and Methodology Report
   remain versioned in-repo, as D-012 fixed.
5. **Gates unchanged.** Backend and frontend CI jobs stay as they are; the
   new packaging path adds a smoke check (install the built wheel, start the
   server, assert `/` serves the app shell and `/api/meta` answers) rather
   than a new test framework.

## Non-negotiable rules (carried forward)

1. The engine and methodology are untouched; no version bump.
2. The frontend adds no runtime dependency; the backend adds none beyond
   packaging tooling (dev-only).
3. No AI attribution anywhere — code, docs, commits. Sole author:
   Dimitris Kafetzis. Run the attribution grep before pushing.

## Delivery

Conventional Commits, one coherent Phase 6 change set to `main`, CI green.
README gains the packaged quick-start (roadmap Phase 6 ✅); decision-log
entries recorded (D-035 + implementation rulings); backend package and
frontend `package.json` to 0.6.0; tag `v0.6.0` with a GitHub release
carrying the first packaged artefacts.
