"""MkDocs build hooks (D-035).

The site renders the existing corpus under ``docs/`` — nothing here authors
content twice. The hooks only adapt repository-relative concerns to the
published site:

1. ``index.md`` is generated from the repository README at build time (never
   committed), with the badge images dropped — the published site makes no
   third-party requests — and its repository-relative links rebased.
2. The three brand font families are injected from ``frontend/public/fonts``,
   the same self-hosted files the application serves (with their OFL notice).
3. The Criterra lockup and favicon are injected the same way, from
   ``frontend/public`` — one copy of each asset in the repository, exactly as
   the fonts are handled (D-036, D-042).
4. Corpus links that point outside ``docs/`` (``config/…``, ``tools/…``) are
   rewritten to the GitHub repository so they resolve from the site.
"""

from __future__ import annotations

import re
from pathlib import Path

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/Dimitrios-Kafetzis/CriterraNatureCoolingTool"

_BADGE_LINE = re.compile(r"^\[!\[[^\n]*$\n?", re.MULTILINE)
_PARENT_LINK = re.compile(r"\]\(((?:\.\./)+)([^)#\s]+)(#[^)]*)?\)")


def _github_url(repo_path: str) -> str:
    kind = "blob" if "." in repo_path.rsplit("/", 1)[-1] else "tree"
    return f"{REPO_URL}/{kind}/main/{repo_path.rstrip('/')}"


def _index_markdown() -> str:
    """The landing page: the README, rebased for the site."""
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    text = _BADGE_LINE.sub("", text)
    # Links into the corpus lose their docs/ prefix; links to repository
    # files outside the corpus point at GitHub.
    text = text.replace("](docs/methodology/)", "](methodology/README.md)")
    text = text.replace("](docs/", "](")
    text = text.replace("](LICENSE)", f"]({_github_url('LICENSE')})")
    text = text.replace("](NOTICE)", f"]({_github_url('NOTICE')})")
    text = text.replace("](paper/main.pdf)", f"]({_github_url('paper/main.pdf')})")
    text = text.replace("](paper/)", f"]({_github_url('paper/')})")
    return text


_BRAND_ASSETS = {
    "assets/criterra-lockup.svg": "brand/criterra-lockup.svg",
    "assets/favicon.ico": "favicon.ico",
}


def on_files(files: Files, config: MkDocsConfig) -> Files:
    files.append(File.generated(config, "index.md", content=_index_markdown()))
    public = REPO_ROOT / "frontend" / "public"
    for font in sorted((public / "fonts").iterdir()):
        files.append(
            File.generated(config, f"assets/fonts/{font.name}", abs_src_path=str(font))
        )
    for site_path, source in _BRAND_ASSETS.items():
        files.append(
            File.generated(config, site_path, abs_src_path=str(public / source))
        )
    return files


def on_page_markdown(
    markdown: str, page: Page, config: MkDocsConfig, files: Files
) -> str:
    """Rebase relative links that climb out of the corpus onto GitHub.

    A link that stays inside ``docs/`` resolves normally and is left alone;
    one that climbs exactly to the repository root becomes a GitHub URL.
    """
    depth = page.file.src_uri.count("/")

    def rebase(match: re.Match[str]) -> str:
        ups = match.group(1).count("../")
        if ups != depth + 1:
            return match.group(0)
        return f"]({_github_url(match.group(2))}{match.group(3) or ''})"

    return _PARENT_LINK.sub(rebase, markdown)
