"""Geographic lookups over the bundled datasets (v2.1, D-047; v2.2, D-049).

Three questions are answered here, and deliberately only three: how large a
drawn polygon is, which country a point falls in, and which climate zone a
point classifies to. That is the whole of what a map can fill in without
inventing anything — see docs/V2.1-BRIEF.md, which names the temptation this
boundary exists to refuse. Canopy cover, imperviousness, land-surface
temperature and land use are NOT derived here; deriving them from imagery is
the GIS workflow deferred by D-002, and generating the tool's most
decision-relevant site inputs from an unvalidated pipeline with no evidence
table behind it is the defect D-016 refused for cost defaults.

Place search (v2.2, D-049.6) is navigation, not a fourth answer: it finds a
named place for the map to move to, and fills in nothing.

Everything runs against files inside the package. No network request is made,
no geospatial library is imported, and nothing here needs one: a ray-cast
point-in-polygon test and an indexed lookup into a class grid are both a few
dozen lines of arithmetic, and `rasterio`/GDAL would trade the tool's
one-command install for a system-libraries install (D-033).
"""

from nature_cooling.geo.datasets import (
    CountryBoundaries,
    GeoDataError,
    KoppenGrid,
    Place,
    PlaceIndex,
    load_basemap,
    load_countries,
    load_koppen,
    load_places,
)
from nature_cooling.geo.lookup import (
    ClimateLookup,
    CountryLookup,
    SiteLookup,
    look_up_site,
    polygon_area_m2,
)
from nature_cooling.geo.places import search_places

__all__ = [
    "ClimateLookup",
    "CountryBoundaries",
    "CountryLookup",
    "GeoDataError",
    "KoppenGrid",
    "Place",
    "PlaceIndex",
    "SiteLookup",
    "load_basemap",
    "load_countries",
    "load_koppen",
    "load_places",
    "look_up_site",
    "polygon_area_m2",
    "search_places",
]
