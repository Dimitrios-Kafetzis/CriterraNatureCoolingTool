"""Local-first project storage (D-020, D-028).

Projects are JSON files — one file per project, named by its UUID — under the
platform user-data directory resolved by ``platformdirs``. This is the only
place in the system where clocks live: the engine is clock-free, so creation
and update timestamps are stamped here, as ISO-8601 UTC.

Writes are atomic (write to a sibling temp file, then rename) so an
interrupted save never truncates a project a user may have spent 45 answers
building.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

import platformdirs

from nature_cooling.api.schemas import Project

_APP_NAME = "criterra-nature-cooling"
_APP_AUTHOR = "Criterra"


class ProjectNotFoundError(Exception):
    """Raised when no stored project has the requested identifier."""


def utc_now_iso() -> str:
    """The current time as an ISO-8601 UTC timestamp."""
    return datetime.now(UTC).isoformat()


def default_storage_root() -> Path:
    """The platform user-data directory for project files."""
    return platformdirs.user_data_path(_APP_NAME, _APP_AUTHOR) / "projects"


class ProjectStore:
    """Load, save, list, and delete project documents.

    The store is deliberately dumb: it moves validated ``Project`` documents
    between memory and disk and stamps nothing itself. Domain rules (what may
    change, when a result is written) live with the routes.
    """

    def __init__(self, root: Path) -> None:
        self._root = root

    def _path(self, project_id: str) -> Path:
        return self._root / f"{project_id}.json"

    def save(self, project: Project) -> None:
        """Write the project atomically, creating the directory on first use."""
        self._root.mkdir(parents=True, exist_ok=True)
        path = self._path(project.project_id)
        temp = path.with_name(path.name + ".tmp")
        temp.write_text(
            json.dumps(project.model_dump(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        os.replace(temp, path)

    def load(self, project_id: str) -> Project:
        """Read one project.

        Raises:
            ProjectNotFoundError: if no file exists for this identifier.
        """
        path = self._path(project_id)
        if not path.is_file():
            raise ProjectNotFoundError(project_id)
        return Project.model_validate(json.loads(path.read_text(encoding="utf-8")))

    def delete(self, project_id: str) -> None:
        """Delete one project file.

        Raises:
            ProjectNotFoundError: if no file exists for this identifier.
        """
        path = self._path(project_id)
        if not path.is_file():
            raise ProjectNotFoundError(project_id)
        path.unlink()

    def list_all(self) -> list[Project]:
        """All stored projects, most recently updated first."""
        if not self._root.is_dir():
            return []
        projects = [
            Project.model_validate(json.loads(path.read_text(encoding="utf-8")))
            for path in self._root.glob("*.json")
        ]
        return sorted(projects, key=lambda p: (p.updated_at, p.project_id), reverse=True)
