import { useEffect, useState } from 'react';
import { Link, Outlet } from 'react-router';
import { api } from '../api/client';
import type { MetaResponse } from '../api/types';
import { messages } from '../i18n/en';

/**
 * Layout frame: brand header, content, and a footer stamped with the live
 * versions plus the Criterra copyright and product line (D-042).
 *
 * The Criterra lockup and every icon are self-hosted under `public/`, like the
 * three brand font families: the application makes no third-party requests.
 */
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
          <Link to="/" className="shell__brand" aria-label={messages.app.homeLink}>
            <img
              className="shell__logo"
              src="/brand/criterra-lockup.svg"
              alt={messages.app.criterraLogoAlt}
              width={264}
              height={104}
            />
            <span className="shell__brand-text">
              {messages.app.title}
              <small>{messages.app.subtitle}</small>
            </span>
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
          <span>
            {messages.app.footer.copyright(new Date().getFullYear())} ·{' '}
            {messages.app.footer.product}{' '}
            <a href={messages.app.footer.siteUrl} rel="noreferrer noopener">
              {messages.app.footer.site}
            </a>
          </span>
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
