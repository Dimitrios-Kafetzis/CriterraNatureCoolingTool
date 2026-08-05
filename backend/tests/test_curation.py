"""The published curation records, read for the per-entry reason (v2.6).

Unlike the image manifest, absence is not an expected state here: every shipped
entry has an approved curation reason, enforced entry for entry by
``test_catalogue_fidelity.py``, so a missing record or an unexplained entry is
a packaging defect and must raise rather than render around.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from nature_cooling.curation import (
    CURATION_RECORD_FILES,
    CurationDataError,
    curation_reasons_for,
    load_curation_reasons,
)
from nature_cooling.engine.config import default_curation_records_dir, repo_root


def test_the_default_records_dir_is_the_repository_checkout() -> None:
    assert default_curation_records_dir() == repo_root() / "docs" / "assets"


def test_every_shipped_entry_has_a_reason(config) -> None:
    """The join the detail dialog depends on: nbs_id is the curation id."""
    reasons = curation_reasons_for(config.typologies)
    assert set(reasons) == {t.nbs_id for t in config.typologies.resolved}
    assert all(reason.strip() for reason in reasons.values())
    # Two spot checks against the records as written, one per record: the
    # v1.2 keep for strategic tree planting and the v2.5 keep for depaving.
    assert reasons["A1"].startswith("Deliberately sited single tree")
    assert reasons["SA16"].startswith("The deliberate removal of sealed surface")


def test_reasons_load_from_both_records_into_one_disjoint_lookup() -> None:
    reasons = load_curation_reasons()
    # 243 v1.2 entries + 143 supplementary entries, ids disjoint by S-prefix.
    assert len(reasons) == 243 + 143
    assert "7.14" in reasons and "S7.14" in reasons


def test_a_missing_record_raises_rather_than_serving_a_partial_answer(tmp_path: Path) -> None:
    with pytest.raises(CurationDataError, match="missing curation record"):
        load_curation_reasons(tmp_path)


def _stage_records(target: Path) -> None:
    source = default_curation_records_dir()
    for name in CURATION_RECORD_FILES:
        shutil.copy(source / name, target / name)


def test_a_corrupt_record_raises(tmp_path: Path) -> None:
    _stage_records(tmp_path)
    (tmp_path / CURATION_RECORD_FILES[0]).write_text("{not json", encoding="utf-8")
    with pytest.raises(CurationDataError, match="invalid JSON"):
        load_curation_reasons(tmp_path)


def test_a_record_that_is_not_an_array_raises(tmp_path: Path) -> None:
    _stage_records(tmp_path)
    (tmp_path / CURATION_RECORD_FILES[0]).write_text("{}", encoding="utf-8")
    with pytest.raises(CurationDataError, match="JSON array"):
        load_curation_reasons(tmp_path)


def test_an_entry_without_id_or_reason_raises(tmp_path: Path) -> None:
    _stage_records(tmp_path)
    (tmp_path / CURATION_RECORD_FILES[0]).write_text(
        json.dumps([{"id": "A1", "reason": ""}]), encoding="utf-8"
    )
    with pytest.raises(CurationDataError, match="lacks an id or a reason"):
        load_curation_reasons(tmp_path)


def test_a_shipped_entry_the_records_do_not_explain_raises(config, tmp_path: Path) -> None:
    """An installed wheel must be exactly as honest as a checkout."""
    _stage_records(tmp_path)
    first = CURATION_RECORD_FILES[0]
    loaded = json.loads((tmp_path / first).read_text(encoding="utf-8"))
    trimmed = [entry for entry in loaded if entry["id"] != "A1"]
    (tmp_path / first).write_text(json.dumps(trimmed), encoding="utf-8")
    with pytest.raises(CurationDataError, match=r"absent from the curation records: \['A1'\]"):
        curation_reasons_for(config.typologies, tmp_path)
