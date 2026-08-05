"""The shipped library must match the approved curation, entry for entry.

Two curation records govern the library, and the shipped catalogue is exactly
their union:

* `v1.2-curation.json` / `v1.2-availability-matrix.json` — which of the 243
  entries of the UNEP catalogue survive, which archetype each inherits, and
  where each is offered.
* `v2.5-curation.json` / `v2.5-availability-matrix.json` — the same three
  questions for the 143 entries of the supplementary proposal, of which 11 were
  accepted, 58 merged onto entries the catalogue already had, and 74 dropped.

Generated data drifts. These tests compare records and configuration directly,
so a hand edit that quietly disagrees with an approved curation fails the build
and names the entry — rather than being discovered by a reviewer reading 386
rows, or not at all.
"""

from __future__ import annotations

import json

import pytest

from nature_cooling.engine.config import repo_root

ASSETS = repo_root() / "docs" / "assets"

# The curation asset was produced BEFORE the six structural rulings, and D-043.1
# overrode it for exactly two entries: schoolyard greening was marked *keep* but
# is retired as a land-use context, and green playground was marked *merge into
# schoolyard greening* and therefore becomes the canonical entry in its place.
# Both are named here so the override is documented rather than absorbed into a
# looser assertion — and so a third divergence cannot appear unnoticed.
RULING_OVERRIDES = {
    "3.6": "kept by the curation, retired by D-043.1 as a land-use context",
    "3.15": "merged by the curation, canonical after D-043.1 retired its target",
}


def _load(name: str) -> dict[str, dict]:
    entries = json.loads((ASSETS / name).read_text(encoding="utf-8"))
    return {entry["id"]: entry for entry in entries}


@pytest.fixture(scope="module")
def curation_v12() -> dict[str, dict]:
    return _load("v1.2-curation.json")


@pytest.fixture(scope="module")
def curation_v25() -> dict[str, dict]:
    return _load("v2.5-curation.json")


@pytest.fixture(scope="module")
def curation(curation_v12: dict[str, dict], curation_v25: dict[str, dict]) -> dict[str, dict]:
    """Both records as one lookup. Safe only because the ids are disjoint."""
    return {**curation_v12, **curation_v25}


@pytest.fixture(scope="module")
def matrix() -> dict[str, dict]:
    return {**_load("v1.2-availability-matrix.json"), **_load("v2.5-availability-matrix.json")}


def test_the_two_record_id_namespaces_do_not_overlap(
    curation_v12: dict[str, dict], curation_v25: dict[str, dict]
) -> None:
    """The reason the supplementary ids carry an `S` prefix.

    The supplementary document renumbers from scratch and collides with the
    243-entry catalogue on seventeen ids. The one that makes this a correctness
    problem rather than a tidiness one is 7.14: it names a *shipped* entry in
    the first document (coastal ecological corridor) and a *dropped* one in the
    second (bat flyway). Merging the records on raw source numbers would make a
    dropped entry appear to ship. This test is what keeps the two apart.
    """
    assert not (set(curation_v12) & set(curation_v25))
    assert all(entry["id"] == "S" + entry["source_ref"] for entry in curation_v25.values())
    collisions = {entry["source_ref"] for entry in curation_v25.values()} & set(curation_v12)
    assert "7.14" in collisions, "the motivating collision must still be one"


def test_the_curation_still_reduces_243_entries_to_110(curation_v12: dict[str, dict]) -> None:
    """The headline of D-043: 110 kept, 88 merged, 45 dropped."""
    assert len(curation_v12) == 243
    decisions = [entry["decision"] for entry in curation_v12.values()]
    assert decisions.count("keep") == 110
    assert decisions.count("merge") == 88
    assert decisions.count("drop") == 45


def test_the_supplement_reduces_143_entries_to_11(curation_v25: dict[str, dict]) -> None:
    """The headline of the v2.5 curation: 11 kept, 58 merged, 74 dropped.

    The keep rate is 8% against v1.2's 45%, and that is the finding rather than
    a defect: the supplementary document extends the catalogue sideways into
    bank and slope engineering, wastewater treatment, marine ecology, habitat
    furniture, soil science, maintenance regimes and buried drainage, and six
    of its groups state in their own classification notes that they are
    supporting or enabling layers rather than interventions.
    """
    assert len(curation_v25) == 143
    decisions = [entry["decision"] for entry in curation_v25.values()]
    assert decisions.count("keep") == 11
    assert decisions.count("merge") == 58
    assert decisions.count("drop") == 74


