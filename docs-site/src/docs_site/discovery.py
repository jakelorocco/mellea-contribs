"""Discover subpackages by walking ``mellea_contribs/*/pyproject.toml``.

Mirrors the discovery pattern in ``.github/scripts/parse_release_tag.py``:
iterate the directory, parse each ``pyproject.toml`` with ``tomllib``, and
key off ``data["project"]["name"]``.
"""
from __future__ import annotations

import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .pyproject_parse import (
    DependencyDisplay,
    find_mellea_constraint,
    other_dependencies,
)


@dataclass
class Package:
    name: str
    dir: Path
    project: dict
    version: str
    description: str
    requires_python: str
    mellea_constraint: str | None
    other_deps: list[DependencyDisplay]
    authors: list[str]
    keywords: list[str]
    classifiers: list[str]
    urls: dict[str, str] = field(default_factory=dict)
    license: str = ""

    @property
    def has_readme(self) -> bool:
        return (self.dir / "README.md").exists()


def _author_display(author: dict) -> str:
    name = author.get("name", "").strip()
    email = author.get("email", "").strip()
    if name and email:
        return f"{name} <{email}>"
    return name or email or ""


def _license_display(project: dict) -> str:
    lic = project.get("license")
    if isinstance(lic, str):
        return lic
    if isinstance(lic, dict):
        return lic.get("text") or lic.get("file") or ""
    for cls in project.get("classifiers", []):
        if cls.startswith("License ::"):
            return cls.split("::")[-1].strip()
    return ""


def _build_package(name: str, dir_path: Path, project: dict) -> Package:
    deps = project.get("dependencies", []) or []
    return Package(
        name=name,
        dir=dir_path,
        project=project,
        version=project.get("version", ""),
        description=project.get("description", ""),
        requires_python=project.get("requires-python", ""),
        mellea_constraint=find_mellea_constraint(deps),
        other_deps=other_dependencies(deps),
        authors=[_author_display(a) for a in project.get("authors", []) if _author_display(a)],
        keywords=list(project.get("keywords", [])),
        classifiers=list(project.get("classifiers", [])),
        urls=dict(project.get("urls", {})),
        license=_license_display(project),
    )


def discover_packages(root: Path) -> list[Package]:
    if not root.exists():
        print(f"warning: {root} does not exist", file=sys.stderr)
        return []
    packages: list[Package] = []
    for dir_path in sorted(root.iterdir()):
        if not dir_path.is_dir():
            continue
        pyproject = dir_path / "pyproject.toml"
        if not pyproject.exists():
            continue
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, OSError) as e:
            print(f"warning: skipping {pyproject}: {e}", file=sys.stderr)
            continue
        project = data.get("project") or {}
        name = project.get("name")
        if not name:
            continue
        packages.append(_build_package(name, dir_path, project))
    packages.sort(key=lambda p: p.name)
    return packages
