"""Storage-layer tests, always against a temporary directory."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from nature_cooling.api.schemas import STORAGE_SCHEMA_VERSION, Project
from nature_cooling.api.storage import (
    ProjectNotFoundError,
    ProjectStore,
    default_storage_root,
    utc_now_iso,
)


def _project(
    project_id: str, name: str = "P", updated_at: str = "2026-07-30T10:00:00+00:00"
) -> Project:
    return Project(
        schema_version=STORAGE_SCHEMA_VERSION,
        project_id=project_id,
        name=name,
        created_at="2026-07-30T09:00:00+00:00",
        updated_at=updated_at,
        site={},
        assessments=[],
    )


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    project = _project("11111111-1111-4111-8111-111111111111")
    store.save(project)
    assert store.load(project.project_id) == project


def test_saved_files_are_pretty_printed_utf8_json(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    project = _project("11111111-1111-4111-8111-111111111111", name="Ágios Δήμος")
    store.save(project)
    text = (tmp_path / "projects" / f"{project.project_id}.json").read_text(encoding="utf-8")
    assert f'"schema_version": {STORAGE_SCHEMA_VERSION}' in text
    assert "Ágios Δήμος" in text  # ensure_ascii=False keeps names readable
    assert json.loads(text) == project.model_dump()


def test_save_leaves_no_temp_file_behind(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    store.save(_project("11111111-1111-4111-8111-111111111111"))
    assert [path.name for path in (tmp_path / "projects").iterdir()] == [
        "11111111-1111-4111-8111-111111111111.json"
    ]


def test_load_and_delete_raise_for_unknown_projects(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    with pytest.raises(ProjectNotFoundError):
        store.load("11111111-1111-4111-8111-111111111111")
    with pytest.raises(ProjectNotFoundError):
        store.delete("11111111-1111-4111-8111-111111111111")


def test_delete_removes_the_file(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    project = _project("11111111-1111-4111-8111-111111111111")
    store.save(project)
    store.delete(project.project_id)
    with pytest.raises(ProjectNotFoundError):
        store.load(project.project_id)


def test_list_all_is_empty_before_any_save(tmp_path: Path) -> None:
    assert ProjectStore(tmp_path / "projects").list_all() == []


def test_list_all_sorts_most_recently_updated_first(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    older = _project("11111111-1111-4111-8111-111111111111", updated_at="2026-07-30T10:00:00+00:00")
    newer = _project("22222222-2222-4222-8222-222222222222", updated_at="2026-07-30T11:00:00+00:00")
    store.save(older)
    store.save(newer)
    assert [item.project_id for item in store.list_all()] == [
        newer.project_id,
        older.project_id,
    ]


def test_an_unsupported_schema_version_is_refused() -> None:
    # The model always sees the current version: a document is validated only
    # after migration has run, so anything else is a build mismatch (D-029).
    document = _project("11111111-1111-4111-8111-111111111111").model_dump()
    document["schema_version"] = STORAGE_SCHEMA_VERSION + 1
    with pytest.raises(
        ValueError, match=f"unsupported storage schema_version {STORAGE_SCHEMA_VERSION + 1}"
    ):
        Project.model_validate(document)


def test_reading_a_v1_file_migrates_it_in_memory_and_leaves_the_file_alone(
    tmp_path: Path,
) -> None:
    """D-029/D-044.2: migration happens on read, is itemised, and is not persisted.

    Opening a project to look at it never rewrites the user's data; the file is
    rewritten only when they next save.
    """
    root = tmp_path / "projects"
    root.mkdir(parents=True)
    project_id = "11111111-1111-4111-8111-111111111111"
    document = {
        "schema_version": 1,
        "project_id": project_id,
        "name": "P",
        "created_at": "2026-07-30T09:00:00+00:00",
        "updated_at": "2026-07-30T10:00:00+00:00",
        "site": {},
        "assessments": [
            {
                "assessment_id": "22222222-2222-4222-8222-222222222222",
                "label": "Option A",
                "created_at": "2026-07-30T09:30:00+00:00",
                "input": {"nbs_type": "street_tree_planting", "site_area_m2": 6000.0},
                "result": None,
            }
        ],
    }
    path = root / f"{project_id}.json"
    original = json.dumps(document, indent=2)
    path.write_text(original, encoding="utf-8")

    loaded = ProjectStore(root).load(project_id)
    assert loaded.schema_version == STORAGE_SCHEMA_VERSION
    assert loaded.assessments[0].input["nbs_type"] == ["street_tree_planting"]
    assert loaded.migration_notes, "a migrated document must itemise what changed"
    assert path.read_text(encoding="utf-8") == original


def test_utc_now_iso_is_iso8601_utc() -> None:
    stamp = utc_now_iso()
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+\+00:00", stamp)


def test_default_storage_root_is_a_per_user_application_directory() -> None:
    root = default_storage_root()
    assert root.name == "projects"
    assert "criterra-nature-cooling" in str(root)