def test_the_expansion_introduced_no_new_archetype(config) -> None:
    """The load-bearing claim of the v2.5 curation.

    Every accepted entry inherits one of the eighteen evidence classes that
    already existed, so the expansion added no envelope, no citation and no new
    literature. An entry that could not inherit honestly was dropped rather
    than given a class invented for it.
    """
    assert len(config.typologies.archetypes) == 18
    supplementary = [t for t in config.typologies.resolved if t.nbs_id.startswith("S")]
    assert len(supplementary) == 11
    existing = {a.archetype for a in config.typologies.archetypes}
    assert {t.archetype for t in supplementary} <= existing


def test_the_two_ruling_overrides_are_exactly_the_ones_documented(
    config, curation: dict[str, dict]
) -> None:
    """D-043.1 overrode the curation for two entries, and only those two.

    The asset was produced before the structural rulings, so a divergence
    between it and the library is either one of these two — documented,
    deliberate — or a defect. This test is what keeps that distinction sharp.
    """
    shipped = {typology.nbs_id for typology in config.typologies.resolved}
    diverging = {
        entry_id
        for entry_id, entry in curation.items()
        if (entry["decision"] == "keep") != (entry_id in shipped)
    }
    assert diverging == set(RULING_OVERRIDES), (
        f"divergences: {sorted(diverging)}; documented: {sorted(RULING_OVERRIDES)}"
    )
    assert "3.6" not in shipped, "schoolyard greening is retired as a typology (D-043.1)"
    assert "3.15" in shipped, "green playground is canonical in its place (D-043.1)"


def test_every_shipped_entry_is_an_approved_one(config, matrix: dict[str, dict]) -> None:
    """No entry may appear in the library that the curation did not keep."""
    shipped = {typology.nbs_id for typology in config.typologies.resolved}
    assert shipped == set(matrix), {
        "in the library but not approved": sorted(shipped - set(matrix)),
        "approved but missing from the library": sorted(set(matrix) - shipped),
    }


def test_every_entry_inherits_the_archetype_it_was_mapped_to(
    config, matrix: dict[str, dict]
) -> None:
    """Part 3's entry-to-archetype mapping, asserted row by row.

    This is the mapping that decides which cited evidence an entry reports on,
    so a silent change here would restate an entry's cooling on the wrong
    literature — the single failure mode the archetype model exists to prevent.
    """
    wrong = {
        typology.nbs_id: (matrix[typology.nbs_id]["archetype"], typology.archetype)
        for typology in config.typologies.resolved
        if typology.archetype != matrix[typology.nbs_id]["archetype"]
    }
    assert not wrong, (
        f"archetype mapping differs from the approved pack (approved, shipped): {wrong}"
    )


def test_every_entry_reports_the_envelope_its_archetype_was_approved_with(
    config, matrix: dict[str, dict]
) -> None:
    """The one deliberate exception is `large_water_body` (D-045.1).

    Its floor was lowered from 0.5 to 0.1 °C at implementation, because source
    verification found the pack had attributed to `yao2023a` a figure the paper
    does not contain. Every other envelope must match the pack exactly, and
    this test states the exception rather than hiding it in a tolerance.
    """
    corrected = {"large_water_body": (0.1, 3.0)}
    for typology in config.typologies.resolved:
        approved = matrix[typology.nbs_id]
        shipped = (typology.temp_reduction_min_c, typology.temp_reduction_max_c)
        expected = corrected.get(
            typology.archetype, (approved["temp_min_c"], approved["temp_max_c"])
        )
        assert shipped == expected, (
            f"{typology.nbs_id} ({typology.nbs_type}) reports {shipped}, approved {expected}"
        )


