"""Calculation engine (Phase 2).

The engine is a pure function of (validated input, methodology configuration):
no I/O, no network, no randomness, no global state. Same inputs and same
methodology version always produce identical results.

Scoring formulas are implemented one module per formula family under
``nature_cooling.engine.scoring`` and are documented, value by value, in the
Methodology Report (docs/methodology/).
"""

from nature_cooling.engine.config import MethodologyConfig, get_config, load_config
from nature_cooling.engine.models import AssessmentInput, AssessmentResult
from nature_cooling.engine.runner import run_assessment

__all__ = [
    "AssessmentInput",
    "AssessmentResult",
    "MethodologyConfig",
    "get_config",
    "load_config",
    "run_assessment",
]
