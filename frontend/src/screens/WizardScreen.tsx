/**
 * The six-step questionnaire wizard (UX §3–4; D-018, D-020, D-030).
 *
 * Auto-save is a debounced PATCH of the draft input; inline validation and
 * the live confidence panel are a debounced POST /api/assessments/validate
 * with the full draft payload, errors filtered to the active step's fields.
 * Errors block progression within their step; warnings never block anything
 * (OQ-08). Evaluation is the explicit final action: results enter storage
 * only from the engine.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router';
import { api, ApiError } from '../api/client';
import { messages } from '../i18n/en';
import { useDebouncedValue } from '../lib/useDebouncedValue';
import { ConfidencePanel } from '../wizard/ConfidencePanel';
import { StepForm } from '../wizard/StepForm';
import { STEPS, stepTitle } from '../wizard/steps';
import type {
  AssessmentInput,
  AvailabilityQuery,
  AvailableTypologies,
  DraftInput,
  FieldIssue,
  InputField,
  MethodologyData,
  TypologyLibrary,
  ValidateResponse,
} from '../api/types';

const SAVE_DEBOUNCE_MS = 600;
const VALIDATE_DEBOUNCE_MS = 350;

type SaveState = 'idle' | 'saving' | 'saved' | 'error';

/**
 * The site conditions the availability endpoint gates on (D-043, D-044.1),
 * read straight off the draft. `assessment_scale` is required, so a draft
 * without one has nothing to ask about yet and the picker offers everything.
 *
 * The three yes/no/unknown answers become booleans only where the user said
 * yes or no; an explicit "unknown" is not a "no", so it is left unsent and the
 * service decides what an unanswered condition means.
 */
function availabilityQuery(draft: DraftInput): AvailabilityQuery | null {
  if (draft.assessment_scale == null) return null;
  const tristate = (value: 'yes' | 'no' | 'unknown' | null | undefined) =>
    value === 'yes' ? true : value === 'no' ? false : undefined;
  return {
    assessment_scale: draft.assessment_scale,
    land_use: draft.land_use,
    waterfront_type: draft.waterfront_type,
    includes_railway: tristate(draft.includes_railway),
    existing_woodland: tristate(draft.existing_woodland),
    productive_governance: draft.productive_governance,
  };
}

