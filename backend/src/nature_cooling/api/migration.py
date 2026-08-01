"""Explicit storage migration (D-029, D-044.2).

D-029 forbids silent migration, so a stored project written by an older build
is migrated **deliberately and itemised**: each change is recorded as a
human-readable note that travels with the project to the interface, and
nothing happens that the user is not told about.

Two rules bound what a migration may do.

**Stored results are never touched.** A result keeps the methodology version
that produced it (OQ-15). Migration rewrites only the *draft input* — the
answers — and never the outputs, which is why an engine upgrade can never make
an older stored result unreadable or silently restate it.

**A migration reshapes data; it never substitutes methodology.** The v1→v2
migration wraps ``nbs_type`` into a single-element list, because the field
became a list when an assessment gained the ability to propose a package. It
does **not** map the fourteen retired typology slugs onto successor catalogue
entries, tempting though that is: choosing a different intervention on the
user's behalf would change what the assessment means without the user saying
so. The retired slug is preserved, the note says plainly that it must be
re-selected, and the note names the archetype its cited values moved to so the
user can find them again.
"""

from __future__ import annotations

from typing import Any

# The v1.1 typology library, split by what actually happened to each slug.
# Getting this split right matters: telling a user to re-select an intervention
# that is still there would be a false alarm about their own saved work.
#
# These nine no longer name a selectable entry. Their cited values became
# archetypes, which the catalogue entries now inherit (D-043.6, D-044). The
# archetype is named so a migrated draft can say where its evidence went; the
# mapping is never applied as a substitution, because choosing a different
# intervention on the user's behalf would change what the assessment means.
RETIRED_TYPOLOGIES: dict[str, str] = {
    "street_tree_planting": "street_tree_canopy",
    "shaded_pedestrian_corridor": "continuous_shaded_corridor",
    "urban_forest": "dense_tree_canopy",
    "park_upgrade": "established_park",
    "green_roof": "extensive_green_roof",
    "green_facade": "green_facade_living_wall",
    "rain_garden_bioswale": "bioretention",
    "riparian_restoration": "riparian_restoration",
    "permeable_shaded_plaza": "permeable_shaded_hardscape",
}

# These three still name a selectable entry in the 110-entry library: only
# their evidence class moved, and the draft continues to evaluate unchanged.
# They are reported for transparency — the numbers behind the entry may differ
# from the ones the user saw when they saved it — but nothing needs re-doing.
MOVED_EVIDENCE_CLASS: dict[str, str] = {
    "pocket_park": "established_park",
    "blue_green_corridor": "blue_green_corridor",
    "courtyard_greening": "enclosed_courtyard",
}

# Two typologies have no archetype successor at all, and say so rather than
# pointing at an approximation.
WITHDRAWN_TYPOLOGIES: dict[str, str] = {
    "schoolyard_greening": (
        "retired as a typology: a schoolyard is a land-use context, not an "
        "intervention (D-043.1). A school site is now offered the real "
        "interventions that suit it"
    ),
    "mixed_nbs_package": (
        "replaced by multi-intervention packages: select the components "
        "themselves and each is scored and shown individually (D-038)"
    ),
}


def _migrate_assessment_v1_to_v2(assessment: dict[str, Any]) -> list[str]:
    """Migrate one stored assessment's draft input in place; return notes."""
    label = assessment.get("label", assessment.get("assessment_id", "assessment"))
    draft = assessment.get("input")
    if not isinstance(draft, dict) or "nbs_type" not in draft:
        return []

    value = draft["nbs_type"]
    if not isinstance(value, str):
        return []

    draft["nbs_type"] = [value]
    notes = [
        f"{label}: nbs_type {value!r} wrapped into a single-element list, "
        "because an assessment may now propose a package of interventions"
    ]
    if value in WITHDRAWN_TYPOLOGIES:
        notes.append(f"{label}: {value!r} {WITHDRAWN_TYPOLOGIES[value]}; re-select an intervention")
    elif value in RETIRED_TYPOLOGIES:
        notes.append(
            f"{label}: {value!r} is no longer a selectable typology — its cited values are now "
            f"the {RETIRED_TYPOLOGIES[value]!r} evidence class, which the catalogue entries "
            "inherit; re-select an intervention from the new library"
        )
    elif value in MOVED_EVIDENCE_CLASS:
        notes.append(
            f"{label}: {value!r} is still selectable and this draft still evaluates; its cooling "
            f"values are now inherited from the {MOVED_EVIDENCE_CLASS[value]!r} evidence class, "
            "so the numbers may differ from the ones shown when it was saved"
        )
    return notes


def _v1_to_v2(document: dict[str, Any]) -> list[str]:
    """Wrap every stored draft's ``nbs_type`` into a list.

    The four availability fields added at this version are deliberately left
    **absent** rather than defaulted: a default would be an answer the user
    never gave, and these questions gate which interventions are offered.
    """
    notes: list[str] = []
    for assessment in document.get("assessments", []):
        notes.extend(_migrate_assessment_v1_to_v2(assessment))
    document["schema_version"] = 2
    return notes


_MIGRATIONS = {1: _v1_to_v2}


def migrate_document(document: dict[str, Any], target: int) -> tuple[dict[str, Any], list[str]]:
    """Bring one stored project document up to ``target``, itemising changes.

    Raises:
        ValueError: if the document's version is newer than this build reads,
            or if no migration path exists from it. A version this build does
            not understand is refused, never guessed at (D-029).
    """
    version = document.get("schema_version")
    if not isinstance(version, int):
        raise ValueError("stored project has no integer schema_version")
    if version > target:
        raise ValueError(
            f"stored project schema_version {version} is newer than this build reads ({target}); "
            "upgrade the application rather than downgrading the data"
        )

    notes: list[str] = []
    while version < target:
        migrate = _MIGRATIONS.get(version)
        if migrate is None:
            raise ValueError(f"no migration path from stored schema_version {version} to {target}")
        notes.extend(migrate(document))
        version = int(document["schema_version"])
    return document, notes
