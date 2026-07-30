"""Export the service's OpenAPI schema as deterministic JSON.

The frontend's TypeScript API types are generated from this schema and
committed (D-030); CI regenerates both and fails on drift, so the schema on
disk can never silently diverge from the service.

Usage: python scripts/export_openapi.py [output-path]
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from nature_cooling.api import create_app


def main() -> None:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("openapi.json")
    with tempfile.TemporaryDirectory() as scratch:
        app = create_app(storage_root=Path(scratch))
        schema = app.openapi()
    output.write_text(
        json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
