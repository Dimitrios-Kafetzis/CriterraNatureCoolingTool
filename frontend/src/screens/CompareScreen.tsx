/**
 * Same-site A/B/C comparison (UX §7, D-021, D-005).
 *
 * Options render side by side from their stored results; rows where the
 * options differ are highlighted rather than repeating identical values.
 * The winning option is never announced — the tool presents the axes and
 * the decision belongs to the user.
 */

import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router';
import { api } from '../api/client';
import { storedResult } from '../api/types';
import type { AssessmentResult, AssessmentView, ProjectView } from '../api/types';
import { messages, optionLabel } from '../i18n/en';
import { stepNumber } from '../wizard/steps';

const t = messages.compare;

function fmt(value: number): string {
  return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

interface Option {
  assessment: AssessmentView;
  result: AssessmentResult;
}

interface Row {
  label: string;
  values: string[];
  emphasis?: 'error' | undefined;
}

function buildRows(options: Option[]): Row[] {
  const results = options.map((option) => option.result);
  return [
    {
      // A package lists its components; a package of one reads exactly as it
      // always has (D-038).
      label: t.row.typology,
      values: results.map((r) =>
        r.components.map((component) => component.typology.display_name).join(' + '),
      ),
    },
    {
      label: t.row.components,
      values: results.map((r) => messages.picker.selectionCount(r.package.component_count)),
    },
    {
      label: t.row.opportunity,
      values: results.map(
        (r) => `${fmt(r.opportunity.score)} (${optionLabel(r.opportunity.category)})`,
      ),
    },
    {
      label: t.row.heatPriority,
      values: results.map(
        (r) => `${fmt(r.heat_priority.score)} (${optionLabel(r.heat_priority.category)})`,
      ),
    },
    {
      label: t.row.deltaT,
      values: results.map(
        (r) => `${fmt(r.cooling.delta_t_min_c)}–${fmt(r.cooling.delta_t_max_c)} °C`,
      ),
    },
    {
      label: t.row.energySavings,
      values: results.map((r) =>
        r.energy.status === 'calculated'
          ? `${fmt(r.energy.savings_min_kwh_per_year ?? 0)}–${fmt(r.energy.savings_max_kwh_per_year ?? 0)} ${messages.results.energy.unit}`
          : r.energy.status_message,
      ),
    },
    {
      label: t.row.payback,
      values: results.map((r) =>
        r.costs.payback_status === 'calculated'
          ? `${fmt(r.costs.payback_years_central ?? 0)} ${messages.results.costs.paybackUnit}`
          : (messages.results.statuses[r.costs.payback_status] ?? r.costs.payback_status),
      ),
    },
    {
      label: t.row.confidence,
      values: results.map((r) => optionLabel(r.confidence.overall)),
    },
    {
      // The evidence class the headline estimate was inherited from, named
      // alongside its confidence (D-044).
      label: t.row.evidence,
      values: results.map(
        (r) =>
          `${optionLabel(r.typology.evidence_confidence)} (${r.typology.archetype_display_name})`,
      ),
    },
    {
      label: t.row.flags,
      values: results.map((r) =>
        r.suitability.flags.length > 0
          ? r.suitability.flags.map((flag) => flag.message).join(' · ')
          : t.noFlags,
      ),
      emphasis: 'error',
    },
  ];
}

export function CompareScreen() {
  const { projectId } = useParams<'projectId'>();
  const navigate = useNavigate();
  const [project, setProject] = useState<ProjectView | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string[] | null>(null);

  useEffect(() => {
    if (!projectId) return;
    let cancelled = false;
    api
      .getProject(projectId)
      .then((view) => {
        if (!cancelled) setProject(view);
      })
      .catch(() => {
        if (!cancelled) setError(messages.app.apiError);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId]);

  const evaluated = useMemo(
    () =>
      (project?.assessments ?? [])
        .map((assessment) => ({ assessment, result: storedResult(assessment) }))
        .filter((option): option is Option => option.result !== null),
    [project],
  );

  // Default: the first three evaluated options.
  const chosen = selected ?? evaluated.slice(0, 3).map((option) => option.assessment.assessment_id);

  if (error) return <p className="notice notice--error">{error}</p>;
  if (!project || !projectId) return <p className="muted">{messages.app.loading}</p>;

  const options = evaluated.filter((option) => chosen.includes(option.assessment.assessment_id));
  const rows = options.length >= 2 ? buildRows(options) : [];

  function toggle(assessmentId: string) {
    const next = chosen.includes(assessmentId)
      ? chosen.filter((id) => id !== assessmentId)
      : [...chosen, assessmentId];
    setSelected(next);
  }

  async function addOption() {
    const source = options[0] ?? evaluated[0];
    if (!source) return;
    const created = await api.duplicateAssessment(projectId ?? '', source.assessment.assessment_id);
    void navigate(
      `/projects/${projectId}/assessments/${created.assessment_id}/edit?step=${String(stepNumber('intervention'))}`,
    );
  }

  return (
    <div>
      <h1>{t.heading}</h1>
      <p className="page-intro muted">{t.intro}</p>

      <fieldset className="field">
        <legend className="field__label">{t.pickOptions}</legend>
        <div className="actions-row">
          {evaluated.map((option) => (
            <label key={option.assessment.assessment_id}>
              <input
                type="checkbox"
                checked={chosen.includes(option.assessment.assessment_id)}
                onChange={() => toggle(option.assessment.assessment_id)}
              />{' '}
              {option.assessment.label}
            </label>
          ))}
        </div>
      </fieldset>

      {options.length < 2 ? (
        <p className="notice">{t.needTwo}</p>
      ) : (
        <>
          <table className="data compare-table">
            <thead>
              <tr>
                <th scope="col"></th>
                {options.map((option) => (
                  <th key={option.assessment.assessment_id} scope="col">
                    {option.assessment.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const differs = new Set(row.values).size > 1;
                return (
                  <tr key={row.label} className={differs ? 'differs' : 'identical'}>
                    <th scope="row">{row.label}</th>
                    {row.values.map((value, index) => (
                      <td
                        key={options[index]?.assessment.assessment_id ?? index}
                        className={
                          row.emphasis === 'error' && value !== t.noFlags ? 'num' : undefined
                        }
                      >
                        {value}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
          <p className="muted small">{t.identicalNote}</p>
        </>
      )}

      <div className="actions-row" style={{ marginTop: '1.5rem' }}>
        <button type="button" className="button" onClick={() => void addOption()}>
          {t.addOption}
        </button>
        <Link className="button button--secondary" to={`/projects/${projectId}`}>
          {messages.results.actions.backToProject}
        </Link>
      </div>
    </div>
  );
}
