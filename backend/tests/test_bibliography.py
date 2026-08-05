"""The bibliography, parsed for serving (v2.6).

A citation key renders to users who do not have BIBLIOGRAPHY.md open, so the
parsed reference — the full citation with its DOI or URL — must be faithful to
the file, entry for entry. The parsing reuses the config loader's own key
pattern, so what is served and what citation checking accepts cannot drift.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from nature_cooling.bibliography import load_bibliography, references_for
from nature_cooling.engine.config import (
    ConfigError,
    bibliography_keys,
    collect_source_keys,
)


def test_every_declared_key_parses_to_a_reference() -> None:
    """The parsed entries are exactly the keys the citation check accepts."""
    entries = load_bibliography()
    assert set(entries) == bibliography_keys()
    for key, entry in entries.items():
        assert entry.reference, key
        assert "[" not in entry.reference and "*" not in entry.reference, key


def test_a_journal_entry_carries_its_doi_and_resolver_link() -> None:
    """The jacobs2020 line, exactly as the bibliography states it."""
    entry = load_bibliography()["jacobs2020"]
    assert entry.reference.startswith("Jacobs, C., Klok, L., Bruse, M.")
    assert "Urban Climate" in entry.reference
    assert "DOI:" not in entry.reference, "the DOI clause moves to its own fields"
    assert entry.doi == "10.1016/j.uclim.2020.100607"
    assert entry.url == "https://doi.org/10.1016/j.uclim.2020.100607"


def test_a_dataset_entry_without_a_doi_keeps_its_page_link() -> None:
    """The four non-journal entries carry an autolink instead of a DOI."""
    entry = load_bibliography()["naturalearth"]
    assert entry.doi is None
    assert entry.url == "https://www.naturalearthdata.com/"
    assert "<" not in entry.reference


def test_every_key_the_library_cites_resolves(config) -> None:
    """The dialog's promise: no citation key renders without its work."""
    cited = {s.key for a in config.typologies.archetypes for s in a.sources}
    served = references_for(cited)
    assert cited <= set(served)
    # The whole configuration's citations resolve too, not only the library's
    # (the methodology browser renders sources from every config file).
    everything = collect_source_keys(config.model_dump())
    assert everything <= set(served)


def test_a_missing_bibliography_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="missing bibliography"):
        load_bibliography(tmp_path / "BIBLIOGRAPHY.md")


def test_a_file_with_no_entries_raises(tmp_path: Path) -> None:
    empty = tmp_path / "BIBLIOGRAPHY.md"
    empty.write_text("# Bibliography\n\nNothing here.\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="no bibliography entries"):
        load_bibliography(empty)


def test_a_cited_key_the_parse_does_not_yield_raises(tmp_path: Path) -> None:
    """A parsing regression must fail loudly, never serve dangling citations."""
    partial = tmp_path / "BIBLIOGRAPHY.md"
    partial.write_text(
        "**`bowler2010`** — Bowler, D.E. (2010). A study. *Journal*, 1(1), 1–2. "
        "DOI: [10.1/x](https://doi.org/10.1/x)\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match=r"absent from the parsed bibliography: \['ziter2019'\]"):
        references_for({"bowler2010", "ziter2019"}, partial)
