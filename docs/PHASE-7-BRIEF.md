# Phase 7 Brief — v1.0 Stabilisation: External Review & Hardening

The implementation brief for Phase 7, fixed at the close of Phase 6 so that
the road to `v1.0.0` is implemented against settled decisions rather than
re-designed. Companion to [DECISIONS.md](DECISIONS.md) (D-037 records the
scope decisions) and [V2-VISION.md](V2-VISION.md) (everything this phase
deliberately does not start).

## Starting state

Phases 0–6 are complete at `v0.6.0`, methodology `2026.08.02` — the original
roadmap table is finished:

- The packaged app works end to end from one `pip install` and one command;
  the container image is public on GHCR; the documentation site publishes
  the full corpus; `vX.Y.Z` tags release every artefact automatically.
- The methodology has been reviewable by design since Phase 1 (D-012), but
  no external reviewer has yet been through it.
- Known cosmetic debt: the D-034 frontend catalog defect (the shared
  `statuses.not_estimated` wording says "requires cost data" for two cooling
  outputs whose missing inputs are intervention sizing, not cost).

## Scope (D-037 — approved selection)

| Deliverable | Realises |
|---|---|
| External methodology review round: review package, critique intake, findings triage | D-012 (the methodology exists to be reviewed) |
| Hardening & polish: WCAG AA pass, packaged-app UX polish, D-034 catalog defect | ARCHITECTURE §3 (the stated AA promise), D-034 |
| `v1.0.0` released time-boxed, with the versioning rules across 1.0 fixed | D-037 |

**Explicitly out of scope:** PyPI publication (deferred, not rejected —
distribution remains the GitHub release wheel and the GHCR image); every
V2 capability (portfolio mode, GIS workflow, funder view, institutional
deployment, planting guidance); any strict review-gated release criterion.

## Decided contracts (D-037 — implement, do not re-litigate)

1. **The review package is the existing corpus, not a new document.** What
   reviewers receive is the paper PDF and the Methodology Report as
   versioned in-repo (D-012), plus the published documentation site.
   Outreach (UNEP, external reviewers) is the author's action; the phase's
   repository work is the intake and triage machinery, not the sending.
2. **Critique intake is structured.** A GitHub issue template for
   methodology critique asking for the Methodology Report section, the
   claim challenged, and supporting literature — mirroring the standing
   invitation in CONTRIBUTING.md. Findings triage into: **methodology-
   blocking** (configuration/report change, version bump, D-017 evidence
   gates apply), **clarification** (report/docs wording, no version bump),
   or **declined** (recorded with rationale in the decision log). Every
   accepted methodology change follows the existing evidence rules; nothing
   about D-017 loosens.
3. **The hardening set is bounded.** (a) An accessibility pass verifying the
   web app against WCAG AA — the promise ARCHITECTURE §3 already makes —
   fixing what fails it; (b) packaged-app UX polish limited to defects and
   friction found by using the packaged app, not feature work; (c) the
   D-034 catalog defect corrected the way the report catalog already
   corrected it: the two sizing-dependent cooling outputs get neutral,
   accurate wording, split from the cost-dependent statuses.
4. **`v1.0.0` is time-boxed, not review-gated.** It ships when the
   hardening set lands. Review findings are handled as they arrive; a
   methodology change accepted after `v1.0.0` is an ordinary versioned
   release, exactly as OQ-15/D-011 already provide. Package semver and the
   date-stamped methodology version remain independent; `v1.0.0` asserts
   product stability, not methodological finality.

## Non-negotiable rules (carried forward)

1. Engine purity, determinism, and the D-017 evidence gates are untouched;
   methodology changes only through the review-triage path with version
   bumps.
2. The frontend adds no runtime dependency; backend runtime dependencies
   unchanged.
3. All gates stay green at 100% coverage; the same-origin model (D-030) and
   the one-source-of-truth rules (D-028/D-035) stand.
4. No AI attribution anywhere — code, docs, commits. Sole author:
   Dimitris Kafetzis. Run the attribution grep before pushing.

## Delivery

Conventional Commits, coherent change sets to `main`, CI green. README
roadmap gains and closes the Phase 7 row; decision-log entries recorded
(D-037 + implementation rulings if needed); backend package and frontend
`package.json` to 1.0.0; tag `v1.0.0` with the full packaged release. Close
the phase by proposing what follows v1.0 — the natural candidates are the
V2 waves (V2-VISION sequencing: portfolio mode + funder view first) and
PyPI publication — with decision entries, for approval.
