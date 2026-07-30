# UX Specification — Questionnaire and Results

The interaction design for the v1 web application. Companion to [ARCHITECTURE.md](ARCHITECTURE.md) (how it is built) and [methodology/METHODOLOGY.md](methodology/METHODOLOGY.md) (what the numbers mean). Decisions D-018 to D-021 in [DECISIONS.md](DECISIONS.md) record the choices this document implements.

## 1. Design premise

The methodology requires about 45 inputs, roughly 20 of them mandatory. Reducing that count would not reduce uncertainty — it would only move uncertainty from *visible* (a stated confidence level) to *invisible* (a silent default). The interface therefore takes the opposite approach:

> **Ask everything. Make skipping free and honest. Show the user exactly what skipping costs.**

Three consequences follow, and they drive every screen below: missing answers must never feel like failure; the cost of a gap must be visible while the user can still act on it; and the tool must never appear to know something the user did not tell it.

**Visual register.** The interface reads as a scientific instrument, not a lifestyle app: generous whitespace, one accent colour reserved for scores and decisions, score cards rather than dashboards, no decorative motion. Design tokens come from criterra.eu (paper `#eaebe2`, ink `#16231c`, brand green `#2e6a4e`; Newsreader / Hanken Grotesk / IBM Plex Mono, self-hosted). WCAG AA throughout; `prefers-reduced-motion` respected.

## 2. Entry

The landing screen states what the tool does, what it will ask for, and how long it takes, before requesting anything. It also says plainly that partial answers are acceptable — abandonment is driven more by unset expectations than by form length.

It offers two actions: **Start a new assessment** and **Open a saved project**. The methodology is linked from here and from every subsequent screen; a user must never have to leave the flow to find out how a number is produced.

## 3. The six steps

A single guided flow (D-018). No quick/full mode split: the confidence meter already lets users choose their own depth.

| Step | Group | Notes |
|---|---|---|
| 1 | Project information | Identity and context; shortest step, establishes momentum |
| 2 | Site characteristics | The heaviest step; area, cover, land use, users, soil, irrigation |
| 3 | Climate and heat exposure | Climate zone required; measured values optional |
| 4 | Vulnerability and equity | Social context |
| 5 | NbS intervention | The guided typology picker (§5) |
| 6 | Cost and energy | Entirely optional; gated by an explicit "do you have cost data?" |

Persistent throughout: a step indicator, the live confidence panel (§4), and **Back** / **Continue**. Work auto-saves as the user progresses (D-020); a closed tab loses nothing.

**Validation.** Errors block progression *within their step* and appear inline next to the field. Warnings — intervention area exceeding site area, cover percentages summing above 105% — appear inline and never block. There is no third severity level; the confidence rating already conveys input quality.

## 4. The confidence panel

Every step header carries live per-block confidence (cooling / energy / economic / equity), updating as answers are entered:

```
Cooling confidence   ████████░░  Medium
   → Adding existing tree canopy % would raise this to High

Economic confidence  ██░░░░░░░░  Low
   → Requires cost data (step 6)
```

Two behaviours make this work rather than nag:

- **It names the single highest-value missing field.** The user sees precisely which answer buys the most confidence and decides whether it is worth finding out — the tool assists rather than demands.
- **It shows blocks independently.** A user with no interest in payback can skip the entire economic block knowingly, without feeling the assessment is degraded overall.

Where a typology's evidence confidence caps a block (green façade, rain garden/bioswale, courtyard greening — see Methodology Report §6.2), the panel says so: *"Cooling confidence is capped at Medium because published evidence for this typology is limited."* Complete inputs cannot compensate for thin evidence, and the interface must not imply otherwise.

## 5. The guided typology picker

The specification's ordering collects site data before intervention choice. Left alone, that means a user who picks riparian restoration for a site with no water discovers the problem at the results screen, after 40 questions — the worst possible moment.

The fix is not to reorder the questions but to make the picker context-aware. By step 5 the tool knows the site, so all 14 cards render sorted by fit and annotated (D-019):

```
┌──────────────────────────────┬──────────────────────────────┐
│ ✓ Urban forest               │ ✓ Street tree planting       │
│   Well suited to this site   │   Well suited to this site   │
│   Strong cooling 1.0–3.0 °C  │   Strong cooling 0.5–3.0 °C  │
│   Evidence: high             │   Evidence: high             │
├──────────────────────────────┼──────────────────────────────┤
│ ! Green façade               │ ✕ Riparian restoration       │
│   Needs reliable irrigation  │   No water feature on site   │
│   Evidence: limited          │   Not suitable — selectable  │
└──────────────────────────────┴──────────────────────────────┘
```

Each card shows fit, the literature cooling envelope, and evidence confidence — the three things that should drive the choice. Unsuitable typologies stay fully selectable: a user deliberately testing a hypothesis must not be overridden, and the flag follows through to results and the report.

Selecting a card reveals its sizing fields (intervention area, canopy at maturity, maturity period, maintenance, complexity — the schema's intervention group, per D-031).

## 6. Results

A single scrolling page, ordered by decreasing decision relevance:

1. **Two score cards** — Heat Priority Index and NbS Cooling Opportunity Score, each with its category and confidence.
2. **Flags**, where present — suitability warnings first, then evidence-confidence caveats (green roofs benefit the building rather than the street; blue typologies in humid climates), then any low overall confidence.
3. **The recommendation** — deterministic composed text (no language model).
4. **The six output blocks** — cooling, energy and GHG, economic, equity and co-benefits, each with its own confidence badge and each showing ranges, never point estimates. Blocks that could not be calculated say why: *"Capital cost not estimated — no cost data supplied. This tool ships no default cost values."*
5. **Assumptions applied** — every default the engine used, itemised.
6. **Method note and limitations**, including the daytime-only caveat.
7. **Actions** — export report, compare another option, return to projects.

Every score links to its formula and sources in the methodology browser. A user who wants to know why a number is what it is is two clicks from the evidence.

## 7. Comparison

**Compare another option** carries the entire site description forward and re-asks only the intervention step, plus cost/energy where used — about 9 questions rather than 45 (D-021). Site conditions belong to the place, not the option; re-asking would be tedious and would introduce inconsistency between variants that the comparison exists to isolate.

The comparison view places options side by side, highlights differences rather than repeating identical rows, and carries each option's own suitability flags and confidence. The winning option is never announced: the tool presents the axes and the decision belongs to the user. v1 supports intervention comparison within one site; multi-site portfolio ranking is v2 ([V2-VISION.md](V2-VISION.md)).

## 8. Methodology browser

A first-class section, not a help page. It renders the live configuration — formulas, weights, typology library with citations, adjustment rules, the effective-weights table including the disclosed equity-forward weighting — with the methodology version stamped. Every claim in the interface traces here, and this page traces to the Methodology Report and the published literature.

## 9. Accessibility and language

WCAG AA; full keyboard operability; visible focus states; form errors associated with their fields programmatically, not by colour alone; `prefers-reduced-motion` honoured for the confidence meter and any transitions. English UI in v1; all user-facing strings externalised so translation does not require code changes (multilingual UI is v2).
