# Hosting and Configuration

How to run this tool for other people, and the one setting a deployment can
configure: map imagery. Written for the operator of a deployment — a company
hosting it for its users, an institution running it on its own premises —
rather than for a developer. The decisions behind everything on this page are
recorded in [DECISIONS.md](DECISIONS.md) (D-035 for packaging, D-049 for
imagery).

## Running the application

One command, either way:

```bash
pip install "criterra-nature-cooling[serve]"
nature-cooling serve                      # http://127.0.0.1:8000
```

or, with the published container image, `docker compose up -d` against the
repository's [`compose.yaml`](https://github.com/Dimitrios-Kafetzis/CriterraNatureCoolingTool/blob/main/compose.yaml),
which also mounts a named volume so saved projects survive container
replacement.

## What a deployment that configures nothing gets

Everything, except street-level imagery. The assessment questionnaire, the
typology catalogue, the reports, and the map itself all work offline: the map
draws bundled country outlines (Natural Earth), identifies the country and
climate zone of any clicked point from data inside the package, computes a
drawn site's area, and finds 7,342 cities and towns by name through its place
search — all with **no network request to anyone**. This is the default on
purpose. It is what makes the tool deployable inside restricted networks, and
it is enforced by CI: an unconfigured installation is driven headlessly through
a complete assessment on every build and asserted to make zero external
requests (D-049.8).

What the bundled map cannot do is show streets and buildings, because a
world-scale basemap at street zoom cannot ship inside a Python wheel. That is
the one thing this page's setting adds.

## Enabling map imagery

An operator supplies two values — a raster tile URL template and the credit
line that tile source requires. Both, or neither: the application refuses to
start with a URL and no attribution, because imagery must never render
uncredited (D-049.2).

As environment variables (what a container deployment uses — see the commented
example in `compose.yaml`):

```bash
export NATURE_COOLING_TILE_URL="https://tiles.example.com/{z}/{x}/{y}.png?key=YOUR_KEY"
export NATURE_COOLING_TILE_ATTRIBUTION="© OpenStreetMap contributors © Example Tiles"
nature-cooling serve
```

Or as flags, for a one-command local run (they set the same variables):

```bash
nature-cooling serve \
  --tile-url "https://tiles.example.com/{z}/{x}/{y}.png?key=YOUR_KEY" \
  --tile-attribution "© OpenStreetMap contributors © Example Tiles"
```

The template must contain `{z}`, `{x}` and `{y}`, which the browser expands
per tile. There is no config file — these two variables are the application's
entire runtime configuration.

With a source configured, every user of that deployment sees imagery by
default, credited on the map. Each user can still turn it off for their visit,
or substitute a source of their own; neither choice is saved (D-049.4). If the
configured source is unreachable from a user's network, the map falls back to
the bundled outlines and says so — a restricted-network deployment that was
configured optimistically still works.

## Choosing a tile provider

**Do not use `tile.openstreetmap.org`.** OpenStreetMap's own tile servers are
community-funded donated infrastructure, run by the OSM Foundation with a
[Tile Usage Policy](https://operations.osmfoundation.org/policies/tiles/) that
forbids bulk and offline use, requires identifying User-Agents, and warns that
access — particularly for commercial services — may be blocked or withdrawn
without notice. A product deployment needs a provider it has an agreement
with, not a donation it silently consumes. This application therefore ships no
default tile host and never will: the operator's choice of provider is a real
choice, made deliberately.

The appropriate route is an **OSM-data provider** — a company that renders
OpenStreetMap data and serves tiles under commercial terms, with free tiers
that comfortably cover a screening tool's traffic:

| Provider | Notes |
|---|---|
| [MapTiler](https://www.maptiler.com/) | Raster and vector tiles, free tier, key in URL |
| [Stadia Maps](https://stadiamaps.com/) | Includes the former Stamen styles |
| [Geoapify](https://www.geoapify.com/) | Raster XYZ tiles, free tier |
| [Thunderforest](https://www.thunderforest.com/) | OpenCycleMap heritage, raster XYZ |
| [Carto](https://carto.com/) | Basemap styles over OSM data |
| Self-hosted | Render your own tiles from an OSM extract (e.g. an [OpenMapTiles](https://openmaptiles.org/) / TileServer GL stack) — the right answer for a fully offline estate |

Any of them hands you an XYZ template of exactly the shape
`NATURE_COOLING_TILE_URL` expects. Aerial/satellite imagery providers work the
same way if photography rather than cartography is wanted.

### Attribution is part of the licence, not a courtesy

Almost every provider above renders **OpenStreetMap data**, which is licensed
under the [ODbL](https://opendatacommons.org/licenses/odbl/1-0/). A rendered
raster tile is a *Produced Work* under that licence: share-alike does not
reach it (§4.4.7), but public use requires a notice "reasonably calculated" to
tell viewers the content came from OpenStreetMap (§4.3) — in practice, **"©
OpenStreetMap contributors" visible on the map**, plus whatever credit your
provider's terms add. That is why the attribution is a required half of the
configuration and is rendered on the map whenever the layer is on: the
application makes the compliant path the only path. Your provider's
documentation states the exact line to use; put it in
`NATURE_COOLING_TILE_ATTRIBUTION` verbatim.

No OpenStreetMap data is bundled in the package itself — tiles are requested
by each user's browser directly from your provider at runtime (D-049.3,
D-049.7).

### Restricting your API key

Tiles are requested **browser-direct**, so your provider key appears in the
tile URLs any user of your deployment can see. This is normal for raster tile
services and is managed, not hidden: every provider above lets you restrict a
key so it only answers requests originating from your deployment's domain
(checked via the HTTP `Referer`/`Origin`) — MapTiler calls this "allowed
HTTP origins", Stadia "domain restriction", Geoapify and Thunderforest offer
the same in their dashboards. Restrict the key to your domain when you create
it, and a copied key is useless anywhere else. The alternative — proxying
tiles through this application's backend to keep the key secret — was
considered and rejected (D-049.3): it would make the backend an outbound HTTP
client for the first time and spend the operator's bandwidth to solve a
problem key restriction already solves.

### Privacy note for your users

With imagery on, each user's browser talks to the tile provider directly, so
the provider sees that user's IP address and the map areas they view — the
same disclosure any map-embedding website makes. Nothing about the user's
assessment is ever sent to the provider, and the application's own backend
makes no third-party request whether imagery is configured or not. The
in-application disclosure text states all of this next to the imagery
controls.

## Reference

| Variable | Meaning |
|---|---|
| `NATURE_COOLING_TILE_URL` | Raster tile URL template with `{z}`, `{x}`, `{y}` placeholders. Unset ⇒ offline map, no third-party requests. |
| `NATURE_COOLING_TILE_ATTRIBUTION` | Credit line rendered on the map while the layer is on. Required whenever the URL is set. |

| CLI flag | Equivalent |
|---|---|
| `--tile-url` | sets `NATURE_COOLING_TILE_URL` |
| `--tile-attribution` | sets `NATURE_COOLING_TILE_ATTRIBUTION` |
| `--host`, `--port` | bind address and port (unchanged since D-036) |
