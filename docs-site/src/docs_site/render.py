"""Jinja2 environment + README rendering."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape


def make_env(templates_dir: Path, base_url: str = "") -> Environment:
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["base_url"] = base_url

    def asset(path: str) -> str:
        path = path.lstrip("/")
        return f"{base_url}/{path}" if base_url else f"/{path}"

    def page_url(name: str) -> str:
        name = name.strip("/")
        return f"{base_url}/{name}/" if base_url else f"/{name}/"

    def home_url() -> str:
        return f"{base_url}/" if base_url else "/"

    def fmt_date(dt: datetime | None) -> str:
        if dt is None:
            return "—"
        return dt.strftime("%Y-%m-%d")

    env.globals["asset"] = asset
    env.globals["page_url"] = page_url
    env.globals["home_url"] = home_url
    env.filters["fmt_date"] = fmt_date
    return env


_README_EXTENSIONS = ["fenced_code", "tables", "toc", "codehilite", "sane_lists"]


def render_readme(path: Path) -> str:
    if not path.exists():
        return "<p><em>No README provided.</em></p>"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return "<p><em>Could not read README.</em></p>"
    return markdown.markdown(text, extensions=_README_EXTENSIONS, output_format="html5")
