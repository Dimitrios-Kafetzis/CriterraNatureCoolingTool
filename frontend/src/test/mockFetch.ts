/**
 * The fetch-boundary mock: tests exercise real
 * components against recorded response shapes captured from the live API
 * (src/test/fixtures/), never invented ones. An unmatched request fails the
 * test loudly instead of resolving to something invented.
 */

import { vi } from 'vitest';

export interface RecordedCall {
  method: string;
  url: string;
  body: unknown;
}

export interface Route {
  method: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  path: string | RegExp;
  /** A recorded fixture, or a function of the parsed request body. */
  response: unknown;
  status?: number;
}

function matches(route: Route, method: string, url: string): boolean {
  if (route.method !== method) return false;
  const path = url.split('?')[0] ?? url;
  return typeof route.path === 'string' ? route.path === path : route.path.test(path);
}

export function installFetchMock(routes: Route[]): { calls: RecordedCall[] } {
  const calls: RecordedCall[] = [];
  vi.stubGlobal(
    'fetch',
    vi.fn((input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
      const method = init?.method ?? 'GET';
      const body = typeof init?.body === 'string' ? (JSON.parse(init.body) as unknown) : null;
      calls.push({ method, url, body });
      const route = routes.find((candidate) => matches(candidate, method, url));
      if (!route) {
        return Promise.reject(new Error(`unmatched ${method} ${url} — add a fixture route`));
      }
      const payload =
        typeof route.response === 'function'
          ? (route.response as (body: unknown, url: string) => unknown)(body, url)
          : route.response;
      const status = route.status ?? (method === 'DELETE' ? 204 : 200);
      return Promise.resolve(
        new Response(status === 204 ? null : JSON.stringify(payload), {
          status,
          headers: { 'Content-Type': 'application/json' },
        }),
      );
    }),
  );
  return { calls };
}
