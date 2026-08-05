/**
 * A cited source list: each key with the finding it supports, and — where the
 * served bibliography resolves the key — the full reference with its DOI or
 * URL as a link (v2.6). A key like `jacobs2020` says nothing on its own, so
 * wherever the interface shows one, it shows the work it names.
 *
 * Everything rendered is served: the findings are the archetype's own
 * `sources`, and the references ride on `GET /api/typologies` parsed from the
 * bibliography the package already carries — no reference text originates
 * here. The links are links the *user* may choose to follow; a link is not a
 * request the app makes, so the request gates are untouched.
 *
 * The bibliography arrives through context so the recursive configuration
 * tree of the methodology browser does not thread it through every level.
 * With no provider (or an unresolved key) the list renders exactly as it
 * always has — key and finding, nothing else. Absence renders nothing.
 */

import { createContext, useContext } from 'react';
import { messages } from '../i18n/en';
import type { SourceReference } from '../api/types';

export const BibliographyContext = createContext<Record<string, SourceReference>>({});

export function SourceList({ sources }: { sources: { key: string; finding: string }[] }) {
  const bibliography = useContext(BibliographyContext);
  return (
    <ul className="source-list">
      {sources.map((source) => {
        const entry = bibliography[source.key];
        return (
          <li key={`${source.key}-${source.finding.slice(0, 24)}`}>
            <span className="source-key">{source.key}</span> — {source.finding}
            {entry !== undefined ? (
              <span className="source-reference">
                {entry.reference}
                {entry.url != null ? (
                  <>
                    {' '}
                    {entry.doi != null ? messages.sources.doi : null}
                    {entry.doi != null ? ' ' : null}
                    <a href={entry.url} target="_blank" rel="noreferrer">
                      {entry.doi ?? messages.sources.link}
                    </a>
                  </>
                ) : null}
              </span>
            ) : null}
          </li>
        );
      })}
    </ul>
  );
}
