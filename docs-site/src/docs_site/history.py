"""Per-package release history derived from git tags.

For each package, we list tags shaped ``<name>/v*`` (sorted newest-first by
``--sort=-version:refname``), and for each tag read the ``pyproject.toml``
that existed at that tag via ``git show <tag>:<dir>/pyproject.toml`` so the
``mellea`` constraint shown matches what the user would have gotten if they'd
installed that exact release.
"""
from __future__ import annotations

import subprocess
import sys
import tomllib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from .pyproject_parse import find_mellea_constraint


@dataclass
class Release:
    tag: str
    version: str
    date: datetime | None
    is_prerelease: bool
    mellea_constraint: str | None  # None when historical pyproject is missing/malformed
    release_url: str
    install_command: str


def _run(cmd: list[str], check: bool = False) -> str:
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
    except FileNotFoundError:
        print("warning: git not found on PATH", file=sys.stderr)
        return ""
    if result.returncode != 0 and not check:
        return ""
    return result.stdout


def _list_tags(name: str) -> list[str]:
    out = _run(["git", "tag", "-l", f"{name}/v*", "--sort=-version:refname"])
    return [t for t in (line.strip() for line in out.splitlines()) if t]


def _tag_date(tag: str) -> datetime | None:
    iso = _run(["git", "log", "-1", "--format=%aI", tag]).strip()
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso)
    except ValueError:
        return None


def _pyproject_at(tag: str, pkg_dir: Path) -> dict | None:
    blob = _run(["git", "show", f"{tag}:{pkg_dir}/pyproject.toml"])
    if not blob.strip():
        return None
    try:
        return tomllib.loads(blob)
    except tomllib.TOMLDecodeError as e:
        print(f"warning: malformed pyproject at {tag}: {e}", file=sys.stderr)
        return None


def build_history(name: str, pkg_dir: Path, repo: str) -> list[Release]:
    releases: list[Release] = []
    for tag in _list_tags(name):
        if not tag.startswith(f"{name}/v"):
            continue
        version = tag.split("/v", 1)[1]
        is_prerelease = "-" in version  # matches release-package.yml:154
        data = _pyproject_at(tag, pkg_dir)
        constraint: str | None = None
        if data is not None:
            project = data.get("project") or {}
            constraint = find_mellea_constraint(project.get("dependencies", []) or [])
        encoded_tag = quote(tag, safe="/")
        install_cmd = (
            f'pip install "git+https://github.com/{repo}.git@{tag}'
            f'#subdirectory={pkg_dir}"'
        )
        releases.append(
            Release(
                tag=tag,
                version=version,
                date=_tag_date(tag),
                is_prerelease=is_prerelease,
                mellea_constraint=constraint,
                release_url=f"https://github.com/{repo}/releases/tag/{encoded_tag}",
                install_command=install_cmd,
            )
        )
    return releases
