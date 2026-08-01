#!/usr/bin/env bash
# Build the distributable wheel with the app embedded (D-035).
#
# The wheel must carry everything an installed package needs and a checkout
# provides implicitly: the production frontend build (served at `/`), the
# methodology configuration, the bibliography its citation check reads, and the
# two bundled geographic datasets the map picker looks sites up in — with their
# attribution notices, which their licences require to travel with them (D-047.1).
# All four are staged into src/nature_cooling/_bundled — gitignored, admitted
# into the wheel by the hatchling `artifacts` setting, and removed again on
# exit so a checkout never shadows the live repository files.
#
# Requires: Node 18+ (frontend build) and `build` in the Python environment
# (ships with the backend `dev` extra).

set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
bundled="$root/backend/src/nature_cooling/_bundled"

cleanup() { rm -rf "$bundled"; }
trap cleanup EXIT

# 1. Production frontend build.
if [ ! -d "$root/frontend/node_modules" ]; then
    (cd "$root/frontend" && npm ci)
fi
(cd "$root/frontend" && npm run build)

# 2. Stage the embedded data inside the package.
rm -rf "$bundled"
mkdir -p "$bundled"
cp -r "$root/config" "$bundled/config"
cp "$root/docs/methodology/BIBLIOGRAPHY.md" "$bundled/BIBLIOGRAPHY.md"
cp -r "$root/data" "$bundled/data"
cp -r "$root/frontend/dist" "$bundled/webapp"

# 3. Build the wheel.
rm -rf "$root/backend/dist"
(cd "$root/backend" && python -m build --wheel)

echo
echo "Built: $(ls "$root"/backend/dist/*.whl)"
