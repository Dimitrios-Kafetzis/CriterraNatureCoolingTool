import { render } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router';
import { Shell } from '../components/Shell';

/**
 * Render a screen inside the app shell at a concrete URL, with optional
 * probe routes to observe navigation.
 */
export function renderAt(url: string, routes: React.ReactNode) {
  return render(
    <MemoryRouter initialEntries={[url]}>
      <Routes>
        <Route element={<Shell />}>{routes}</Route>
      </Routes>
    </MemoryRouter>,
  );
}
