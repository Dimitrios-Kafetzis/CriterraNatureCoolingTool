"""The published curation records, read for the per-entry curation reason (v2.6).

Every catalogue entry exists because a curation decision kept it, and each of
the two records in ``docs/assets/`` states that decision's one-line reason —
the machine-readable transparency data of D-052.3, enforced entry for entry by
``test_catalogue_fidelity.py``. The v2.6 detail dialog shows the reason at the
point of choosing, so a user comparing three entries that inherit the same
evidence class can read *why* each inherits it without opening the report.

The reasons are served by the backend rather than bundled into the frontend
build: user-facing content must not originate from a docs path at build time,
and the records must not move into ``config/`` either — the reason is curation
provenance, not methodology configuration, and rewording a sentence must never
force a methodology version bump. The records are therefore staged into the
wheel beside ``config/`` by ``tools/build_wheel.sh`` and read here, the
bibliography's own arrangement.

Unlike the image manifest, absence is NOT an expected state: every shipped
entry has an approved reason, so a missing record or a shipped entry without
one is a packaging defect and raises rather than rendering around it.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType

from nature_cooling.engine.config import TypologyLibrary, default_curation_records_dir

CURATION_RECORD_FILES = ("v1.2-curation.json", "v2.5-curation.json")


class CurationDataError(RuntimeError):
    """The published curation records are missing, unreadable, or incomplete."""


@lru_cache(maxsize=4)
def load_curation_reasons(records_dir: Path | None = None) -> Mapping[str, str]:
    """Load every curation entry's reason, keyed by curation id.

    The two records' id namespaces are disjoint by construction (the
    supplementary ids carry an ``S`` prefix precisely because the source
    documents collide on seventeen numbers), so merging them into one lookup
    loses nothing.
    """
    directory = records_dir if records_dir is not None else default_curation_records_dir()
    reasons: dict[str, str] = {}
    for name in CURATION_RECORD_FILES:
        path = directory / name
        if not path.is_file():
            raise CurationDataError(f"missing curation record: {path}")
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CurationDataError(f"invalid JSON in {path}: {exc}") from exc
        if not isinstance(loaded, list):
            raise CurationDataError(f"{path} must contain a JSON array at the top level")
        for entry in loaded:
            if not isinstance(entry, dict) or not entry.get("id") or not entry.get("reason"):
                raise CurationDataError(
                    f"curation entry in {path} lacks an id or a reason: {entry!r}"
                )
            reasons[str(entry["id"])] = str(entry["reason"])
    return MappingProxyType(reasons)


def curation_reasons_for(
    library: TypologyLibrary, records_dir: Path | None = None
) -> dict[str, str]:
    """The curation reason of every shipped entry, keyed by ``nbs_id``.

    The catalogue's ``nbs_id`` is the curation record's own id, so the join is
    direct. A shipped entry the records do not explain is a defect the fidelity
    suite also refuses; raising here keeps an installed wheel exactly as honest
    as a checkout.
    """
    reasons = load_curation_reasons(records_dir)
    missing = sorted(
        typology.nbs_id for typology in library.resolved if typology.nbs_id not in reasons
    )
    if missing:
        raise CurationDataError(f"shipped entries absent from the curation records: {missing}")
    return {typology.nbs_id: reasons[typology.nbs_id] for typology in library.resolved}
