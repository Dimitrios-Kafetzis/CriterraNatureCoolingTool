# Bundled geographic datasets

Two published datasets ship inside this tool, in `data/geo/`, and are staged
into the distributable wheel alongside `config/` and the bibliography (D-036).
They exist so that the map-based site picker introduced in v2.1 works with **no
network access of any kind** — the country and climate-zone lookups it performs
are answered entirely from these files (D-047.1).

Neither file is the publisher's original. Both were derived from it by
[`tools/build_datasets.py`](../../tools/build_datasets.py), which records the
source URL and checksum of each input and states what was discarded. Run that
script to reproduce these files from the published sources.

Full licence texts accompany the data in this directory, in the same
arrangement the redistributed typefaces use
(`backend/src/nature_cooling/report/fonts/`): a summary here, the complete
upstream text in a file of its own.

---

## Country boundaries — Natural Earth

**Files:** `countries.json.z` (lookup), `basemap.json` (drawing), licence
`LICENCE-naturalearth.txt`

Natural Earth, *Admin 0 – Countries*, release **v5.1.2**, at two scales.
<https://www.naturalearthdata.com/>

*Use:* point-in-polygon identification of the country a mapped site falls in,
which feeds only the electricity-grid emission-factor and currency defaults;
and the country outlines the offline basemap draws.

*Licence:* **public domain.** Natural Earth states that all versions of its
data are in the public domain and that no permission, fee or attribution is
required. Attribution is given here regardless, because a reader is entitled to
know where a boundary the tool asserts came from.

*Why two scales.* The two jobs want opposite things, and one file cannot serve
both well:

- **`countries.json.z` — 1:50m**, the layer the lookup reads, zlib-compressed
  to 438 KB. At 1:110m, Natural Earth omits every country smaller than roughly
  a thousand square kilometres, so a click on Singapore falls through to
  Malaysia and a click on Monaco to France. A wrong country stated confidently
  is worse than no country at all, and it is wrong for exactly the dense hot
  coastal cities this tool exists to serve. The v2.1 brief cited the 1:110m
  file's size as evidence that bundling was affordable; it is, and so is this.
- **`basemap.json` — 1:110m**, the layer the browser draws, 159 KB of outlines
  with no attributes. It is rendered at world zoom, where 1:50m detail is
  invisible and its ten-times vertex count is pure cost.

*What was changed:* every attribute except the ISO 3166-1 alpha-2 and alpha-3
codes and the country name was discarded (the basemap layer keeps only the
outlines); coordinates were rounded to two decimal places; and a bounding box
was precomputed per entry. Two decimal places is roughly 1.1 km — tested
against the unrounded source over thirty capitals, the rounding changes no
identification. A ring that rounding collapsed below a triangle would have been
dropped; none was.

*Territories with no ISO code.* Four entries carry no ISO 3166-1 code in the
source: Northern Cyprus, Somaliland, Kosovo and the Siachen Glacier. They are
**not** assigned to the state that claims them, and they are **not** simply
deleted either. They are kept as `unassigned` outlines, and a site inside one
of them returns no country, definitively. Deleting them would have left holes
that the lookup's coastal tolerance (below) then filled by proximity — handing
a site in Northern Cyprus to Cyprus by accident, which is precisely the claim
the omission was making a point of not stating. The user types the code they
consider correct.

*Coastal tolerance.* A point that falls inside no boundary at all is attributed
to the nearest country within **25 km**, and otherwise to none. This is not a
guess about sovereignty; it is an acknowledgement that a generalised coastline
is drawn inland of the real one. Tested against the unrounded source, Beirut,
Nicosia, Manama, Kingston, Banjul, Monaco and Hong Kong all fall in the sea by
a few kilometres, and refusing to name a country for a waterfront site in
Beirut would be precision the data does not have. The tolerance is far narrower
than any open-water distance, so a genuinely offshore point still returns
nothing, and it never runs when the point is inside a boundary — so it cannot
override a containment match or choose between neighbours at a land border. The
lookup records which of the two ways it reached its answer.

*Verified:* Full. Release v5.1.2 retrieved from the project repository, both
scales recorded by SHA-256 in the build script.

---

## Climate classification — Köppen–Geiger (Beck et al. 2023)

**Files:** `koppen_geiger.json` (metadata and legend),
`koppen_geiger_1991_2020_0p1.bin.z` (the class grid), licence
`LICENCE-koppen-CC-BY-4.0.txt`

Beck, H.E., McVicar, T.R., Vergopolan, N., Berg, A., Lutsko, N.J., Dufour, A.,
Zeng, Z., Jiang, X., van Dijk, A.I.J.M., Miralles, D.G. (2023).
*High-resolution (1 km) Köppen-Geiger maps for 1901–2099 based on constrained
CMIP6 projections.* **Scientific Data 10, 724.**
doi:[10.1038/s41597-023-02549-6](https://doi.org/10.1038/s41597-023-02549-6)

*Use:* classification of a mapped point into one of the 30 Köppen–Geiger
classes, which the methodology's documented mapping table
(`config/climate_classification.yaml`) resolves to one of the tool's six
climate zones.

*Licence:* **CC BY 4.0**, which permits redistribution, including commercially,
with attribution. This is the same licence basis on which the `ember` emission
factors already ship inside the wheel, so the redistribution precedent was
already set by D-036 and no new licensing question arises.

*What was changed:* the published archive spans six periods, seven future
scenarios and four resolutions across 73 files and 125 MB. One file is used:
the **present-day period, 1991–2020, at 0.1°**. Its 1800 × 3600 grid of class
indices was extracted and zlib-compressed to 162 KB. Nothing was resampled,
reprojected or reclassified — the class indices are the publisher's, and the
legend in `koppen_geiger.json` is copied from the archive's `legend.txt`.

*Why 0.1° and not the 1 km layer:* the brief requires the coarsest layer that
classifies correctly, not the finest available. Measured against the published
1 km layer over 75 world cities, the 0.1° layer reproduces the tool's six-zone
answer for 71 of them, the 0.5° layer for 69 and the 1° layer for 68. The four
0.1° disagreements sit on steep gradients and coastlines — Rio de Janeiro,
Windhoek, Anchorage, Ulaanbaatar — whereas at 0.5° the errors begin landing on
ordinary inland cities such as Denver and Nairobi, which is the failure that
would matter. 0.1° costs 162 KB against the 1 km layer's 12 MB, for four cities
in seventy-five.

*A limit worth stating:* 0.1° is roughly 11 km. The classification is
trustworthy for the city a site sits in and is not a statement about the site
itself. That is the resolution at which climate zone enters this methodology
anyway — it selects a row of the climate adjustment matrix, not a temperature.

*Verified:* Full. Licence, period, resolution and the 30-class legend confirmed
against the published archive, whose MD5 is recorded in the build script.
