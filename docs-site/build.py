#!/usr/bin/env python3
"""Static site generator for the mellea-contribs GitHub Pages index.

Walks ``mellea_contribs/*/pyproject.toml``, gathers per-package metadata and
git-tag-derived version history, and renders an index page plus one detail
page per subpackage into the output directory.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow running the script directly without installing the package.
sys.path.insert(0, str(Path(__file__).parent / "src"))

from docs_site.discovery import discover_packages
from docs_site.history import build_history
from docs_site.install import install_command
from docs_site.render import make_env, render_readme


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", required=True, type=Path, help="Output directory (e.g. _site)"
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get(
            "GITHUB_REPOSITORY", "generative-computing/mellea-contribs"
        ),
        help="owner/name slug used for release URLs",
    )
    parser.add_argument(
        "--base-url",
        default="",
        help="URL prefix for project Pages sites (e.g. /mellea-contribs)",
    )
    parser.add_argument(
        "--root",
        default=Path("mellea_contribs"),
        type=Path,
        help="Directory containing subpackages",
    )
    return parser.parse_args()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def copy_static(src: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        shutil.copy2(item, dest / item.name)


def commit_sha() -> str:
    return os.environ.get("GITHUB_SHA", "")[:7] or _git_head_sha()


def _git_head_sha() -> str:
    import subprocess

    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def main() -> int:
    args = parse_args()
    base_url = args.base_url.rstrip("/")
    out: Path = args.output
    out.mkdir(parents=True, exist_ok=True)

    here = Path(__file__).parent
    env = make_env(here / "templates", base_url=base_url)

    packages = discover_packages(args.root)
    if not packages:
        print(
            f"warning: no packages discovered under {args.root}",
            file=sys.stderr,
        )

    rendered_packages = []
    for pkg in packages:
        history = build_history(pkg.name, pkg.dir, args.repo)
        latest_release = next(
            (r for r in history if not r.is_prerelease), history[0] if history else None
        )
        readme_html = render_readme(pkg.dir / "README.md")
        install = install_command(
            args.repo,
            pkg.name,
            latest_release.version if latest_release else None,
            pkg.dir,
        )
        rendered_packages.append(
            {
                "pkg": pkg,
                "history": history,
                "latest_release": latest_release,
                "readme_html": readme_html,
                "install": install,
            }
        )

    build_meta = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "sha": commit_sha(),
        "repo": args.repo,
    }

    index_html = env.get_template("index.html").render(
        packages=rendered_packages, build=build_meta
    )
    write(out / "index.html", index_html)

    not_found_html = env.get_template("base.html").render(
        title="Not found",
        build=build_meta,
        content="<h1>Not found</h1><p>That page does not exist. <a href=\""
        + (base_url or "/")
        + "\">Go home</a>.</p>",
    )
    write(out / "404.html", not_found_html)

    copy_static(here / "static", out / "static")

    print(
        f"wrote single-page index ({len(rendered_packages)} package(s) inlined) to {out}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
