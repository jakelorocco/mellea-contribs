"""Helpers for extracting display metadata from a parsed pyproject.toml."""
from __future__ import annotations

from dataclasses import dataclass

from packaging.requirements import InvalidRequirement, Requirement


@dataclass
class DependencyDisplay:
    raw: str
    name: str
    extras: list[str]
    specifier: str

    def display(self) -> str:
        extras = f"[{','.join(sorted(self.extras))}]" if self.extras else ""
        return f"{self.name}{extras}{self.specifier}"


def parse_dependency(raw: str) -> DependencyDisplay | None:
    try:
        req = Requirement(raw)
    except InvalidRequirement:
        return None
    return DependencyDisplay(
        raw=raw,
        name=req.name,
        extras=sorted(req.extras),
        specifier=str(req.specifier),
    )


def find_mellea_constraint(dependencies: list[str]) -> str | None:
    """Return the displayable mellea requirement, or None if not pinned.

    Handles ``mellea>=0.3.2``, ``mellea[litellm]==0.3.2``, etc.
    """
    for raw in dependencies or []:
        dep = parse_dependency(raw)
        if dep and dep.name.lower() == "mellea":
            return dep.display()
    return None


def other_dependencies(dependencies: list[str]) -> list[DependencyDisplay]:
    """All deps except mellea itself, in order, parseable only."""
    out: list[DependencyDisplay] = []
    for raw in dependencies or []:
        dep = parse_dependency(raw)
        if dep is None or dep.name.lower() == "mellea":
            continue
        out.append(dep)
    return out
