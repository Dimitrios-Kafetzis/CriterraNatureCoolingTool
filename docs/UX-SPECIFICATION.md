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

## 3. The steps: an optional map, then six question groups

A single guided flow (D-018). No quick/full mode split: the confidence meter already lets users choose their own depth. Since v2.1 the flow opens with a map step (D-047), skippable in one action, that can fill in exactly three answers — site area, country, climate zone — each marked as autofilled and never overwriting an answer already given (D-047.2). The wizard therefore shows seven steps; the six question groups are unchanged.

| Step | Group | Notes |
|---|---|---|
| 1 | Find the site on a map | Optional and skippable in one action (D-047); place search moves the map and fills in nothing (D-049.6) |
| 2 | Project information | Identity and context; shortest step, establishes momentum |
| 3 | Site characteristics | The heaviest step; area, cover, land use, users, soil, irrigation, and the four availability answers (§3.1) |
| 4 | Climate and heat exposure | Climate zone required; measured values optional |
| 5 | Vulnerability and equity | Social context |
| 6 | NbS intervention | The guided typology picker (§5) |
| 7 | Cost and energy | Entirely optional; gated by an explicit "do you have cost data?" |

### 3.1 The four availability answers, and the promise the interface must keep

The site-characteristics step asks four questions that decide **which interventions the tool offers** and feed **no score** (D-044.1): whether the site includes a railway, whether it already carries woodland, what kind of waterfront it adjoins, and who could deliver a productive landscape there.

Their explanations must say so plainly. The tool's premise is that a user can see what skipping a question costs (§4), and a question that cannot move a number has to admit it — otherwise the interface implies an influence the methodology denies. Each explanation therefore ends with the same statement in the same terms: *"It feeds no score. Your answer cannot raise or lower any result."*

The governance question is a multi-select, and its help text carries a second promise that is easy to get backwards: **leaving it blank hides nothing.** An unanswered question is not evidence that no one could deliver, so every productive option stays on offer until the user narrows it (D-043.3). Copy that read "leave unticked if none could" would tell the user the opposite of what the system does.

Persistent throughout: a step indicator, the live confidence panel (§4), and **Back** / **Continue**. Work auto-saves as the user progresses (D-020); a closed tab loses nothing.

**Validation.** Errors block progression *within their step* and appear inline next to the field. Warnings — intervention area exceeding site area, cover percentages summing above 105% — appear inline and never block. There is no third severity level; the confidence rating already conveys input quality.

## 4. The confidence panel

Every step header carries live per-block confidence (cooling / energy / economic / equity), updating as answers are entered:

```
Cooling confidence   ████████░░  Medium
   → Adding existing tree canopy % would raise this to High

Economic confidence  ██░░░░░░░░  Low
   → Requires cost data (the cost step)
```

Two behaviours make this work rather than nag:

- **It names the single highest-value missing field.** The user sees precisely which answer buys the most confidence and decides whether it is worth finding out — the tool assists rather than demands.
- **It shows blocks independently.** A user with no interest in payback can skip the entire economic block knowingly, without feeling the assessment is degraded overall.

Where an entry's inherited evidence class caps a block (green façade / living wall, bioretention, enclosed courtyard, vegetated shade structure, and both productive classes — see Methodology Report §6.2), the panel says so: *"Cooling confidence is capped at Medium because published evidence for this typology is limited."* Complete inputs cannot compensate for thin evidence, and the interface must not imply otherwise.

## 5. The guided typology picker

The specification's ordering collects site data before intervention choice. Left alone, that means a user who picks riparian restoration for a site with no water discovers the problem at the results screen, after 40 questions — the worst possible moment.

The fix is not to reorder the questions but to make the picker context-aware. By the intervention step the tool knows the site, so the cards render sorted by fit and annotated (D-019).

**From v2.0 the picker also has to survive its own catalogue.** The library holds 110 entries across fourteen families, and a school site is offered 67 of them; a flat list of cards is not something anyone will read. Regrouping is therefore a functional requirement of this release, not polish. The picker groups by family, filters by name, and supports selecting several entries as a package (D-038):

