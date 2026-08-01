/**
 * The four form controls of the questionnaire.
 *
 * Every optional qualitative field offers the explicit "Unknown / not sure"
 * level as well as "(not answered)" — the methodology distinguishes an
 * explicit unknown (neutral value, itemised assumption) from a skipped
 * question, and the interface must too. Errors are associated with their
 * fields programmatically (aria-describedby / aria-invalid), not by colour
 * alone (UX §9).
 */

import { useId } from 'react';
import { messages, optionLabel } from '../i18n/en';
import { FieldExplainer } from './FieldExplainer';

interface CommonProps {
  field: string;
  error?: string | undefined;
  required?: boolean;
}

/** The display name for one option of a field, falling back to the level list. */
function labelFor(field: string, option: string): string {
  const perField = messages.options[field as keyof typeof messages.options] as
    Record<string, string> | undefined;
  return perField?.[option] ?? optionLabel(option);
}

function FieldShell(props: CommonProps & { inputId: string; children: React.ReactNode }) {
  const meta = messages.fields[props.field];
  const help = meta?.help;
  return (
    <div className="field">
      <div className="field__label-row">
        <label className="field__label" htmlFor={props.inputId}>
          {meta?.label ?? props.field}
          {!props.required && (
            <span className="muted small"> — {messages.wizard.optionalHint}</span>
          )}
        </label>
        <FieldExplainer field={props.field} />
      </div>
      {help ? (
        <p className="field__help" id={`${props.inputId}-help`}>
          {help}
        </p>
      ) : null}
      {props.children}
      {props.error ? (
        <p className="error-text" id={`${props.inputId}-error`} role="alert">
          {props.error}
        </p>
      ) : null}
    </div>
  );
}

function describedBy(inputId: string, hasHelp: boolean, hasError: boolean): string | undefined {
  const ids = [...(hasHelp ? [`${inputId}-help`] : []), ...(hasError ? [`${inputId}-error`] : [])];
  return ids.length > 0 ? ids.join(' ') : undefined;
}

export function LevelField(
  props: CommonProps & {
    value: string | null | undefined;
    options: readonly string[];
    withUnknown?: boolean;
    onChange: (value: string | undefined) => void;
  },
) {
  const inputId = useId();
  const meta = messages.fields[props.field];
  return (
    <FieldShell {...props} inputId={inputId}>
      <select
        id={inputId}
        value={props.value ?? ''}
        aria-invalid={props.error ? true : undefined}
        aria-describedby={describedBy(inputId, Boolean(meta?.help), Boolean(props.error))}
        onChange={(event) =>
          props.onChange(event.target.value === '' ? undefined : event.target.value)
        }
      >
        <option value="">{messages.wizard.unansweredOption}</option>
        {props.options.map((option) => (
          <option key={option} value={option}>
            {labelFor(props.field, option)}
          </option>
        ))}
        {(props.withUnknown ?? true) ? (
          <option value="unknown">{messages.wizard.unknownOption}</option>
        ) : null}
      </select>
    </FieldShell>
  );
}

/**
 * A multi-select over a fixed option list, rendered as a checkbox group.
 *
 * `productive_governance` is the first field where several answers are
 * simultaneously true (D-043.3: who *could* deliver, not who is interested),
 * and a `<select multiple>` is a poor keyboard and screen-reader target for
 * that. A native checkbox group is reachable by Tab and Space, each box owns
 * its own label, and the group is named by its legend. An empty selection is
 * an unanswered field, not an empty list: the field is deleted from the draft.
 */
export function MultiSelectField(
  props: CommonProps & {
    value: readonly string[] | null | undefined;
    options: readonly string[];
    onChange: (value: string[] | undefined) => void;
  },
) {
  const groupId = useId();
  const meta = messages.fields[props.field];
  const selected = props.value ?? [];

  function toggle(option: string) {
    const next = selected.includes(option)
      ? selected.filter((candidate) => candidate !== option)
      : // Selection order follows the option list, so the stored value does
        // not depend on the order the user happened to tick the boxes.
        props.options.filter((candidate) => candidate === option || selected.includes(candidate));
    props.onChange(next.length > 0 ? [...next] : undefined);
  }

  return (
    <div className="field">
      <fieldset
        className="field__group"
        aria-describedby={describedBy(groupId, Boolean(meta?.help), Boolean(props.error))}
      >
        {/* The legend must be the fieldset's first child, or it does not name
            the group for assistive technology. The explainer sits inside it
            for that reason, and contributes to the group's name exactly as it
            does to every other field's (D-041). */}
        <legend className="field__label field__label-row">
          <span>
            {meta?.label ?? props.field}
            {!props.required && (
              <span className="muted small"> — {messages.wizard.optionalHint}</span>
            )}
          </span>
          <FieldExplainer field={props.field} />
        </legend>
        {meta?.help ? (
          <p className="field__help" id={`${groupId}-help`}>
            {meta.help}
          </p>
        ) : null}
        <div className="checkbox-group">
          {props.options.map((option) => (
            <label className="checkbox-group__option" key={option}>
              <input
                type="checkbox"
                checked={selected.includes(option)}
                onChange={() => toggle(option)}
              />
              <span>{labelFor(props.field, option)}</span>
            </label>
          ))}
        </div>
      </fieldset>
      {props.error ? (
        <p className="error-text" id={`${groupId}-error`} role="alert">
          {props.error}
        </p>
      ) : null}
    </div>
  );
}

export function NumberField(
  props: CommonProps & {
    value: number | null | undefined;
    onChange: (value: number | undefined) => void;
  },
) {
  const inputId = useId();
  const meta = messages.fields[props.field];
  return (
    <FieldShell {...props} inputId={inputId}>
      <span>
        <input
          id={inputId}
          type="number"
          inputMode="decimal"
          step="any"
          value={props.value ?? ''}
          aria-invalid={props.error ? true : undefined}
          aria-describedby={describedBy(inputId, Boolean(meta?.help), Boolean(props.error))}
          onChange={(event) => {
            const raw = event.target.value;
            props.onChange(raw === '' ? undefined : Number(raw));
          }}
        />
        {meta?.unit ? <span className="field__unit">{meta.unit}</span> : null}
      </span>
    </FieldShell>
  );
}

export function TextField(
  props: CommonProps & {
    value: string | null | undefined;
    onChange: (value: string | undefined) => void;
  },
) {
  const inputId = useId();
  const meta = messages.fields[props.field];
  return (
    <FieldShell {...props} inputId={inputId}>
      <input
        id={inputId}
        type="text"
        value={props.value ?? ''}
        aria-invalid={props.error ? true : undefined}
        aria-describedby={describedBy(inputId, Boolean(meta?.help), Boolean(props.error))}
        onChange={(event) => {
          const raw = event.target.value;
          props.onChange(raw === '' ? undefined : raw);
        }}
      />
    </FieldShell>
  );
}
