/** Criterra identity and copyright in the application frame (D-042). */

import { screen } from '@testing-library/react';
import { Route } from 'react-router';
import { describe, expect, it } from 'vitest';
import { messages } from '../i18n/en';
import { installFetchMock } from './mockFetch';
import { renderAt } from './render';
import meta from './fixtures/meta.json';

function renderShell() {
  installFetchMock([{ method: 'GET', path: '/api/meta', response: meta }]);
  renderAt('/', <Route index element={<p>content</p>} />);
}

describe('Shell branding', () => {
  it('carries the Criterra logo in the header', () => {
    renderShell();

    expect(screen.getByAltText(messages.app.criterraLogoAlt)).toHaveAttribute(
      'src',
      '/brand/criterra-lockup.svg',
    );
  });

  it('states the copyright, the product relationship, and links to criterra.eu', () => {
    renderShell();

    // One footer line interleaves text and a link, so read the whole banner.
    const footer = screen.getByRole('contentinfo');
    expect(footer).toHaveTextContent('Criterra');
    expect(footer).toHaveTextContent(messages.app.footer.product);
    expect(screen.getByRole('link', { name: messages.app.footer.site })).toHaveAttribute(
      'href',
      messages.app.footer.siteUrl,
    );
  });

  it('keeps the open-methodology licence line beside the copyright', () => {
    renderShell();

    expect(screen.getByText(messages.app.footer.license)).toBeInTheDocument();
  });
});