```
Your package (2)                                     ⚠ nothing above 5
  1. Tree Avenue                                           [remove]
  2. Rain garden                                           [remove]

Search  [ tree                                    ]  [clear]

Offered for this site — 67 entries
  ▾ Tree-based elements (13 · elements)
    ┌──────────────────────────────┬──────────────────────────────┐
    │ ✓ Tree grove            [✓]  │ ✓ Strategic individual tree  │
    │   Well suited to this site   │   Well suited to this site   │
    │   1.0–3.0 °C · Evidence high │   0.5–3.0 °C · Evidence high │
    │   Dense tree canopy          │   Street tree canopy         │
    └──────────────────────────────┴──────────────────────────────┘
  ▸ Park scale (9 · composites)
  ▸ Water landscape (12 · composites)

Not offered for this site — still selectable
  ▸ Woodland & forest (2)   restoration types need existing woodland
```

Each card shows fit, the literature cooling envelope, evidence confidence, **and the evidence class its numbers are inherited from** — under the archetype model an entry inherits a *cited* envelope, and the interface must say which one rather than implying solution-specific evidence that does not exist.

Two rules the picker must not break. **Availability is asked, never computed**: `GET /api/typologies/available` says what suits this site and the picker renders that answer; no gating rule originates in the frontend (ARCHITECTURE boundary 1). And **availability guides, it never blocks** (D-019): entries the matrix does not offer sit in a separate, de-emphasised, labelled section and stay fully selectable, because a professional deliberately testing a hypothesis must not be overridden. The flag follows through to results and the report.

At city and district scale the copy changes: those scales compose a package rather than choosing one option (D-043.2), so their short menus are correct by construction rather than a defect. Above five components the picker states plainly that adding another will not raise the temperature estimate — it adds co-benefit breadth and cost only (D-044.4).

Selecting a card reveals its sizing fields (intervention area, canopy at maturity, maturity period, maintenance, complexity — the schema's intervention group, per D-031).

## 6. Results

A single scrolling page, ordered by decreasing decision relevance:

1. **Two score cards** — Heat Priority Index and NbS Cooling Opportunity Score, each with its category and confidence.
2. **Flags**, where present — suitability warnings first, then evidence-confidence caveats (green roofs benefit the building rather than the street; blue typologies in humid climates), then any low overall confidence.
3. **The recommendation** — deterministic composed text (no language model).
4. **The six output blocks** — cooling, energy and GHG, economic, equity and co-benefits, each with its own confidence badge and each showing ranges, never point estimates. Blocks that could not be calculated say why: *"Capital cost not estimated — no cost data supplied. This tool ships no default cost values."*
5. **The package**, where more than one intervention was proposed — every component itemised with its own cooling range, evidence class, evidence confidence and suitability, with the component carrying the headline temperature marked. The combination rules are rendered **verbatim from the result**, not restated in interface language, so the report and the screen cannot drift into describing different arithmetic. A single intervention renders no package section and looks exactly as it always has.
6. **Assumptions applied** — every default the engine used, itemised.
7. **Method note and limitations**, including the daytime-only caveat.
8. **Actions** — export report, compare another option, return to projects.

Every score links to its formula and sources in the methodology browser. A user who wants to know why a number is what it is is two clicks from the evidence.

## 7. Comparison

**Compare another option** carries the entire site description forward and re-asks only the intervention step, plus cost/energy where used — about 9 questions rather than 45 (D-021). Site conditions belong to the place, not the option; re-asking would be tedious and would introduce inconsistency between variants that the comparison exists to isolate.

The comparison view places options side by side, highlights differences rather than repeating identical rows, and carries each option's own suitability flags and confidence. The winning option is never announced: the tool presents the axes and the decision belongs to the user. v1 supports intervention comparison within one site; multi-site portfolio ranking is v2 ([V2-VISION.md](V2-VISION.md)).

## 8. Methodology browser

A first-class section, not a help page. It renders the live configuration — formulas, weights, typology library with citations, adjustment rules, the effective-weights table including the disclosed equity-forward weighting — with the methodology version stamped. Every claim in the interface traces here, and this page traces to the Methodology Report and the published literature.

## 9. Accessibility and language

WCAG AA; full keyboard operability; visible focus states; form errors associated with their fields programmatically, not by colour alone; `prefers-reduced-motion` honoured for the confidence meter and any transitions. English UI in v1; all user-facing strings externalised so translation does not require code changes (multilingual UI is v2).
