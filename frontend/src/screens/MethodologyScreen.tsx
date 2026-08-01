/**
 * The methodology browser (UX §8): a first-class section rendering the live
 * configuration — the same objects the engine scores with, served verbatim
 * by GET /api/methodology and GET /api/typologies, citations included. No
 * weight, band, factor, or typology value here comes from a constant.
 *
 * The effective final-score weights (D-007) are shown as the products of the
 * served weights with their derivation visible, so the disclosed
 * equity-forward weighting is inspectable without a hard-coded number.
 */

import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { MethodologyData, ScoreBand, Typology, TypologyLibrary } from '../api/types';
import { messages, optionLabel } from '../i18n/en';

const t = messages.methodology;

function SourceList({ sources }: { sources: { key: string; finding: string }[] }) {
  return (
    <ul className="source-list">
      {sources.map((source) => (
        <li key={`${source.key}-${source.finding.slice(0, 24)}`}>
          <span className="source-key">{source.key}</span> — {source.finding}
        </li>
      ))}
    </ul>
  );
}

function isSourceArray(value: unknown): value is { key: string; finding: string }[] {
  return (
    Array.isArray(value) &&
    value.every(
      (item) => typeof item === 'object' && item !== null && 'key' in item && 'finding' in item,
    )
  );
}

/** Renders any configuration subtree: numbers in mono, citations and rationale styled. */
function ConfigTree({ node }: { node: unknown }) {
  if (typeof node === 'string' || typeof node === 'number' || typeof node === 'boolean') {
    return <span className="config-value">{String(node)}</span>;
  }
  if (node === null || node === undefined || typeof node !== 'object') {
    return <span className="config-value">—</span>;
  }
  if (isSourceArray(node) && node.length > 0) {
    return <SourceList sources={node} />;
  }
  if (Array.isArray(node)) {
    return (
      <div className="config-tree">
        {(node as unknown[]).map((item, index) => (
          <div key={index}>
            <ConfigTree node={item} />
          </div>
        ))}
      </div>
    );
  }
  const entries = Object.entries(node as Record<string, unknown>).filter(
    ([key]) => key !== 'version',
  );
  return (
    <div className="config-tree">
      {entries.map(([key, value]) => {
        if (key === 'rationale' && typeof value === 'string') {
          return (
            <p key={key} className="rationale">
              {t.rationaleLabel}: {value}
            </p>
          );
        }
        if (key === 'sources' && isSourceArray(value)) {
          return <SourceList key={key} sources={value} />;
        }
        return (
          <div key={key}>
            <span className="config-key">{key}: </span>
            <ConfigTree node={value} />
          </div>
        );
      })}
    </div>
  );
}

