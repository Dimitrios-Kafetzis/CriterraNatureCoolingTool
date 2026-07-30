import { useEffect, useState } from 'react';
import { Link, Outlet } from 'react-router';
import { api } from '../api/client';
import type { MetaResponse } from '../api/types';
import { messages } from '../i18n/en';

/** Layout frame: brand header, content, and a footer stamped with the live versions. */
export function Shell() {
  const [meta, setMeta] = useState<MetaResponse | null>(null);

  useEffect(() => {
    let cancelled = false;
    api
      .meta()
      .then((response) => {
        if (!cancelled) setMeta(response);
      })
      .catch(() => {
        // The footer version stamp is decoration; screens surface API failures themselves.
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="shell">
      <header className="shell__header">
        <div className="shell__header-inner">
          <Link to="/" className="shell__brand">
            {messages.app.title}
            <small>
              {messages.app.subtitle} {messages.app.byCriterra}
            </small>
          </Link>
          <nav className="shell__nav" aria-label="Main">
            <Link to="/projects">{messages.app.nav.projects}</Link>
            <Link to="/methodology">{messages.app.nav.methodology}</Link>
          </nav>
        </div>
      </header>
      <main className="shell__main">
        <Outlet />
      </main>
      <footer className="shell__footer">
        <div className="shell__footer-inner">
          <span>{messages.app.footer.license}</span>
          {meta ? (
            <span className="mono">
              {messages.app.footer.methodologyVersion} {meta.methodology_version} ·{' '}
              {messages.app.footer.engine} {meta.engine_version}
            </span>
          ) : null}
        </div>
      </footer>
    </div>
  );
}
