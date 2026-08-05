# Methodology Paper (LaTeX)

The Nature for Cooling Rapid Assessment Tool methodology, written as a
standalone, publication-quality scientific paper for expert review — the
document to send to UNEP, independent scientific reviewers, and public
authorities.

**Methodology version:** `2026.08.05` · **Licence:** Apache-2.0 · **Author:** Criterra

This paper is the expanded, citable form of
[`docs/methodology/METHODOLOGY.md`](../docs/methodology/METHODOLOGY.md). It is
kept in lock-step with that document, with
[`docs/methodology/EVIDENCE-TABLES.md`](../docs/methodology/EVIDENCE-TABLES.md),
with [`docs/methodology/BIBLIOGRAPHY.md`](../docs/methodology/BIBLIOGRAPHY.md),
and with the configuration in [`config/`](../config/). A change to any
methodology value requires updating all of them together and bumping the
version stamp.

## How to cite

> Criterra (2026). *The Nature for Cooling Rapid Assessment Tool: a transparent,
> evidence-grounded screening methodology for prioritising nature-based solutions
> for urban cooling.* Methodology Report, version 2026.08.05.
> https://github.com/Dimitrios-Kafetzis/CriterraNatureCoolingTool

```bibtex
@techreport{criterra2026naturecooling,
  author      = {{Criterra}},
  title       = {The Nature for Cooling Rapid Assessment Tool: a transparent,
                 evidence-grounded screening methodology for prioritising
                 nature-based solutions for urban cooling},
  type        = {Methodology Report},
  institution = {Criterra},
  year        = {2026},
  version     = {2026.08.05},
  url         = {https://github.com/Dimitrios-Kafetzis/CriterraNatureCoolingTool},
}
```

Quote the methodology version with any score taken from the tool: the same site
may score differently under a later version.

## Contact

Questions, corrections, and methodology challenges are handled openly as issues
at [the repository issue tracker](https://github.com/Dimitrios-Kafetzis/CriterraNatureCoolingTool/issues),
so that critique and its resolution stay part of the public record. Section 13
of the paper describes what a well-formed challenge looks like.

## Building

Requires a TeX distribution with `latexmk` and `biber` (TeX Live 2023 or later;
`texlive-full` on Debian/Ubuntu covers everything used here).

```sh
make            # build Criterra_NatureCoolingTool_MethodologyReport.pdf
make watch      # rebuild continuously on change
make clean      # remove build artefacts, keep the PDF
make distclean  # remove build artefacts and the PDF
```

Or directly:

```sh
latexmk -pdf main.tex
```

The current build produces a 111-page PDF with no LaTeX errors, no warnings, and
no overfull boxes.

## Layout

```
paper/
├── main.tex           Preamble, package setup, document assembly
├── references.bib     BibTeX with DOIs; keys match BIBLIOGRAPHY.md
├── sections/          One file per major section
│   ├── titlepage.tex        Title page, licence, openness statement
│   ├── abstract.tex
│   ├── introduction.tex     Urban heat, NbS, the decision gap
│   ├── scope.tex            What the tool is and is not; design commitments
│   ├── related-work.tex     Positioning; how a screening tool should be judged
│   ├── framework.tex        Three-layer structure
│   ├── inputs.tex           Inputs, normalisation, the LST proxy caution
│   ├── typologies.tex       The archetype library: 110 entries over 18 classes
│   ├── formulas.tex         Every scoring formula and weight
│   ├── uncertainty.tex      Ranges, branched confidence, missing data
│   ├── sensitivity.tex      Design and the results, re-confirmed at 2026.08.05
│   ├── implementation.tex   Config-as-data, machine-enforced evidence rules
│   ├── worked-example.tex   One hand-computed illustrative assessment
│   ├── limitations.tex      Limitations and misuse cases
│   ├── governance.tex       Versioning and how to challenge the methodology
│   ├── conclusion.tex
│   └── appendices.tex       A–E: archetypes and entries, weights, fields,
│                            glossary, source verification register
├── figures/           TikZ / pgfplots sources (all vector, no raster)
│   ├── three-layer-framework.tex
│   ├── data-flow.tex
│   ├── cooling-evidence.tex     Per-measure comparison from keravec2026
│   ├── climate-dependence.tex   Climate-subzone spread
│   └── envelope-clipping.tex    The envelope clipping rule
├── Makefile
├── .latexmkrc
└── .gitignore
```

## Editing conventions

- **Never invent a citation, DOI, page number, or quantitative finding.** Every
  reference comes from `BIBLIOGRAPHY.md`. Author names are reproduced with
  initials exactly as recorded there; initials are not expanded, because the
  expansions were not part of what was verified.
- **Respect the verification status.** Appendix E reproduces the register from
  `BIBLIOGRAPHY.md`. Sources verified as *metadata + finding (secondary)* must
  not be presented as full-text readings.
- **Distinguish the metrics.** Air temperature, land surface temperature, and
  thermal comfort indices (PET/UTCI) are different quantities. The methodology
  reports daytime pedestrian-level **air temperature** only. Every figure quoted
  from a source carries its metric.
- **Do not soften the limitations.** The daytime-only restriction, the
  air-temperature-only scope, the geographic skew of the evidence base, the
  modelling bias, the absence of default costs, and the contestability of the
  weights are deliberate disclosures.
- **Sensitivity analysis is reported, and its published design is fixed.** The
  design was published before the engine existed and has not been altered. The
  results are regenerated from `docs/methodology/SENSITIVITY-ANALYSIS.md`
  whenever the scenario set or any aggregation weight moves, and every figure
  in the paper must match that file.
- **An entry carries no performance value.** Envelopes, base scores, evidence
  ratings, suitability conditions, and co-benefit defaults belong to the
  archetype. Anything the paper attributes to a catalogue entry must be
  identity, family, availability, or its primary cooling mechanism.
- **All units via `siunitx`**, all figures vector (TikZ/pgfplots), all tables
  `booktabs` with no vertical rules.

## Cross-reference macros

| Macro | Renders |
|---|---|
| `\methver` | the methodology version, `2026.08.05` |
| `\prevver` | the previous methodology version, `2026.08.04` |
| `\tool` / `\Tool` | "the Nature for Cooling Rapid Assessment Tool" |
| `\repourl` | the repository URL |
| `\clamp{x}` | $\mathrm{clamp}(x)$, bounding to 0–100 |
| `\clip{x}{l}{u}` | $\mathrm{clip}(x, l, u)$, bounding to an envelope |
| `\dT` | $\Delta T$ |
| `\fieldname{...}` | a `snake_case` config field, breakable at underscores |
| `keynote` environment | a boxed note the reader must not skip |

## Known gaps recorded in the paper

The three specification gaps disclosed at version `2026.07.30` — the
input-to-sub-indicator rules, the cost-feasibility derivation, and the
confidence field-to-block mapping — were closed at `2026.08.01`. One gap
remains, and the paper states it in the limitations section:

- The country emission factor table ships **empty**, so greenhouse-gas outputs
  report *not calculated* unless a deployment supplies its own factor.

Two disclosures that are design choices rather than gaps are also carried in
the paper: the Equity Score is computed and reported but does not enter the
final aggregation, and an entry's cooling range is its archetype's, so the tool
does not discriminate on cooling between two entries inheriting the same
evidence class.
