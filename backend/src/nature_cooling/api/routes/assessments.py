"""Stateless assessment endpoints: evaluate and dry-run validation."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from nature_cooling.api.schemas import ValidateResponse
from nature_cooling.api.validation import validate_payload
from nature_cooling.engine import run_assessment
from nature_cooling.engine.config import MethodologyConfig
from nature_cooling.engine.models import AssessmentInput, AssessmentResult

router = APIRouter(prefix="/assessments", tags=["assessments"])


def _config(request: Request) -> MethodologyConfig:
    config: MethodologyConfig = request.app.state.config
    return config


@router.post("/evaluate")
def evaluate(inp: AssessmentInput, request: Request) -> AssessmentResult:
    """Validate the input, run the engine, return the full result.

    Stateless and deterministic: an identical request body against an
    identical methodology version yields a byte-identical response body.
    """
    try:
        return run_assessment(inp, _config(request))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/validate")
def validate(payload: dict[str, Any], request: Request) -> ValidateResponse:
    """Dry-run validation of a partial questionnaire state (D-028)."""
    return validate_payload(payload, _config(request))