export function WizardScreen() {
  const { projectId, assessmentId } = useParams<'projectId' | 'assessmentId'>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const stepParam = Number(searchParams.get('step') ?? '1');
  const stepIndex = Number.isInteger(stepParam)
    ? Math.min(Math.max(stepParam, 1), STEPS.length) - 1
    : 0;
  const step = STEPS[stepIndex] ?? STEPS[0]!;

  const [draft, setDraft] = useState<DraftInput | null>(null);
  const [label, setLabel] = useState('');
  const [validation, setValidation] = useState<ValidateResponse | null>(null);
  const [saveState, setSaveState] = useState<SaveState>('idle');
  const [loadError, setLoadError] = useState<string | null>(null);
  const [evaluateIssues, setEvaluateIssues] = useState<FieldIssue[] | null>(null);
  const [evaluating, setEvaluating] = useState(false);
  const [library, setLibrary] = useState<TypologyLibrary | null>(null);
  const [methodology, setMethodology] = useState<MethodologyData | null>(null);
  const [availability, setAvailability] = useState<AvailableTypologies | null>(null);
  // Which answers the map filled in, and from which dataset (D-047.2). Held
  // beside the draft rather than inside it: `draft` holds engine input fields
  // and nothing else, and the engine has no concept of where a value came from.
  const [autofilled, setAutofilled] = useState<Record<string, string>>({});

  // What the store currently holds, to avoid saving an unchanged draft.
  const persisted = useRef<string>('');

  useEffect(() => {
    if (!projectId || !assessmentId) return;
    let cancelled = false;
    api
      .getAssessment(projectId, assessmentId)
      .then((assessment) => {
        if (cancelled) return;
        if (assessment.result != null) {
          // Evaluated input is frozen (D-029); the wizard has nothing to edit.
          void navigate(`/projects/${projectId}/assessments/${assessmentId}/results`, {
            replace: true,
          });
          return;
        }
        const input = assessment.input as DraftInput;
        persisted.current = JSON.stringify(input);
        setLabel(assessment.label);
        setDraft(input);
        setAutofilled(assessment.autofilled ?? {});
      })
      .catch(() => {
        if (!cancelled) setLoadError(messages.app.apiError);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, assessmentId, navigate]);

  // The typology picker's data (step 5): the library and the ordinal ranks.
  useEffect(() => {
    let cancelled = false;
    Promise.all([api.typologies(), api.methodology()])
      .then(([lib, meth]) => {
        if (!cancelled) {
          setLibrary(lib);
          setMethodology(meth);
        }
      })
      .catch(() => {
        // Step 5 shows its own loading state; a hard failure surfaces on save/validate.
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const debouncedDraft = useDebouncedValue(draft, SAVE_DEBOUNCE_MS);
  const debouncedForValidate = useDebouncedValue(draft, VALIDATE_DEBOUNCE_MS);

  // What the service offers for this site (D-043). Re-asked whenever a gating
  // answer changes; the frontend derives no availability rule of its own
  // (ARCHITECTURE boundary 1), so this is the only source of the answer. The
  // query is serialised as the effect's dependency because it is rebuilt on
  // every render — the answers it is made of are what should re-trigger it,
  // not the object's identity.
  const querySignature = useMemo(() => {
    const query = draft === null ? null : availabilityQuery(draft);
    return query === null ? null : JSON.stringify(query);
  }, [draft]);

  useEffect(() => {
    if (querySignature === null) {
      setAvailability(null);
      return;
    }
    let cancelled = false;
    api
      .availableTypologies(JSON.parse(querySignature) as AvailabilityQuery)
      .then((response) => {
        if (!cancelled) setAvailability(response);
      })
      .catch(() => {
        // Unavailable: the picker then offers every entry rather than
        // inventing a gating rule to fill the gap.
        if (!cancelled) setAvailability(null);
      });
    return () => {
      cancelled = true;
    };
  }, [querySignature]);

  // Auto-save (D-020): debounced PATCH of the full draft input.
  useEffect(() => {
    if (!projectId || !assessmentId || debouncedDraft === null) return;
    const serialised = JSON.stringify(debouncedDraft);
    if (serialised === persisted.current) return;
    setSaveState('saving');
    api
      .patchAssessment(projectId, assessmentId, { input: debouncedDraft, autofilled })
      .then((saved) => {
        persisted.current = serialised;
        // The service re-settles the marks against the input it just stored, so
        // a mark for an answer the user has since changed or cleared comes back
        // dropped. Taking its answer rather than keeping ours is what makes the
        // interface and the report agree about provenance (D-047.2).
        setAutofilled(saved.autofilled ?? {});
        setSaveState('saved');
      })
      .catch(() => setSaveState('error'));
  }, [debouncedDraft, autofilled, projectId, assessmentId]);

  // Inline validation + confidence preview (D-028), from the engine only.
  useEffect(() => {
    if (debouncedForValidate === null) return;
    let cancelled = false;
    api
      .validate(debouncedForValidate)
      .then((response) => {
        if (!cancelled) setValidation(response);
      })
      .catch(() => {
        // Transient; the next keystroke retries.
      });
    return () => {
      cancelled = true;
    };
  }, [debouncedForValidate]);

  const setField = useCallback(
    <F extends InputField>(field: F, value: AssessmentInput[F] | undefined) => {
      setEvaluateIssues(null);
      setDraft((previous) => {
        const next = { ...(previous ?? {}) };
        if (value === undefined) {
          delete next[field];
        } else {
          next[field] = value;
        }
        return next;
      });
      // The user has answered this themselves, so it is no longer the map's
      // answer and stops being marked as one — whether they typed a different
      // value or the same one (D-047.2).
      setAutofilled((previous) => {
        if (!(field in previous)) return previous;
        const next = { ...previous };
        delete next[field];
        return next;
      });
    },
    [],
  );

  /**
   * Applies the map's answers, and only where the user has not answered
   * already (D-047.2 — autofill never overwrites an answer already given).
   *
   * Batched deliberately: three fields become one state update and therefore
   * one auto-save, rather than three racing PATCHes.
   */
  const applyAutofill = useCallback((values: DraftInput, sources: Record<string, string>) => {
    setEvaluateIssues(null);
    setDraft((previous) => ({ ...(previous ?? {}), ...values }));
    setAutofilled((previous) => {
      const next = { ...previous };
      for (const field of Object.keys(values)) {
        const source = sources[field];
        if (source !== undefined) next[field] = source;
      }
      return next;
    });
  }, []);

  const errorsByField = useMemo(() => {
    const map: Partial<Record<string, string>> = {};
    for (const issue of validation?.errors ?? []) {
      const field = issue.field.split('.')[0] ?? issue.field;
      if (!(field in map)) map[field] = issue.message;
    }
    return map;
  }, [validation]);

  const stepHasError = (candidate: readonly string[]) =>
    Object.keys(errorsByField).some((field) => candidate.includes(field));
  const currentBlocked = stepHasError(step.fields);

  function goToStep(index: number) {
    // Errors block progression within their step (OQ-08): no forward move
    // while the current step has errors. Going back is always allowed.
    if (index > stepIndex && currentBlocked) return;
    setSearchParams({ step: String(index + 1) }, { replace: false });
    window.scrollTo({ top: 0 });
  }

  async function saveNow(current: DraftInput): Promise<void> {
    if (!projectId || !assessmentId) return;
    const serialised = JSON.stringify(current);
    if (serialised === persisted.current) return;
    setSaveState('saving');
    await api.patchAssessment(projectId, assessmentId, { input: current });
    persisted.current = serialised;
    setSaveState('saved');
  }

  async function runAssessment() {
    if (!projectId || !assessmentId || draft === null) return;
    setEvaluating(true);
    setEvaluateIssues(null);
    try {
      await saveNow(draft);
      await api.evaluateAssessment(projectId, assessmentId);
      void navigate(`/projects/${projectId}/assessments/${assessmentId}/results`);
    } catch (error) {
      if (error instanceof ApiError && Array.isArray(error.detail)) {
        setEvaluateIssues(error.detail as FieldIssue[]);
      } else {
        setLoadError(messages.app.apiError);
      }
      setEvaluating(false);
    }
  }

  if (loadError) return <p className="notice notice--error">{loadError}</p>;
  if (draft === null) return <p className="muted">{messages.app.loading}</p>;

  const isLast = stepIndex === STEPS.length - 1;

  return (
    <div className="wizard">
      <div>
        <p className="muted small">
          {label} — {messages.wizard.stepLabel(stepIndex + 1, STEPS.length)}
        </p>
        <nav aria-label="Steps">
          <ol className="wizard__steps">
            {STEPS.map((candidate, index) => {
              const hasError = stepHasError(candidate.fields);
              return (
                <li key={candidate.id}>
                  <button
                    type="button"
                    className={`wizard__step-chip${hasError ? ' wizard__step-chip--error' : ''}`}
                    aria-current={index === stepIndex ? 'step' : undefined}
                    aria-label={
                      hasError
                        ? messages.wizard.stepHasErrors(stepTitle(candidate.id))
                        : stepTitle(candidate.id)
                    }
                    onClick={() => goToStep(index)}
                  >
                    {index + 1}. {stepTitle(candidate.id)}
                  </button>
                </li>
              );
            })}
          </ol>
        </nav>

        <h1>{stepTitle(step.id)}</h1>
        <p className="muted">{messages.wizard.steps[step.id].intro}</p>

        <StepForm
          step={step.id}
          draft={draft}
          errors={errorsByField}
          setField={setField}
          library={library}
          methodology={methodology}
          availability={availability}
          autofilled={autofilled}
          onAutofill={applyAutofill}
          onSkipMap={() => {
            goToStep(stepIndex + 1);
          }}
        />

        {validation && validation.warnings.length > 0 ? (
          <div className="notice notice--warn" role="status">
            <strong>{messages.wizard.warningsHeading}</strong>
            <ul>
              {validation.warnings.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
            <p className="small muted">{messages.wizard.warningsNeverBlock}</p>
          </div>
        ) : null}

        {evaluateIssues ? (
          <div className="notice notice--error" role="alert">
            <p>{messages.wizard.evaluateInvalid}</p>
            <ul>
              {evaluateIssues.map((issue) => (
                <li key={issue.field}>
                  <code>{issue.field}</code>: {issue.message}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        <div className="wizard__nav">
          <button
            type="button"
            className="button button--quiet"
            disabled={stepIndex === 0}
            onClick={() => goToStep(stepIndex - 1)}
          >
            {messages.wizard.back}
          </button>
          {isLast ? (
            <button
              type="button"
              className="button"
              disabled={evaluating || currentBlocked}
              onClick={() => void runAssessment()}
            >
              {evaluating ? messages.wizard.running : messages.wizard.runAssessment}
            </button>
          ) : (
            <button
              type="button"
              className="button"
              disabled={currentBlocked}
              onClick={() => goToStep(stepIndex + 1)}
            >
              {messages.wizard.continue}
            </button>
          )}
          <span className="wizard__save-state" role="status">
            {saveState === 'saving'
              ? messages.wizard.saving
              : saveState === 'saved'
                ? messages.wizard.saved
                : saveState === 'error'
                  ? messages.wizard.saveFailed
                  : ''}
          </span>
        </div>
        {currentBlocked ? <p className="error-text">{messages.wizard.blockedByErrors}</p> : null}
      </div>

      <ConfidencePanel preview={validation?.confidence ?? null} />
    </div>
  );
}
