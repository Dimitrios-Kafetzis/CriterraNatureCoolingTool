"""Calculation engine (Phase 2).

The engine is a pure function of (validated input, methodology configuration):
no I/O, no network, no randomness, no global state. Same inputs and same
methodology version always produce identical results.

Scoring formulas are implemented one module per formula family under
``nature_cooling.engine.scoring`` and are documented, value by value, in the
Methodology Report (docs/methodology/).
"""
