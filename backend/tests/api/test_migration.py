"""Explicit storage migration, v1 → v2 (D-029, D-044.2).

D-029 forbids silent migration, so the contract under test is not merely "the
old file still opens". It is that every change to a user's saved work is
itemised in words they can read, that stored *results* are never touched, that
a retired typology is preserved and reported rather than substituted, and that
a version this build does not understand is refused rather than guessed at.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from nature_cooling.api.migration import (
    MOVED_EVIDENCE_CLASS,
    RETIRED_TYPOLOGIES,
    WITHDRAWN_TYPOLOGIES,
    migrate_document,
)
from nature_cooling.api.schemas import STORAGE_SCHEMA_VERSION
from nature_cooling.api.storage import ProjectStore

_PROJECT_ID = "11111111-1111-4111-8111-111111111111"
_ASSESSMENT_ID = "22222222-2222-4222-8222-222222222222"


def _v1_document(
    *, nbs_type: Any = "street_tree_planting", result: dict[str, Any] | None = None, **extra: Any
) -> dict[str, Any]:
    """A stored project document as the v1 build wrote it."""
    return {
        "schema_version": 1,
        "project_id": _PROJECT_ID,
        "name": "Riverside pilot",
        "created_at": "2026-07-30T09:00:00+00:00",
        "updated_at": "2026-07-30T10:00:00+00:00",
        "site": {},
        "assessments": [
            {
                "assessment_id": _ASSESSMENT_ID,
                "label": "Option A",
                "created_at": "2026-07-30T09:30:00+00:00",
                "input": {"assessment_scale": "neighbourhood", "nbs_type": nbs_type, **extra},
                "result": result,
            }
        ],
    }


def _write(storage_root: Path, document: dict[str, Any]) -> str:
    storage_root.mkdir(parents=True, exist_ok=True)
    text = json.dumps(document, indent=2) + "\n"
    (storage_root / f"{document['project_id']}.json").write_text(text, encoding="utf-8")
    return text


# --- The reshape itself ------------------------------------------------------


def test_a_v1_string_nbs_type_becomes_a_single_element_list() -> None:
    """The field became a list when an assessment gained the ability to propose
    a package; the migration reshapes the answer and changes nothing else."""
    document = _v1_document(nbs_type="tree_avenue")
    migrated, notes = migrate_document(document, STORAGE_SCHEMA_VERSION)

    assert migrated["schema_version"] == STORAGE_SCHEMA_VERSION
    assert migrated["assessments"][0]["input"]["nbs_type"] == ["tree_avenue"]
    assert migrated["assessments"][0]["input"]["assessment_scale"] == "neighbourhood"
    assert notes, "a migration is never silent (D-029)"


def test_the_notes_itemise_the_change_in_words_a_user_can_read() -> None:
    _, notes = migrate_document(_v1_document(nbs_type="tree_avenue"), STORAGE_SCHEMA_VERSION)
    (note,) = notes
    # The note names the assessment it applies to, the value it changed, and why.
    assert note.startswith("Option A: ")
    assert "'tree_avenue'" in note
    assert "single-element list" in note
    assert "package" in note


def test_every_stored_assessment_is_itemised_separately() -> None:
    """Notes are per assessment, so a project of several drafts says which is which."""
    document = _v1_document()
    second = json.loads(json.dumps(document["assessments"][0]))
    second["assessment_id"] = "33333333-3333-4333-8333-333333333333"
    second["label"] = "Option B"
    second["input"]["nbs_type"] = "tree_avenue"
    document["assessments"].append(second)

    _, notes = migrate_document(document, STORAGE_SCHEMA_VERSION)
    assert any(note.startswith("Option A: ") for note in notes)
    assert any(note.startswith("Option B: ") for note in notes)


def test_a_draft_without_an_nbs_type_migrates_without_a_note() -> None:
    """An untouched draft produces no note: the notes describe changes, not files."""
    document = _v1_document()
    del document["assessments"][0]["input"]["nbs_type"]
    migrated, notes = migrate_document(document, STORAGE_SCHEMA_VERSION)
    assert notes == []
    assert migrated["schema_version"] == STORAGE_SCHEMA_VERSION


def test_an_nbs_type_that_is_already_a_list_is_left_alone() -> None:
    """The reshape is idempotent, so a document that already carries the new
    shape is neither double-wrapped nor reported as changed."""
    document = _v1_document(nbs_type=["tree_avenue", "pocket_park"])
    migrated, notes = migrate_document(document, STORAGE_SCHEMA_VERSION)
    assert migrated["assessments"][0]["input"]["nbs_type"] == ["tree_avenue", "pocket_park"]
    assert notes == []


def test_a_draft_that_is_not_an_object_is_left_alone() -> None:
    """Migration reshapes what it recognises and never invents structure."""
    document = _v1_document()
    document["assessments"][0]["input"] = "corrupted"
    _, notes = migrate_document(document, STORAGE_SCHEMA_VERSION)
    assert notes == []


def test_the_availability_answers_are_left_absent_rather_than_defaulted() -> None:
    """A default would be an answer the user never gave, and these four
    questions gate which interventions are offered (D-044.1)."""
    migrated, _ = migrate_document(_v1_document(), STORAGE_SCHEMA_VERSION)
    draft = migrated["assessments"][0]["input"]
    for field in (
        "includes_railway",
        "existing_woodland",
        "waterfront_type",
        "productive_governance",
    ):
        assert field not in draft


# --- Retired and withdrawn typologies ---------------------------------------


def test_a_withdrawn_slug_is_preserved_and_the_note_says_it_must_be_reselected() -> None:
    """``schoolyard_greening`` was retired as a typology, not renamed.

    Choosing a different intervention on the user's behalf would change what
    the assessment means without them saying so, so the migration preserves the
    slug and says plainly that it must be re-selected.
    """
    migrated, notes = migrate_document(
        _v1_document(nbs_type="schoolyard_greening"), STORAGE_SCHEMA_VERSION
    )
    assert migrated["assessments"][0]["input"]["nbs_type"] == ["schoolyard_greening"]

    retirement = notes[-1]
    assert "'schoolyard_greening'" in retirement
    assert "re-select an intervention" in retirement
    assert WITHDRAWN_TYPOLOGIES["schoolyard_greening"] in retirement


def test_the_package_slug_points_at_selecting_the_components_themselves() -> None:
    """``mixed_nbs_package`` is replaced by real multi-intervention packages (D-038)."""
    _, notes = migrate_document(_v1_document(nbs_type="mixed_nbs_package"), STORAGE_SCHEMA_VERSION)
    assert "select the components" in notes[-1]
    assert "re-select an intervention" in notes[-1]


def test_a_retired_slug_names_the_evidence_class_its_values_moved_to() -> None:
    """The mapping is *reported*, never applied: a migration reshapes data, it
    never substitutes methodology (D-044)."""
    migrated, notes = migrate_document(
        _v1_document(nbs_type="street_tree_planting"), STORAGE_SCHEMA_VERSION
    )
    assert migrated["assessments"][0]["input"]["nbs_type"] == ["street_tree_planting"]

    retirement = notes[-1]
    assert "'street_tree_planting'" in retirement
    assert RETIRED_TYPOLOGIES["street_tree_planting"] in retirement
    assert "re-select an intervention" in retirement


@pytest.mark.parametrize("slug", sorted(RETIRED_TYPOLOGIES))
def test_every_retired_slug_is_reported_and_never_substituted(slug: str) -> None:
    migrated, notes = migrate_document(_v1_document(nbs_type=slug), STORAGE_SCHEMA_VERSION)
    assert migrated["assessments"][0]["input"]["nbs_type"] == [slug]
    assert len(notes) == 2
    assert RETIRED_TYPOLOGIES[slug] in notes[-1]


@pytest.mark.parametrize("slug", sorted(MOVED_EVIDENCE_CLASS))
def test_a_slug_that_is_still_selectable_is_not_told_to_re_select(slug: str) -> None:
    """Three v1 slugs still name a catalogue entry; only their evidence class moved.

    Telling a user to re-select an intervention that is still there would be a
    false alarm about their own saved work, so these three get a note that says
    what actually happened: the draft still evaluates, and the numbers behind it
    may differ because the entry now inherits a different cited evidence class.
    """
    migrated, notes = migrate_document(_v1_document(nbs_type=slug), STORAGE_SCHEMA_VERSION)
    assert migrated["assessments"][0]["input"]["nbs_type"] == [slug]
    note = notes[-1]
    assert MOVED_EVIDENCE_CLASS[slug] in note
    assert "still selectable" in note
    assert "re-select" not in note
    assert "no longer a selectable typology" not in note


def test_every_slug_is_classified_against_the_library_it_describes(config) -> None:
    """The two tables must match the library, or the notes tell users lies.

    This is the test that catches the class of defect where a slug is described
    as retired while the library still offers it: it compares the migration's
    own classification against the entries that actually exist, rather than
    trusting the tables to have been maintained by hand.
    """
    names = {typology.nbs_type for typology in config.typologies.resolved}
    for slug in RETIRED_TYPOLOGIES:
        assert slug not in names, f"{slug} is still selectable but is reported as retired"
    for slug in MOVED_EVIDENCE_CLASS:
        assert slug in names, f"{slug} is reported as selectable but no such entry exists"
    assert not set(RETIRED_TYPOLOGIES) & set(MOVED_EVIDENCE_CLASS)
    assert not set(WITHDRAWN_TYPOLOGIES) & names


# --- What a migration may never do -------------------------------------------


def test_stored_results_are_untouched_by_migration() -> None:
    """A result keeps the methodology version that produced it (OQ-15).

    Migration rewrites only the draft input, never the outputs, which is why an
    engine upgrade can never silently restate an older stored result.
    """
    result = {
        "engine_version": "0.6.0",
        "methodology_version": "2026.07.30",
        "typology": {"nbs_type": "street_tree_planting", "display_name": "Street tree planting"},
        "opportunity": {"score": 72.33, "category": "strong"},
        "recommendation": "Proceed to concept design.",
    }
    original = json.loads(json.dumps(result))
    migrated, _ = migrate_document(_v1_document(result=result), STORAGE_SCHEMA_VERSION)
    assert migrated["assessments"][0]["result"] == original


def test_a_newer_schema_version_is_refused_with_a_clear_error() -> None:
    """A version this build does not understand is refused, never guessed at."""
    document = _v1_document()
    document["schema_version"] = STORAGE_SCHEMA_VERSION + 1
    with pytest.raises(ValueError) as exc:
        migrate_document(document, STORAGE_SCHEMA_VERSION)
    message = str(exc.value)
    assert f"schema_version {STORAGE_SCHEMA_VERSION + 1} is newer" in message
    assert "upgrade the application rather than downgrading the data" in message


def test_a_document_without_an_integer_version_is_refused() -> None:
    document = _v1_document()
    document["schema_version"] = "1"
    with pytest.raises(ValueError, match="no integer schema_version"):
        migrate_document(document, STORAGE_SCHEMA_VERSION)


def test_no_migration_path_is_refused_rather_than_improvised() -> None:
    document = _v1_document()
    document["schema_version"] = 0
    with pytest.raises(ValueError, match="no migration path from stored schema_version 0"):
        migrate_document(document, STORAGE_SCHEMA_VERSION)


def test_a_current_document_is_returned_unchanged_with_no_notes() -> None:
    document = _v1_document(nbs_type=["tree_avenue"])
    document["schema_version"] = STORAGE_SCHEMA_VERSION
    migrated, notes = migrate_document(json.loads(json.dumps(document)), STORAGE_SCHEMA_VERSION)
    assert migrated == document
    assert notes == []


# --- Migration through the store and the API ---------------------------------


def test_reading_a_v1_project_does_not_persist_the_migration(storage_root: Path) -> None:
    """Opening a project to look at it never rewrites the user's data: the file
    is rewritten only when they next save."""
    original = _write(storage_root, _v1_document())
    store = ProjectStore(storage_root)

    project = store.load(_PROJECT_ID)
    assert project.schema_version == STORAGE_SCHEMA_VERSION
    assert project.assessments[0].input["nbs_type"] == ["street_tree_planting"]
    assert (storage_root / f"{_PROJECT_ID}.json").read_text(encoding="utf-8") == original

    # Reading twice yields the same migration: nothing accumulated on disk.
    assert store.load(_PROJECT_ID).migration_notes == project.migration_notes


def test_the_api_surfaces_the_migration_notes_on_the_project(
    client: TestClient, storage_root: Path
) -> None:
    """D-029/D-044.2: a user whose saved drafts were reshaped is told what
    changed, rather than discovering it."""
    _write(storage_root, _v1_document(nbs_type="schoolyard_greening"))
    body = client.get(f"/api/projects/{_PROJECT_ID}").json()

    assert body["schema_version"] == STORAGE_SCHEMA_VERSION
    assert body["assessments"][0]["input"]["nbs_type"] == ["schoolyard_greening"]
    notes = body["migrated_notes"]
    assert len(notes) == 2
    assert any("single-element list" in note for note in notes)
    assert any("re-select an intervention" in note for note in notes)


def test_a_project_written_by_this_build_carries_no_notes(client: TestClient) -> None:
    created = client.post("/api/projects", json={"name": "Riverside pilot"}).json()
    assert created["migrated_notes"] == []
    assert client.get(f"/api/projects/{created['project_id']}").json()["migrated_notes"] == []


def test_saving_a_migrated_project_writes_it_at_the_current_version(
    client: TestClient, storage_root: Path
) -> None:
    """The migration reaches disk only through an explicit user action."""
    _write(storage_root, _v1_document())
    assert client.patch(f"/api/projects/{_PROJECT_ID}", json={"name": "Renamed"}).status_code == 200

    stored = json.loads((storage_root / f"{_PROJECT_ID}.json").read_text(encoding="utf-8"))
    assert stored["schema_version"] == STORAGE_SCHEMA_VERSION
    assert stored["assessments"][0]["input"]["nbs_type"] == ["street_tree_planting"]
    # The notes describe an event, not the project, so they are never persisted.
    assert "migration_notes" not in stored
    assert "migrated_notes" not in stored


def test_a_migrated_draft_naming_a_retired_typology_still_refuses_to_evaluate(
    client: TestClient, storage_root: Path
) -> None:
    """Migration reshapes the answer; it does not make a retired slug scoreable.

    The user must re-select an intervention, which is exactly what the note says.
    """
    _write(
        storage_root,
        _v1_document(nbs_type="schoolyard_greening", site_area_m2=6000.0, climate_zone="temperate"),
    )
    response = client.post(
        f"/api/projects/{_PROJECT_ID}/assessments/{_ASSESSMENT_ID}/evaluate",
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "unknown nbs_type: 'schoolyard_greening'"}


def test_a_migrated_draft_naming_a_current_typology_evaluates(
    client: TestClient, storage_root: Path
) -> None:
    """A v1 draft whose slug still names an entry is scoreable once opened.

    ``pocket_park`` survived the library change, so the reshaped draft runs
    without the user touching it — the migration reshaped the answer and did
    not invalidate it.
    """
    _write(
        storage_root,
        _v1_document(nbs_type="pocket_park", site_area_m2=6000.0, climate_zone="temperate"),
    )
    response = client.post(f"/api/projects/{_PROJECT_ID}/assessments/{_ASSESSMENT_ID}/evaluate")
    assert response.status_code == 200
    result = response.json()["result"]
    assert result["typology"]["nbs_type"] == "pocket_park"
    assert result["package"]["component_count"] == 1