function BandTable({ title, bands }: { title: string; bands: ScoreBand[] }) {
  return (
    <div>
      <h3>{title}</h3>
      <table className="data">
        <thead>
          <tr>
            <th scope="col">{t.bands.score}</th>
            <th scope="col">{t.bands.label}</th>
          </tr>
        </thead>
        <tbody>
          {bands.map((band) => (
            <tr key={band.label}>
              <td className="num">{t.bands.bandRange(band.min ?? null, band.max ?? null)}</td>
              <td>{optionLabel(band.label)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

interface EffectiveWeightRow {
  component: string;
  derivation: string;
  effective: number;
}

/**
 * The D-007 effective-weights table, derived transparently from the served
 * weights: the Heat Priority Index is decomposed into its two components,
 * so vulnerability's double contribution is visible. Every operand is shown.
 */
function effectiveWeights(weights: Record<string, unknown>): EffectiveWeightRow[] | null {
  const final = weights.final_opportunity_score;
  const hpi = weights.heat_priority_index;
  if (typeof final !== 'object' || final === null) return null;
  if (typeof hpi !== 'object' || hpi === null) return null;
  const finalW = final as Record<string, unknown>;
  const hpiW = hpi as Record<string, unknown>;
  const num = (value: unknown): number | null => (typeof value === 'number' ? value : null);

  const hpiWeight = num(finalW.heat_priority_index);
  const vulnDirect = num(finalW.vulnerability);
  const hpiHeat = num(hpiW.heat_exposure);
  const hpiVuln = num(hpiW.vulnerability);
  if (hpiWeight === null || vulnDirect === null || hpiHeat === null || hpiVuln === null) {
    return null;
  }

  const rows: EffectiveWeightRow[] = [
    {
      component: 'vulnerability',
      derivation: `${vulnDirect} + ${hpiWeight} × ${hpiVuln}`,
      effective: vulnDirect + hpiWeight * hpiVuln,
    },
    {
      component: 'heat_exposure',
      derivation: `${hpiWeight} × ${hpiHeat}`,
      effective: hpiWeight * hpiHeat,
    },
    ...Object.entries(finalW)
      .filter(
        ([key, value]) =>
          typeof value === 'number' && key !== 'heat_priority_index' && key !== 'vulnerability',
      )
      .map(([key, value]) => ({
        component: key,
        derivation: String(value),
        effective: value as number,
      })),
  ];
  return rows;
}

/** The library grouped by family, in the catalogue's own order (D-043). */
function familyGroups(entries: Typology[]): [string, Typology[]][] {
  const byFamily = new Map<string, Typology[]>();
  for (const entry of entries) {
    const bucket = byFamily.get(entry.family);
    if (bucket) bucket.push(entry);
    else byFamily.set(entry.family, [entry]);
  }
  const ordered = [...messages.families.order].filter((family) => byFamily.has(family));
  const extra = [...byFamily.keys()].filter((family) => !ordered.includes(family));
  return [...ordered, ...extra].map((family) => [family, byFamily.get(family) ?? []]);
}

function TypologyCard({ typology }: { typology: Typology }) {
  const s = typology.suitability;
  return (
    <div className="typology-detail">
      <h3 id={`typology-${typology.nbs_type}`}>{typology.display_name}</h3>
      <dl className="kv small">
        {/* D-044: every performance value below is the archetype's, and the
            page names the evidence class rather than implying the entry was
            measured on its own. */}
        <dt>{t.archetypeLabel}</dt>
        <dd>{typology.archetype_display_name}</dd>
        <dt>{t.typology.baseScore}</dt>
        <dd>{typology.base_cooling_score} / 100</dd>
        <dt>{t.typology.envelope}</dt>
        <dd>
          {typology.temp_reduction_min_c}–{typology.temp_reduction_max_c} °C
        </dd>
        <dt>{t.typology.evidence}</dt>
        <dd>{optionLabel(typology.evidence_confidence)}</dd>
        <dt>{t.typology.mechanism}</dt>
        <dd>{typology.primary_cooling_mechanism}</dd>
        <dt>{t.typology.energyApplicable}</dt>
        <dd>{typology.building_energy_applicable ? t.typology.yes : t.typology.no}</dd>
        <dt>{t.typology.context}</dt>
        <dd>{typology.typical_use_context.join(', ')}</dd>
        <dt>{t.suitability.minArea}</dt>
        <dd>
          {s.minimum_site_area_m2.toLocaleString()} m²
          {typology.suitability_inherited ? ` — ${t.inheritedSuitability}` : ''}
        </dd>
        <dt>{t.suitability.soil}</dt>
        <dd>{s.requires_soil === 'none' ? t.suitability.none : s.requires_soil}</dd>
        <dt>{t.suitability.irrigation}</dt>
        <dd>{s.requires_irrigation === 'none' ? t.suitability.none : s.requires_irrigation}</dd>
        <dt>{t.suitability.climate}</dt>
        <dd>
          {(s.unsuitable_climate_zones ?? []).length > 0
            ? (s.unsuitable_climate_zones ?? []).join(', ')
            : t.suitability.none}
        </dd>
        <dt>{t.typology.coBenefits}</dt>
        <dd>
          {Object.entries(typology.co_benefit_defaults)
            .map(([key, value]) => `${key}: ${value}`)
            .join(', ')}
        </dd>
      </dl>
      {(typology.output_caveats ?? []).length > 0 ? (
        <>
          <p className="small" style={{ marginTop: '0.5rem' }}>
            <strong>{t.typology.caveats}</strong>
          </p>
          <ul className="small">
            {(typology.output_caveats ?? []).map((caveat) => (
              <li key={caveat}>{caveat}</li>
            ))}
          </ul>
        </>
      ) : null}
      <p className="small">
        <strong>{t.typology.sources}</strong>
      </p>
      <SourceList sources={typology.sources} />
      {typology.notes ? <p className="rationale">{typology.notes}</p> : null}
    </div>
  );
}

const SECTION_IDS = [
  'scores',
  'weights',
  'typologies',
  'adjustment',
  'normalisation',
  'derived',
  'confidence',
  'energy',
  'countryDefaults',
  'recommendation',
] as const;

const SECTION_LABEL: Record<(typeof SECTION_IDS)[number], string> = {
  scores: t.sections.scores,
  weights: t.sections.weights,
  typologies: t.sections.typologies,
  adjustment: t.sections.adjustment,
  normalisation: t.sections.normalisation,
  derived: t.sections.derived,
  confidence: t.sections.confidence,
  energy: t.sections.energy,
  countryDefaults: t.sections.countryDefaults,
  recommendation: t.sections.recommendation,
};

export function MethodologyScreen() {
  const [methodology, setMethodology] = useState<MethodologyData | null>(null);
  const [library, setLibrary] = useState<TypologyLibrary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([api.methodology(), api.typologies()])
      .then(([meth, lib]) => {
        if (cancelled) return;
        setMethodology(meth);
        setLibrary(lib);
      })
      .catch(() => {
        if (!cancelled) setError(messages.app.apiError);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // Once loaded, honour a #fragment link from a results page.
  useEffect(() => {
    if (!methodology) return;
    const fragment = window.location.hash.slice(1);
    if (fragment) document.getElementById(fragment)?.scrollIntoView();
  }, [methodology]);

  if (error) return <p className="notice notice--error">{error}</p>;
  if (!methodology || !library) return <p className="muted">{messages.app.loading}</p>;

  const bands = methodology.derived_scores.score_bands ?? {};
  const effective = effectiveWeights(methodology.weights);
  const confidence = methodology.derived_scores.confidence;
  const derivedRest = Object.fromEntries(
    Object.entries(methodology.derived_scores).filter(
      ([key]) => key !== 'score_bands' && key !== 'confidence',
    ),
  );

  return (
    <div className="methodology">
      <nav className="methodology__toc" aria-label={t.heading}>
        {SECTION_IDS.map((id) => (
          <a key={id} href={`#${id}`}>
            {SECTION_LABEL[id]}
          </a>
        ))}
      </nav>

      <div className="methodology__content">
        <div>
          <h1>{t.heading}</h1>
          <p className="page-intro muted">{t.intro}</p>
          <p className="mono">{t.version(methodology.version)}</p>
        </div>

        <section id="scores" aria-label={t.sections.scores}>
          <h2>{t.sections.scores}</h2>
          {bands.heat_priority_index ? (
            <BandTable title={t.bands.heatPriority} bands={bands.heat_priority_index} />
          ) : null}
          {bands.opportunity ? (
            <BandTable title={t.bands.opportunity} bands={bands.opportunity} />
          ) : null}
        </section>

        <section id="weights" aria-label={t.sections.weights}>
          <h2>{t.sections.weights}</h2>
          <ConfigTree node={methodology.weights} />
          {effective ? (
            <>
              <h3>{t.sections.effectiveWeights}</h3>
              <p className="muted small">{t.effectiveWeightsNote}</p>
              <table className="data">
                <thead>
                  <tr>
                    <th scope="col">{t.effectiveWeightsColumns.component}</th>
                    <th scope="col">{t.effectiveWeightsColumns.derivation}</th>
                    <th scope="col">{t.effectiveWeightsColumns.effective}</th>
                  </tr>
                </thead>
                <tbody>
                  {effective.map((row) => (
                    <tr key={row.component}>
                      <td>{row.component}</td>
                      <td className="num">{row.derivation}</td>
                      <td className="num">
                        {row.effective.toLocaleString(undefined, { maximumFractionDigits: 4 })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          ) : null}
        </section>

        <section id="typologies" aria-label={t.sections.typologies}>
          <h2>{t.sections.typologies}</h2>
          {/* `resolved` is the flat scoring view the engine consumes and the
              only one carrying performance values; 110 entries are grouped by
              family so the page stays navigable (D-043). */}
          {familyGroups(library.resolved ?? []).map(([family, entries]) => (
            <details className="collapsible" key={family}>
              <summary>
                {messages.families.labels[family] ?? family}{' '}
                <span className="muted small">· {t.familyCount(entries.length)}</span>
              </summary>
              {entries.map((typology) => (
                <TypologyCard key={typology.nbs_type} typology={typology} />
              ))}
            </details>
          ))}
        </section>

        <section id="adjustment" aria-label={t.sections.adjustment}>
          <h2>{t.sections.adjustment}</h2>
          <ConfigTree node={methodology.adjustment_factors} />
        </section>

        <section id="normalisation" aria-label={t.sections.normalisation}>
          <h2>{t.sections.normalisation}</h2>
          <ConfigTree node={methodology.input_mapping} />
        </section>

        <section id="derived" aria-label={t.sections.derived}>
          <h2>{t.sections.derived}</h2>
          <ConfigTree node={derivedRest} />
        </section>

        <section id="confidence" aria-label={t.sections.confidence}>
          <h2>{t.sections.confidence}</h2>
          <ConfigTree node={confidence ?? null} />
        </section>

        <section id="energy" aria-label={t.sections.energy}>
          <h2>{t.sections.energy}</h2>
          <ConfigTree node={methodology.energy_model} />
        </section>

        <section id="countryDefaults" aria-label={t.sections.countryDefaults}>
          <h2>{t.sections.countryDefaults}</h2>
          <ConfigTree node={methodology.country_defaults} />
        </section>

        <section id="recommendation" aria-label={t.sections.recommendation}>
          <h2>{t.sections.recommendation}</h2>
          <ConfigTree node={methodology.recommendation_templates} />
        </section>
      </div>
    </div>
  );
}
