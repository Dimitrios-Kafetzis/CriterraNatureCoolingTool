/**
 * The results dashboard (UX §6): a single scrolling page ordered by
 * decreasing decision relevance. Every figure, category, level, flag,
 * recommendation, assumption, and method note renders verbatim from the
 * stored AssessmentResult — computed once by the engine, never recomputed
 * (OQ-15) and never re-derived here (ARCHITECTURE boundary 3).
 */

import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router';
import { api } from '../api/client';
import { storedResult } from '../api/types';
import type {
  AssessmentResult,
  AssessmentView,
  ComponentBlock,
  ConfidenceLevel,
} from '../api/types';
import { messages, optionLabel } from '../i18n/en';

const t = messages.results;

function fmt(value: number): string {
  return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

function ConfidenceBadge({ level }: { level: ConfidenceLevel }) {
  return <span className="badge">{t.confidenceBadge(optionLabel(level))}</span>;
}

function FormulaLink({ anchor }: { anchor: string }) {
  return (
    <Link className="small" to={`/methodology#${anchor}`}>
      {t.formulaLink}
    </Link>
  );
}

export function ResultsScreen() {
  const { projectId, assessmentId } = useParams<'projectId' | 'assessmentId'>();
  const navigate = useNavigate();
  const [assessment, setAssessment] = useState<AssessmentView | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId || !assessmentId) return;
    let cancelled = false;
    api
      .getAssessment(projectId, assessmentId)
      .then((view) => {
        if (!cancelled) setAssessment(view);
      })
      .catch(() => {
        if (!cancelled) setError(messages.app.apiError);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, assessmentId]);

  if (error) return <p className="notice notice--error">{error}</p>;
  if (!assessment || !projectId || !assessmentId) {
    return <p className="muted">{messages.app.loading}</p>;
  }

  const result = storedResult(assessment);
  if (!result) {
    return (
      <div>
        <p className="notice">{t.draftNotice}</p>
        <Link className="button" to={`/projects/${projectId}/assessments/${assessmentId}/edit`}>
          {t.continueDraft}
        </Link>
      </div>
    );
  }

  async function compareAnother() {
    const created = await api.duplicateAssessment(projectId ?? '', assessmentId ?? '');
    void navigate(`/projects/${projectId}/assessments/${created.assessment_id}/edit?step=5`);
  }

  const confidence = result.confidence;
  const flags: { key: string; text: string; kind: 'error' | 'warn' }[] = [
    ...result.suitability.flags.map((flag) => ({
      key: flag.code,
      text: flag.message,
      kind: 'error' as const,
    })),
    ...(confidence.cooling_capped_by_evidence
      ? [{ key: 'evidence-cap', text: messages.confidence.evidenceCap, kind: 'warn' as const }]
      : []),
    ...(confidence.overall === 'low'
      ? [{ key: 'low-overall', text: t.lowOverallConfidence, kind: 'warn' as const }]
      : []),
  ];

  return (
    <div className="results">
      <div>
        <p className="muted small">
          {assessment.label} ·{' '}
          {result.package.component_count > 1
            ? result.components.map((component) => component.typology.display_name).join(' + ')
            : result.typology.display_name}
        </p>
        <h1>{t.heading}</h1>
        {assessment.methodology_update_available ? (
          <p className="notice notice--warn">{t.methodologyUpdateAvailable}</p>
        ) : null}
      </div>

      {/* 1 — the two score cards */}
      <div className="score-cards">
        <section className="card" aria-label={t.heatPriority}>
          <h3>{t.heatPriority}</h3>
          <div className="score-card__value">{fmt(result.heat_priority.score)}</div>
          <div className="score-card__scale">{t.heatPriorityScale}</div>
          <p className="score-card__category">
            {optionLabel(result.heat_priority.category)}{' '}
            <ConfidenceBadge level={confidence.overall} />
          </p>
          <dl className="kv small">
            <dt>
              {t.subScores.heatExposure} ({t.subScores.heatExposurePath[result.heat_exposure.path]})
            </dt>
            <dd>{fmt(result.heat_exposure.score)}</dd>
            <dt>{t.subScores.vulnerability}</dt>
            <dd>{fmt(result.vulnerability.score)}</dd>
          </dl>
          <FormulaLink anchor="scores" />
        </section>
        <section className="card" aria-label={t.opportunity}>
          <h3>{t.opportunity}</h3>
          <div className="score-card__value">{fmt(result.opportunity.score)}</div>
          <div className="score-card__scale">{t.opportunityScale}</div>
          <p className="score-card__category">
            {optionLabel(result.opportunity.category)}{' '}
            <ConfidenceBadge level={confidence.overall} />
          </p>
          <details className="collapsible">
            <summary>{t.opportunityComponents.heading}</summary>
            <table className="data">
              <thead>
                <tr>
                  <th scope="col">{t.opportunityComponents.component}</th>
                  <th scope="col">{t.opportunityComponents.score}</th>
                  <th scope="col">{t.opportunityComponents.nominalWeight}</th>
                  <th scope="col">{t.opportunityComponents.appliedWeight}</th>
                </tr>
              </thead>
              <tbody>
                {result.opportunity.components.map((component) => (
                  <tr key={component.name}>
                    <td>{component.name}</td>
                    <td className="num">{fmt(component.score)}</td>
                    <td className="num">{fmt(component.nominal_weight)}</td>
                    <td className="num">{fmt(component.applied_weight)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {result.opportunity.excluded_components.length > 0 ? (
              <p className="muted small">
                {t.opportunityComponents.excluded(
                  result.opportunity.excluded_components.join(', '),
                )}
              </p>
            ) : null}
          </details>
          <FormulaLink anchor="weights" />
        </section>
      </div>

      {/* 2 — flags */}
      {flags.length > 0 ? (
        <section aria-label={t.flagsHeading}>
          <h2>{t.flagsHeading}</h2>
          {flags.map((flag) => (
            <p key={flag.key} className={`notice notice--${flag.kind}`}>
              {flag.text}
            </p>
          ))}
        </section>
      ) : null}

      {/* 3 — the recommendation */}
      <section className="card" aria-label={t.recommendationHeading}>
        <h2>{t.recommendationHeading}</h2>
        <p className="recommendation">{result.recommendation}</p>
      </section>

      {/* 3b — the package, itemised (D-038). A single-intervention
          assessment is a package of one and renders nothing here. */}
      <PackageSection result={result} />

      {/* 4 — the output blocks */}
      <section className="card">
        <div className="result-block__head">
          <h3>{t.blocks.cooling}</h3>
          <ConfidenceBadge level={confidence.cooling} />
          <FormulaLink anchor="typologies" />
        </div>
        <p className="muted small">
          {t.packageSection.inheritedNote(result.typology.archetype_display_name)}
        </p>
        <dl className="kv">
          <dt>{t.cooling.potential}</dt>
          <dd>{fmt(result.cooling.potential_score)} / 100</dd>
          <dt>{t.cooling.deltaT}</dt>
          <dd>
            {fmt(result.cooling.delta_t_min_c)}–{fmt(result.cooling.delta_t_max_c)} °C
          </dd>
          <dt>{t.cooling.heatIndexImprovement}</dt>
          <dd>{optionLabel(result.cooling.heat_index_improvement)}</dd>
          <dt>{t.cooling.shadePotential}</dt>
          <dd>
            {result.cooling.shade_potential_status === 'calculated' &&
            result.cooling.shade_potential_percent != null
              ? `${fmt(result.cooling.shade_potential_percent)} %`
              : t.cooling.notEstimated}
          </dd>
          <dt>{t.cooling.timeToBenefit}</dt>
          <dd>
            {result.cooling.time_to_benefit_status === 'derived' && result.cooling.time_to_benefit
              ? optionLabel(result.cooling.time_to_benefit).replace('_', ' ')
              : t.cooling.notEstimated}
          </dd>
          <dt>{t.cooling.adjustment}</dt>
          <dd>{fmt(result.adjustment.factor)}</dd>
        </dl>
        <p className="muted small">{t.cooling.deltaTNote}</p>
        <details className="collapsible">
          <summary>{t.subScores.heading}</summary>
          <dl className="kv small">
            {(['canopy', 'soil_water', 'scale', 'climate'] as const).map((condition) => (
              <FragmentRow
                key={condition}
                label={t.cooling.adjustmentConditions[condition]}
                value={`${optionLabel(result.adjustment[condition].level)} (× ${fmt(result.adjustment[condition].factor)})${result.adjustment[condition].detail ? ` — ${result.adjustment[condition].detail}` : ''}`}
              />
            ))}
            <FragmentRow
              label={t.subScores.suitability}
              value={`${fmt(result.suitability.score)} / 100`}
            />
            <FragmentRow label={t.subScores.space} value={fmt(result.suitability.space)} />
            <FragmentRow label={t.subScores.soil} value={fmt(result.suitability.soil)} />
            <FragmentRow label={t.subScores.water} value={fmt(result.suitability.water)} />
            <FragmentRow
              label={t.subScores.maintenance}
              value={fmt(result.suitability.maintenance)}
            />
            <FragmentRow
              label={t.subScores.urbanContext}
              value={fmt(result.suitability.urban_context)}
            />
          </dl>
        </details>
      </section>

      <EnergyGhgBlocks result={result} />

      <section className="card">
        <div className="result-block__head">
          <h3>{t.blocks.costs}</h3>
          <ConfidenceBadge level={confidence.economic} />
          <FormulaLink anchor="derived" />
        </div>
        <dl className="kv">
          <dt>{t.costs.annualSavings}</dt>
          <dd>
            {result.costs.annual_savings_status === 'calculated'
              ? `${fmt(result.costs.annual_savings_min ?? 0)}–${fmt(result.costs.annual_savings_max ?? 0)} ${result.costs.currency ?? ''}/year`
              : t.statuses[result.costs.annual_savings_status]}
          </dd>
          <dt>{t.costs.payback}</dt>
          <dd>
            {result.costs.payback_status === 'calculated'
              ? `${fmt(result.costs.payback_years_min ?? 0)}–${fmt(result.costs.payback_years_max ?? 0)} ${t.costs.paybackUnit} (${t.costs.paybackCentral}: ${fmt(result.costs.payback_years_central ?? 0)})`
              : t.statuses[result.costs.payback_status]}
          </dd>
          <dt>{t.costs.feasibility}</dt>
          <dd>
            {result.costs.cost_feasibility_status === 'derived'
              ? `${fmt(result.costs.cost_feasibility_score ?? 0)} / 100${result.costs.payback_bracket ? ` — ${t.costs.bracket[result.costs.payback_bracket]}` : ''}`
              : t.statuses.not_estimated}
          </dd>
          <dt>{t.costs.readiness}</dt>
          <dd>
            {result.costs.investment_readiness_status === 'derived' &&
            result.costs.investment_readiness
              ? optionLabel(result.costs.investment_readiness)
              : t.statuses.not_estimated}
          </dd>
        </dl>
      </section>

      <section className="card">
        <div className="result-block__head">
          <h3>{t.blocks.coBenefits}</h3>
          <FormulaLink anchor="weights" />
        </div>
        <dl className="kv">
          <FragmentRow
            label={t.opportunityComponents.score}
            value={`${fmt(result.co_benefits.score)} / 100`}
          />
          <FragmentRow
            label={t.subScores.biodiversity}
            value={fmt(result.co_benefits.biodiversity)}
          />
          <FragmentRow label={t.subScores.stormwater} value={fmt(result.co_benefits.stormwater)} />
          <FragmentRow
            label={t.subScores.publicHealth}
            value={fmt(result.co_benefits.public_health)}
          />
          <FragmentRow
            label={t.subScores.socialInclusion}
            value={fmt(result.co_benefits.social_inclusion)}
          />
          <FragmentRow
            label={t.subScores.urbanQuality}
            value={fmt(result.co_benefits.urban_quality)}
          />
        </dl>
      </section>

      <section className="card">
        <div className="result-block__head">
          <h3>{t.blocks.equity}</h3>
          <ConfidenceBadge level={confidence.equity} />
          <FormulaLink anchor="derived" />
        </div>
        <dl className="kv">
          <FragmentRow
            label={t.opportunityComponents.score}
            value={`${fmt(result.equity.score)} / 100`}
          />
          <FragmentRow
            label={t.subScores.vulnerableUserBenefit}
            value={fmt(result.equity.vulnerable_user_benefit)}
          />
          <FragmentRow
            label={t.subScores.publicAccessibility}
            value={fmt(result.equity.public_accessibility)}
          />
          <FragmentRow
            label={t.subScores.safetyComfort}
            value={fmt(result.equity.safety_comfort)}
          />
          <FragmentRow
            label={t.subScores.participationRelevance}
            value={fmt(result.equity.participation_relevance)}
          />
        </dl>
        <p className="muted small">{t.subScores.equityNote}</p>
      </section>

      {/* 5 — assumptions applied */}
      <section aria-label={t.assumptionsHeading}>
        <h2>{t.assumptionsHeading}</h2>
        {result.assumptions_applied.length > 0 ? (
          <>
            <p className="muted small">{t.assumptionsIntro}</p>
            <ul>
              {result.assumptions_applied.map((assumption, index) => (
                <li key={`${index}-${assumption}`}>{assumption}</li>
              ))}
            </ul>
          </>
        ) : (
          <p className="muted">{t.assumptionsNone}</p>
        )}
      </section>

      {result.warnings.length > 0 ? (
        <section aria-label={t.warningsHeading}>
          <h2>{t.warningsHeading}</h2>
          <ul>
            {result.warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        </section>
      ) : null}

      {/* 6 — method note and limitations */}
      <section aria-label={t.methodNoteHeading}>
        <h2>{t.methodNoteHeading}</h2>
        <p className="recommendation">{result.method_note}</p>
        <p className="mono small muted">
          {t.versions(result.methodology_version, result.engine_version)}
        </p>
      </section>

      {/* 7 — actions */}
      <div className="actions-row">
        <a
          className="button"
          href={`/api/projects/${projectId}/assessments/${assessmentId}/report.pdf`}
          download
        >
          {t.actions.exportPdf}
        </a>
        <a
          className="button button--secondary"
          href={`/api/projects/${projectId}/assessments/${assessmentId}/report.xlsx`}
          download
        >
          {t.actions.exportXlsx}
        </a>
        <button type="button" className="button" onClick={() => void compareAnother()}>
          {t.actions.compare}
        </button>
        <Link className="button button--secondary" to={`/projects/${projectId}`}>
          {t.actions.backToProject}
        </Link>
      </div>
    </div>
  );
}

/**
 * The package, component by component (D-038, D-044.4).
 *
 * Every component carries its own cooling range, evidence class, suitability
 * and flags, because each was scored on its own values and nothing here is an
 * average of a sibling. The combination rules are the engine's own sentences,
 * served in the `package` block and rendered verbatim — restating them in the
 * interface's words is exactly how the two would drift apart.
 *
 * A package of one renders nothing: a single-intervention assessment looks as
 * it always has.
 */
function PackageSection({ result }: { result: AssessmentResult }) {
  const pkg = result.package;
  if (pkg.component_count <= 1) return null;
  const p = t.packageSection;

  const rules: { key: string; label: string; text: string }[] = [
    { key: 'cooling', label: p.rules.cooling, text: pkg.cooling_rule },
    { key: 'co_benefits', label: p.rules.coBenefits, text: pkg.co_benefit_rule },
    { key: 'suitability', label: p.rules.suitability, text: pkg.suitability_rule },
    { key: 'cost', label: p.rules.cost, text: pkg.cost_rule },
    {
      key: 'energy',
      label: p.rules.energy,
      text: pkg.energy_component_nbs_type
        ? p.energyComponent(
            result.components.find(
              (component) => component.typology.nbs_type === pkg.energy_component_nbs_type,
            )?.typology.display_name ?? pkg.energy_component_nbs_type,
          )
        : p.energyNoComponent,
    },
  ];

  return (
    <section className="card" aria-label={p.heading}>
      <h2>{p.heading}</h2>
      <p className="muted">{p.intro(pkg.component_count)}</p>

      <ol className="package__components">
        {result.components.map((component) => (
          <ComponentCard key={component.typology.nbs_type} component={component} />
        ))}
      </ol>

      <h3>{p.rulesHeading}</h3>
      <dl className="kv small">
        {rules.map((rule) => (
          <FragmentRow key={rule.key} label={rule.label} value={rule.text} />
        ))}
      </dl>
      <p className="muted small">
        {p.representativeWhy}: {pkg.representative_reason}
      </p>
      <FormulaLink anchor="typologies" />
    </section>
  );
}

function ComponentCard({ component }: { component: ComponentBlock }) {
  const p = t.packageSection;
  const typology = component.typology;
  return (
    <li
      className={`package__component${component.is_representative ? ' package__component--representative' : ''}`}
    >
      <div className="package__component-head">
        <strong>{typology.display_name}</strong>
        {component.is_representative ? (
          <span className="badge badge--accent">{p.representative}</span>
        ) : null}
        {component.suitability.suitable ? null : (
          <span className="badge badge--error">{t.flagsHeading}</span>
        )}
      </div>
      <dl className="kv small">
        <FragmentRow
          label={p.cooling}
          value={`${fmt(component.cooling.delta_t_min_c)}–${fmt(component.cooling.delta_t_max_c)} °C`}
        />
        <FragmentRow label={p.evidenceClass} value={typology.archetype_display_name} />
        <FragmentRow
          label={p.evidenceConfidence}
          value={optionLabel(typology.evidence_confidence)}
        />
        <FragmentRow label={p.suitability} value={`${fmt(component.suitability.score)} / 100`} />
        <FragmentRow
          label={p.flags}
          value={
            component.suitability.flags.length > 0
              ? component.suitability.flags.map((flag) => flag.message).join(' · ')
              : p.noFlags
          }
        />
      </dl>
    </li>
  );
}

function FragmentRow({ label, value }: { label: string; value: string }) {
  return (
    <>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </>
  );
}

function EnergyGhgBlocks({ result }: { result: AssessmentResult }) {
  return (
    <>
      <section className="card">
        <div className="result-block__head">
          <h3>{t.blocks.energy}</h3>
          <ConfidenceBadge level={result.confidence.energy} />
          <FormulaLink anchor="energy" />
        </div>
        {result.energy.status === 'calculated' ? (
          <dl className="kv">
            <dt>{t.energy.savings}</dt>
            <dd>
              {fmt(result.energy.savings_min_kwh_per_year ?? 0)}–
              {fmt(result.energy.savings_max_kwh_per_year ?? 0)} {t.energy.unit}
            </dd>
          </dl>
        ) : (
          <p className="muted">{result.energy.status_message}</p>
        )}
      </section>

      <section className="card">
        <div className="result-block__head">
          <h3>{t.blocks.ghg}</h3>
          <ConfidenceBadge level={result.confidence.energy} />
          <FormulaLink anchor="energy" />
        </div>
        {result.ghg.status === 'calculated' ? (
          <dl className="kv">
            <dt>{t.ghg.avoided}</dt>
            <dd>
              {fmt(result.ghg.avoided_min_kgco2e_per_year ?? 0)}–
              {fmt(result.ghg.avoided_max_kgco2e_per_year ?? 0)} {t.ghg.unit}
            </dd>
            <dt>{t.ghg.factor}</dt>
            <dd>
              {fmt(result.ghg.emission_factor_kgco2e_per_kwh ?? 0)}
              {result.ghg.emission_factor_origin
                ? ` (${t.ghg.origin[result.ghg.emission_factor_origin]})`
                : ''}
            </dd>
          </dl>
        ) : (
          <p className="muted">{t.statuses[result.ghg.status]}</p>
        )}
      </section>
    </>
  );
}
