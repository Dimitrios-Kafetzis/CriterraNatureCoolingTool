# Phase 5 Brief — Report Export

The implementation brief for Phase 5, fixed at the close of Phase 4 so that
report export is implemented against settled decisions rather than
re-designed. Companion to [UX-SPECIFICATION.md](UX-SPECIFICATION.md) §6 (the
results page the report mirrors), [ARCHITECTURE.md](ARCHITECTURE.md) §2
(the report builder's place in the backend), and
[DECISIONS.md](DECISIONS.md) (D-033 records the design decisions; OQ-13/D-011
fixed the 2-page PDF long ago).

## Starting state

Phases 0–4 are complete at `v0.4.0`, methodology `2026.08.02`:

- The web application realises the UX specification in full; its results
  page renders stored results verbatim, and its **Export report** button is
  disabled with an "arrives in Phase 5" note.
- Stored assessments hold their full input and full versioned
  `AssessmentResult`, never recomputed (OQ-15, D-028/D-029).

## Scope

A report builder in the backend and the two endpoints that expose it,
wired to the web app's Export action:

| Deliverable | Source of truth |
|---|---|
| `nature_cooling.report` package: pure functions from a stored assessment (project name, label, input, result) to PDF bytes and XLSX bytes | ARCHITECTURE §2.1 (report builder), D-033 |
| 2-page PDF — page 1 summary: identity, both score cards with categories, flags, recommendation, per-block + overall confidence, version stamp; page 2 detail: the six output blocks with ranges and statuses, adjustment and suitability sub-scores, itemised assumptions, warnings, method note with the daytime-only and screening-level caveats | OQ-13/D-011; UX §6 ordering |
| XLSX workbook — sheets: Inputs (field, supplied value, applied default marker), Results (flattened blocks), Assumptions & Warnings; version stamps on every sheet | D-033 |
| `GET /api/projects/{id}/assessments/{aid}/report.pdf` and `…/report.xlsx` — render the **stored** result; 404 unknown ids, 409 for a draft without a result | D-033; OQ-15 |
| Frontend: enable the Export action as two downloads (PDF, XLSX) hitting those endpoints; no client-side rendering | UX §6 action row |

## Decided contracts (D-033 — implement, do not re-litigate)

1. **Toolchain:** `fpdf2` for PDF, `openpyxl` for XLSX — both pure Python
   and pip-installable, no system dependencies (the local-first install
   story stays one `pip install`). Added to the core dependencies: the
   report is a core deliverable (OQ-13), not an extra.
2. **Stored results only.** The report renders a stored `AssessmentResult`
   verbatim — the builder computes no score, band, level, or text, and never
   calls the engine. Rendering a draft is refused (409), exactly as
   evaluation-state rules are enforced elsewhere (D-029).
3. **Deterministic bytes.** Same stored assessment → byte-identical PDF and
   XLSX. Document metadata timestamps (PDF `CreationDate`, XLSX
   created/modified) are set from the assessment's `created_at`, never from
   the clock — the no-clock rule stays intact outside the storage layer.
4. **Typography:** the report embeds TTF builds of the same three
   self-hosted families the web app uses (OFL notice alongside), so the PDF
   is self-contained on any machine. English strings live in one module-level
   catalog in the report package, mirroring the frontend's catalog contract
   (translation without code change).
5. **Testing:** backend gates unchanged (`ruff`, strict `mypy`, `pytest` at
   100% coverage including the report package). PDF assertions run on
   extracted text and document structure (extraction via a dev-only
   dependency), never on pixels; plus a byte-determinism test for both
   formats. Frontend adds a contract test for the enabled Export action.

## Non-negotiable rules

1. **The engine is not touched; the API gains only the two report routes.**
   No methodology value moves without a version bump across `config/`, the
   Methodology Report, and the paper.
2. **No number originates in the report builder** — every figure, level,
   flag, recommendation, and assumption comes from the stored result or the
   stored input; status enums render through the catalog, as in the web app.
3. **The caveats are not optional.** Page 2 carries the daytime-only
   temperature caveat and the screening-level disclaimer (Methodology Report
   §8); suitability flags render prominently on page 1 (D-009).
4. **No AI attribution anywhere** — code, docs, commits. Sole author:
   Dimitris Kafetzis. Run the attribution grep before pushing.
5. **Dependency discipline:** backend adds exactly `fpdf2` and `openpyxl`
   (plus one dev-only PDF text-extraction library); the frontend adds
   nothing.

## Delivery

Conventional Commits, one coherent Phase 5 change set to `main`, CI green
(both jobs). Update: README roadmap (Phase 5 ✅, Phase 6 next) and the
running-locally section (report endpoints), decision-log entries for any new
decisions taken during implementation, backend package and frontend
`package.json` to 0.5.0, and a `v0.5.0` tag with a GitHub release on
completion.
