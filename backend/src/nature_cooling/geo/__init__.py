"""Geographic lookups over the two bundled datasets (v2.1, D-047).

Three questions are answered here, and deliberately only three: how large a
drawn polygon is, which country a point falls in, and which climate zone a
point classifies to. That is the whole of what a map can fill in without
inventing anything — see docs/V2.1-BRIEF.md, which names the temptation this
boundary exists to refuse. Canopy cover, imperviousness, land-surface
temperature and land use are NOT derived here; deriving them from imagery is
the GIS workflow deferred by D-002, and generating the tool's most
decision-relevant site inputs from an unvalidated pipeline with no evidence
table behind it is the defect D-016 refused for cost defaults.

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
    load_basemap,
    load_countries,
    load_koppen,
)
from nature_cooling.geo.lookup import (
    ClimateLookup,
    CountryLookup,
    SiteLookup,
    look_up_site,
    polygon_area_m2,
)

__all__ = [
    "ClimateLookup",
    "CountryBoundaries",
    "CountryLookup",
    "GeoDataError",
    "KoppenGrid",
    "SiteLookup",
    "load_basemap",
    "load_countries",
    "load_koppen",
    "look_up_site",
    "polygon_area_m2",
]