def test_the_corrected_envelope_is_the_only_one_that_moved(config, matrix: dict[str, dict]) -> None:
    """State the exception as a count, so a second one cannot slip in beside it."""
    moved = {
        typology.archetype
        for typology in config.typologies.resolved
        if (typology.temp_reduction_min_c, typology.temp_reduction_max_c)
        != (matrix[typology.nbs_id]["temp_min_c"], matrix[typology.nbs_id]["temp_max_c"])
    }
    assert moved == {"large_water_body"}


def test_availability_matches_the_approved_matrix(config, matrix: dict[str, dict]) -> None:
    """Scales, land uses and the four conditions, entry by entry."""
    for typology in config.typologies.resolved:
        approved = matrix[typology.nbs_id]
        where = f"{typology.nbs_id} ({typology.nbs_type})"

        assert set(typology.availability.scales) == set(approved["scales"]), where

        approved_uses = approved["land_uses"]
        if approved_uses == "all":
            assert typology.availability.land_uses == "all", where
        else:
            assert set(typology.typical_use_context) == set(approved_uses), where

        approved_water = approved["requires_waterfront"]
        if approved_water in (None, "none"):
            assert typology.availability.requires_waterfront is None, where
        else:
            assert typology.availability.requires_waterfront is not None, where
            assert set(typology.availability.requires_waterfront) == {
                value.replace(" ", "_") for value in approved_water
            }, where

        assert typology.availability.requires_railway == bool(approved["requires_railway"]), where
        assert typology.availability.requires_existing_woodland == bool(
            approved["requires_existing_woodland"]
        ), where
        assert typology.availability.requires_governance == approved["governance"], where


def test_display_names_match_the_approved_curation(config, matrix: dict[str, dict]) -> None:
    """A renamed entry is a decision, not an edit (D-043.4 renamed exactly one)."""
    wrong = {
        typology.nbs_id: (matrix[typology.nbs_id]["name"], typology.display_name)
        for typology in config.typologies.resolved
        if typology.display_name != matrix[typology.nbs_id]["name"]
    }
    assert not wrong, f"display names differ from the approved pack: {wrong}"


def test_the_curation_reasons_are_preserved_as_cooling_mechanisms(
    config, curation: dict[str, dict]
) -> None:
    """Each entry describes its own mechanism, not its archetype's.

    The mechanism is descriptive text that reaches the recommendation, so it is
    per entry — a stormwater tree pit and a tree avenue inherit the same
    evidence class but do not cool by the same means.
    """
    for typology in config.typologies.resolved:
        assert (
            typology.primary_cooling_mechanism == (curation[typology.nbs_id]["cooling_mechanism"])
        ), typology.nbs_id


def test_no_dropped_or_merged_entry_reappears(config, curation: dict[str, dict]) -> None:
    """A merged entry must not also ship on its own (D-043's merge chains)."""
    shipped = {typology.nbs_id for typology in config.typologies.resolved}
    unexpected = {
        entry_id: entry["decision"]
        for entry_id, entry in curation.items()
        if entry["decision"] in ("merge", "drop")
        and entry_id in shipped
        and entry_id not in RULING_OVERRIDES
    }
    assert not unexpected, f"entries the curation removed but the library ships: {unexpected}"


def test_the_retired_land_use_contexts_were_all_dropped(curation: dict[str, dict]) -> None:
    """D-043.1: hospital, campus, memorial landscapes and schoolyard greening.

    Schoolyard greening is the one the curation marked *keep* and the ruling
    overrode, so its absence from the library is checked here against the
    ruling rather than against the asset.
    """
    for entry_id in ("3.7", "3.8", "3.10"):
        assert curation[entry_id]["decision"] == "drop", entry_id
    assert curation["3.6"]["name"] == "Schoolyard Greening"
    assert curation["3.15"]["name"] == "Green Playground"


def test_the_assets_are_committed_where_the_documentation_says() -> None:
    """The approved data must travel with the repository, not with a session."""
    assert (ASSETS / "v1.2-curation.json").is_file()
    assert (ASSETS / "v1.2-availability-matrix.json").is_file()
    assert (ASSETS / "v2.5-curation.json").is_file()
    assert (ASSETS / "v2.5-availability-matrix.json").is_file()
