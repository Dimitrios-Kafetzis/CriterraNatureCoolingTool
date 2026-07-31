/**
 * The per-parameter explanation control (D-041).
 *
 * Review comment 6: users could not tell what several parameters meant, and
 * long explanatory text under every field was explicitly unwanted. Each field
 * therefore carries an info button beside its label that discloses a short
 * popover — what the parameter means, and what it affects in the scoring —
 * leaving the default view of the form uncluttered.
 *
 * It is a disclosure, not a hover tooltip: hover fails touch and keyboard
 * users alike. The button owns the open state (`aria-expanded`), the popover
 * is associated with it (`aria-controls`), Escape closes and returns focus,
 * and a click outside dismisses. All strings come from the message catalog.
 */

import { useEffect, useId, useRef, useState } from 'react';
import { Link } from 'react-router';
import { messages } from '../i18n/en';

export function FieldExplainer(props: { field: string }) {
  const meta = messages.fields[props.field];
  const [open, setOpen] = useState(false);
  const panelId = useId();
  const buttonRef = useRef<HTMLButtonElement>(null);
  const wrapRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!open) return;

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setOpen(false);
        buttonRef.current?.focus();
      }
    }
    function onPointerDown(event: MouseEvent) {
      if (!wrapRef.current?.contains(event.target as Node)) setOpen(false);
    }

    document.addEventListener('keydown', onKeyDown);
    document.addEventListener('mousedown', onPointerDown);
    return () => {
      document.removeEventListener('keydown', onKeyDown);
      document.removeEventListener('mousedown', onPointerDown);
    };
  }, [open]);

  if (!meta?.what) return null;
  const t = messages.wizard.explain;

  return (
    <span className="explainer" ref={wrapRef}>
      <button
        type="button"
        ref={buttonRef}
        className="explainer__button"
        aria-expanded={open}
        aria-controls={panelId}
        aria-label={t.open(meta.label)}
        onClick={() => setOpen((wasOpen) => !wasOpen)}
      >
        <span aria-hidden="true">i</span>
      </button>
      {open ? (
        <span className="explainer__panel" id={panelId} role="note">
          <strong className="explainer__heading">{t.whatHeading}</strong>
          <span className="explainer__body">{meta.what}</span>
          <strong className="explainer__heading">{t.affectsHeading}</strong>
          <span className="explainer__body">{meta.affects}</span>
          <Link className="explainer__link" to="/methodology" onClick={() => setOpen(false)}>
            {t.methodologyLink}
          </Link>
        </span>
      ) : null}
    </span>
  );
}
