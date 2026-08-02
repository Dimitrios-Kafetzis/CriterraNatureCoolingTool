"""Place search over the bundled populated-places index (v2.2, D-049.6).

Navigation, not autofill: a result carries a name and a coordinate for the map
to move to, and nothing here fills in an answer. The index is Natural Earth's
populated places — the same public-domain source and pinned release as the
boundary layers — so the search works with no network access of any kind,
which matters because it is the only navigation aid a deployment without
configured imagery has.

Matching is deliberately plain: case-insensitive prefix-then-substring over
the place name and its ASCII fold (so "malaga" finds Málaga), ranked by
population within each tier. 7,342 names is small enough that a linear scan
answers in well under a millisecond; an index structure would be complexity
without a measurable return.
"""

from __future__ import annotations

from nature_cooling.geo.datasets import Place, load_places

# Enough to disambiguate ("Springfield" appears repeatedly) without turning
# the result list into a scroll. The endpoint caps requests at this value.
MAX_RESULTS = 10

# One character matches a quarter of the index; two is where results start
# meaning something.
MIN_QUERY_LENGTH = 2


def search_places(query: str, limit: int = MAX_RESULTS) -> list[Place]:
    """Return the best-matching places for a user-typed query, best first."""
    needle = query.strip().casefold()
    if len(needle) < MIN_QUERY_LENGTH:
        return []
    limit = max(1, min(limit, MAX_RESULTS))

    # The index is population-descending (a property the loader's source data
    # guarantees), so scanning in order and collecting prefix matches before
    # substring matches yields ranked results with no sort at query time.
    prefix: list[Place] = []
    substring: list[Place] = []
    for place in load_places().places:
        name = place.name.casefold()
        ascii_name = place.ascii_name.casefold()
        if name.startswith(needle) or ascii_name.startswith(needle):
            prefix.append(place)
            if len(prefix) >= limit:
                break
        elif len(substring) < limit and (needle in name or needle in ascii_name):
            substring.append(place)
    return (prefix + substring)[:limit]
