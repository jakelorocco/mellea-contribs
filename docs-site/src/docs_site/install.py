"""Install command derivation.

Installations always go through git tags. We never link to PyPI or to the
wheel artefacts attached to a GitHub Release; pip can install a Python
package directly from a git URL pinned to a tag, which is what every install
example on the site uses.

Format::

    pip install "git+https://github.com/<repo>.git@<tag>#subdirectory=<pkg_dir>"

Where ``<tag>`` is the per-package release tag (e.g. ``mellea-dspy/v0.1.0``)
or ``main`` when no release exists yet.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class InstallCommand:
    pip_command: str
    git_ref: str  # "<package>/v<version>" for releases, "main" otherwise
    has_release: bool


def _git_install(repo: str, ref: str, pkg_dir: Path) -> str:
    subdir = str(pkg_dir).strip("/")
    return (
        f'pip install "git+https://github.com/{repo}.git@{ref}'
        f'#subdirectory={subdir}"'
    )


def install_command(
    repo: str,
    package_name: str,
    version: str | None,
    pkg_dir: Path,
) -> InstallCommand:
    """Build an install command pinned to a release tag, or to ``main``."""
    if package_name and version:
        ref = f"{package_name}/v{version}"
        return InstallCommand(
            pip_command=_git_install(repo, ref, pkg_dir),
            git_ref=ref,
            has_release=True,
        )
    return InstallCommand(
        pip_command=_git_install(repo, "main", pkg_dir),
        git_ref="main",
        has_release=False,
    )
