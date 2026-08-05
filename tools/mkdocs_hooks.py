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
5. The header's repository version badge is pre-filled at build time from the
   package version. Material otherwise queries the GitHub API from every
   visitor's browser for it — a third-party request the site must not make,
   and one whose per-browser cache goes stale between releases.
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
    text = text.replace(
        "](paper/Criterra_NatureCoolingTool_MethodologyReport.pdf)",
        f"]({_github_url('paper/Criterra_NatureCoolingTool_MethodologyReport.pdf')})",
    )
    text = text.replace("](paper/)", f"]({_github_url('paper/')})")
    return text


_BRAND_ASSETS = {
    "assets/criterra-lockup.svg": "brand/criterra-lockup.svg",
    "assets/favicon.ico": "favicon.ico",
}


def _package_version() -> str:
    init = REPO_ROOT / "backend" / "src" / "nature_cooling" / "__init__.py"
    match = re.search(r'__version__\s*=\s*"([^"]+)"', init.read_text(encoding="utf-8"))
    assert match, "package version not found"
    return match.group(1)


_BUNDLE_TAG = re.compile(r'<script src="[^"]*assets/javascripts/bundle[^"]*">')


def on_post_page(output: str, page: Page, config: MkDocsConfig) -> str:
    """Pre-fill Material's repository-facts cache so it never queries GitHub.

    Material's bundle reads ``__source`` from sessionStorage and only falls
    back to ``api.github.com`` when it is absent — but it mounts the header
    component synchronously while the bundle executes, so the value must be
    written *before* the bundle tag; ``extra_javascript`` renders after it
    and is too late. Writing the version on every page load keeps the badge
    correct for the build that published it and replaces any stale value a
    browser cached from an earlier visit. Stars and forks are not shown —
    they exist only behind the API request this hook exists to avoid.
    """
    prefill = (
        f'<script>__md_set("__source",'
        f'{{version:"v{_package_version()}"}},sessionStorage)</script>'
    )
    return _BUNDLE_TAG.sub(lambda m: prefill + m.group(0), output, count=1)


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
