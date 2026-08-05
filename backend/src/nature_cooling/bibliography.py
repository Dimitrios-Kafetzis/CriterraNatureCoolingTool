"""The bibliography, parsed for serving: full references behind the citation keys.

A citation key like ``jacobs2020`` is traceable only next to the bibliography,
which ships in ``docs/methodology/BIBLIOGRAPHY.md`` (and inside the wheel, for
the config loader's citation check). The detail dialog and the methodology
browser render source keys to users who do not have that file open, so this
module parses each entry's reference line — the full citation, and the DOI or
URL it links — into data the API can serve beside the library. The findings
stay where they always were, on the archetype's ``sources``; what is added is
the work each key names.

Nothing here is new content: every served reference is the bibliography's own
line, markdown stripped, with the link it already carried. A cited key with no
bibliography entry is impossible by construction — the config loader refuses
to load a configuration citing an unknown key — and this module still checks,
so a parsing regression cannot silently serve a library whose citations
resolve to nothing.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType

from nature_cooling.engine.config import ConfigError, default_bibliography_path

# One entry's reference line: the key, then the full citation to end of line.
_ENTRY_PATTERN = re.compile(r"^\*\*`([a-z0-9]+)`\*\*\s*—\s*(.+)$", re.MULTILINE)
# The DOI clause most entries end with: ``DOI: [10.xxxx/…](https://doi.org/…)``.
_DOI_PATTERN = re.compile(r"\s*DOI:\s*\[([^\]]+)\]\((https?://[^)]+)\)\.?")
# The autolink the non-journal entries carry instead: ``<https://…>``.
_AUTOLINK_PATTERN = re.compile(r"\s*<(https?://[^>]+)>\.?")
# Any remaining inline markdown link, kept as its text.
_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\((?:https?://[^)]+)\)")


@dataclass(frozen=True)
class SourceReference:
    """One bibliography entry's citation, as the interface renders it.

    ``reference`` is the full citation in plain text (authors, year, title,
    venue). ``doi`` is the DOI as printed, when the entry has one; ``url`` is
    the link the bibliography carries — the DOI resolver or the publisher or
    dataset page. A link the user clicks is not a request the app makes
    (the D-051.3 reading), so serving it leaves the request gates untouched.
    """

    reference: str
    doi: str | None
    url: str | None


def _parse_reference(line: str) -> SourceReference:
    doi: str | None = None
    url: str | None = None
    matched = _DOI_PATTERN.search(line)
    if matched:
        doi, url = matched.group(1), matched.group(2)
        line = _DOI_PATTERN.sub("", line, count=1)
    else:
        autolink = _AUTOLINK_PATTERN.search(line)
        if autolink:
            url = autolink.group(1)
            line = _AUTOLINK_PATTERN.sub("", line, count=1)
    line = _LINK_PATTERN.sub(r"\1", line)
    reference = " ".join(line.replace("*", "").split()).strip()
    return SourceReference(reference=reference, doi=doi, url=url)


@lru_cache(maxsize=4)
def load_bibliography(path: Path | None = None) -> Mapping[str, SourceReference]:
    """Parse every bibliography entry into its reference, keyed by citation key.

    The key pattern is the config loader's own (``**`key`**``), so what this
    serves and what citation checking accepts cannot drift apart.
    """
    bibliography = path if path is not None else default_bibliography_path()
    if not bibliography.is_file():
        raise ConfigError(f"missing bibliography: {bibliography}")
    text = bibliography.read_text(encoding="utf-8")
    entries = {key: _parse_reference(line) for key, line in _ENTRY_PATTERN.findall(text)}
    if not entries:
        raise ConfigError(f"no bibliography entries parsed from {bibliography}")
    return MappingProxyType(entries)


def references_for(cited_keys: set[str], path: Path | None = None) -> dict[str, SourceReference]:
    """Every parsed reference, after checking the cited keys all resolve.

    The whole bibliography is served rather than the cited subset: the
    methodology browser cites keys from every configuration file, not only the
    library, and the bibliography is public in full anyway.
    """
    entries = load_bibliography(path)
    missing = sorted(cited_keys - set(entries))
    if missing:
        raise ConfigError(f"cited sources absent from the parsed bibliography: {missing}")
    return dict(entries)
