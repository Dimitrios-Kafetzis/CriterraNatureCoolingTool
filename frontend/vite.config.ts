/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// Same-origin integration (D-030): the dev server proxies /api to the local
// FastAPI service, so the app never makes a cross-origin request and the API
// carries no CORS middleware.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['src/test/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
    globals: false,
    // Raised from the 5s default at v2.0.1. These tests render the served
    // library, which grew from 14 typologies to 110 in v2.0, and the wizard
    // tests drive real user events through a debounced auto-save. The slowest
    // is ~1.3s on a development machine but over 3x that on a CI runner, which
    // put it close enough to the default to flake. 15s still fails a genuine
    // hang quickly; it just stops timing a slow machine as a broken test.
    testTimeout: 15_000,
  },
});
