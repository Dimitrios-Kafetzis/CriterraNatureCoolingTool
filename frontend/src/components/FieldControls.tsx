/**
 * The three form controls of the questionnaire.
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

interface CommonProps {
  field: string;
  error?: string | undefined;
  required?: boolean;
}

function FieldShell(props: CommonProps & { inputId: string; children: React.ReactNode }) {
  const meta = messages.fields[props.field];
  const help = meta?.help;
  return (
    <div className="field">
      <label className="field__label" htmlFor={props.inputId}>
        {meta?.label ?? props.field}
        {!props.required && <span className="muted small"> — {messages.wizard.optionalHint}</span>}
      </label>
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
            {messages.options[props.field as keyof typeof messages.options] !== undefined
              ? ((
                  messages.options[props.field as keyof typeof messages.options] as Record<
                    string,
                    string
                  >
                )[option] ?? optionLabel(option))
              : optionLabel(option)}
          </option>
        ))}
        {(props.withUnknown ?? true) ? (
          <option value="unknown">{messages.wizard.unknownOption}</option>
        ) : null}
      </select>
    </FieldShell>
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
