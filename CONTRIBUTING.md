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

Frontend setup instructions arrive with Phase 4.

## Reporting issues

Use GitHub Issues. For methodology critique (a welcome contribution category — the tool exists to be reviewable), reference the specific section of the Methodology Report and, where possible, the literature supporting your point.
