/**
 * The example-image dialog (v2.3, D-051): one photograph of a real
 * implementation, matched to the project's climate zone, with the attribution
 * its licence requires.
 *
 * Three boundaries govern this file:
 *
 * * **The image is bundled, never hotlinked** (D-049.1): `src` points at the
 *   application's own `/api/images/…`, so opening the dialog adds no request
 *   to any third party. The source-page and licence hyperlinks are links the
 *   *user* may choose to follow — a link is not a request the app makes.
 * * **Captions illustrate, never claim** (D-051.6): what the photograph
 *   shows, where, and in which climate zone. No degrees, no performance, no
 *   cost — and the dialog says outright that the example is not evidence.
 * * **Attribution is rendered, not just stored** (D-051.3): author, licence
 *   name, and a link to the source page appear beside the image, exactly as
 *   the manifest records them.
 *
 * The alt text is the caption verbatim: a screen-reader user gets exactly
 * the statement a sighted user gets, no more and no less.
 */

import { useEffect, useRef } from 'react';
import { messages } from '../i18n/en';
import type { NbsImage } from '../api/types';

function zoneLabel(zone: string): string {
  return (messages.options.climate_zone as Record<string, string>)[zone] ?? zone;
}

export function exampleCaption(image: NbsImage): string {
  return messages.picker.example.caption(image.caption_subject, image.place, zoneLabel(image.zone));
}

export function ExampleImageDialog(props: {
  image: NbsImage;
  /** The evidence class named when the photo attaches at archetype level. */
  archetypeDisplayName: string;
  onClose: () => void;
}) {
  const { image } = props;
  const ref = useRef<HTMLDialogElement>(null);

  // A native <dialog>, opened as a modal so focus containment and Escape
  // handling are the platform's, not reimplementations. jsdom implements
  // neither showModal nor close, so both fall back for the test environment:
  // the open attribute here, and onClose directly in close() below.
  useEffect(() => {
    const dialog = ref.current;
    if (!dialog || dialog.open) return;
    if (typeof dialog.showModal === 'function') dialog.showModal();
    else dialog.setAttribute('open', '');
  }, []);

  const close = () => {
    const dialog = ref.current;
    if (dialog && typeof dialog.close === 'function') dialog.close();
    else props.onClose();
  };

  const caption = exampleCaption(image);

  return (
    <dialog
      ref={ref}
      className="example-dialog"
      aria-label={caption}
      onClose={props.onClose}
      onClick={(event) => {
        // Clicking the backdrop closes; the backdrop is the dialog element
        // itself, while every visible child sits inside the inner div.
        if (event.target === ref.current) close();
      }}
    >
      <div className="example-dialog__body">
        <figure>
          <img
            src={`/api/images/${image.file}`}
            alt={caption}
            width={image.width}
            height={image.height}
          />
          <figcaption>{caption}</figcaption>
        </figure>
        {image.nbs_type == null ? (
          <p className="muted small">
            {messages.picker.example.evidenceClassNote(props.archetypeDisplayName)}
          </p>
        ) : null}
        <p className="muted small">{messages.picker.example.illustrativeNote}</p>
        <p className="example-dialog__credit small">
          {messages.picker.example.credit(image.author)}
          {' · '}
          {messages.picker.example.licenceLabel}{' '}
          {image.licence_url != null ? (
            <a href={image.licence_url} target="_blank" rel="noreferrer">
              {image.licence}
            </a>
          ) : (
            image.licence
          )}
          {' · '}
          <a href={image.source_page} target="_blank" rel="noreferrer">
            {messages.picker.example.sourceLink}
          </a>
        </p>
        <button type="button" className="button button--quiet" onClick={close}>
          {messages.picker.example.close}
        </button>
      </div>
    </dialog>
  );
}
