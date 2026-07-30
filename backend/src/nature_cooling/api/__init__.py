"""FastAPI service (Phase 3).

A thin, stateless wrapper over ``nature_cooling.engine`` plus a local-first
storage layer (D-020, D-028). No score, default, threshold, or recommendation
text originates here: every number the API returns comes from the engine or
from the methodology configuration. UUIDs and timestamps exist only in this
layer — the engine stays pure and clock-free.
"""

from nature_cooling.api.main import create_app

__all__ = ["create_app"]
