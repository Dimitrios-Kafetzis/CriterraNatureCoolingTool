/**
 * The live confidence panel (UX §4, D-018).
 *
 * Renders the per-block preview computed by the engine via
 * POST /api/assessments/validate: level, completeness, and the single
 * highest-value missing field per block. No level, percentage, or threshold
 * originates here. When the typology's evidence confidence caps the cooling
 * block, the panel says so — complete inputs cannot compensate for thin
 * evidence, and the interface must not imply otherwise.
 */

import { messages, fieldLabel, optionLabel } from '../i18n/en';
import { stepOfField, stepTitle } from './steps';
import type { BlockConfidencePreview, ConfidencePreview } from '../api/types';

const BLOCKS = ['cooling', 'energy', 'economic', 'equity'] as const;

function hintText(hint: NonNullable<BlockConfidencePreview['hint']>): string {
  const fields = hint.fields.map(fieldLabel).join(messages.confidence.hintOr);
  const firstField = hint.fields[0];
  const step = firstField ? stepOfField(firstField) : undefined;
  const stepRef = step ? messages.confidence.stepRef(stepTitle(step.id)) : '';
  if (hint.raises_level_to) {
    return messages.confidence.hintRaises(fields, optionLabel(hint.raises_level_to)) + stepRef;
  }
  return messages.confidence.hintNext(fields) + stepRef;
}

export function ConfidencePanel({ preview }: { preview: ConfidencePreview | null }) {
  return (
    <aside className="confidence-panel card" aria-label={messages.confidence.heading}>
      <h3>{messages.confidence.heading}</h3>
      <p className="muted small">{messages.confidence.intro}</p>
      {preview ? (
        <>
          {BLOCKS.map((block) => {
            const data = preview[block];
            return (
              <div key={block} className="confidence-panel__block">
                <div className="confidence-panel__row">
                  <span>{messages.confidence.blocks[block]}</span>
                  <strong>{optionLabel(data.level)}</strong>
                </div>
                <div
                  className="meter"
                  role="img"
                  aria-label={`${messages.confidence.blocks[block]}: ${optionLabel(data.level)} — ${messages.confidence.completeness(data.completeness_percent)}`}
                >
                  <div className="meter__fill" style={{ width: `${data.completeness_percent}%` }} />
                </div>
                {data.hint ? (
                  <p className="confidence-panel__hint">→ {hintText(data.hint)}</p>
                ) : null}
              </div>
            );
          })}
          <div className="confidence-panel__row">
            <span>{messages.confidence.overall}</span>
            <strong>{optionLabel(preview.overall)}</strong>
          </div>
          {preview.cooling_capped_by_evidence ? (
            <p className="notice notice--warn small" style={{ marginTop: '0.75rem' }}>
              {messages.confidence.evidenceCap}
            </p>
          ) : null}
        </>
      ) : (
        <p className="muted small">{messages.app.loading}</p>
      )}
    </aside>
  );
}
