# Contributing

Thank you for your interest in the Nature for Cooling Rapid Assessment Tool.

## Ground rules

- **Methodology changes** (anything under `config/` or `docs/methodology/`) require citations. A performance value without a verifiable source will not be merged — CI enforces this. Methodology changes must bump the config `version:` and update the Methodology Report in the same PR.
- **Engine changes** must keep the engine pure (no I/O, no randomness, no network) and deterministic, with tests. Target: 100% line coverage of `nature_cooling.engine`.
- **Commits** follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`).
- **Workflow:** branch from `main` → PR → CI green → review → squash-merge. One development phase (or coherent feature) per PR.

## Development setup

```bash
# Backend (Python 3.11+)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest          # tests
ruff check .    # lint
mypy src        # types
```

```bash
# Frontend (Node 18+)
cd frontend
npm install
npm run dev           # dev server; proxies /api to http://127.0.0.1:8000
npm test              # vitest (contract tests against recorded API responses)
npm run lint          # eslint
npm run format:check  # prettier
npm run typecheck     # tsc --noEmit
npm run generate      # regenerate openapi.json + src/api/schema.ts (CI fails on drift)
```

Frontend ground rules: no number originates client-side — every score, threshold, band, default, confidence level, and recommendation text renders from an API response; API types are generated from the OpenAPI schema, never hand-written; runtime dependencies stay limited to `react`, `react-dom`, and `react-router` (D-030); all user-facing strings live in the message catalog (`src/i18n/`).

## Reporting issues

Use GitHub Issues. For methodology critique (a welcome contribution category — the tool exists to be reviewable), reference the specific section of the Methodology Report and, where possible, the literature supporting your point.
