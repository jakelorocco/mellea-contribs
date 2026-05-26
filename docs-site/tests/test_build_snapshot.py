"""End-to-end smoke test: run build.py against the real repo, assert outputs.

The site is a single-page app — all package data is inlined into one
``index.html`` and shown/hidden client-side via hash routing.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
BUILD_SCRIPT = REPO_ROOT / "docs-site" / "build.py"

KNOWN_PACKAGES = [
    "mellea-integration-core",
    "mellea-dspy",
    "mellea-crewai",
    "mellea-langchain",
    "mellea-tools",
    "mellea-reqlib",
]


@pytest.fixture
def site(tmp_path: Path) -> Path:
    out = tmp_path / "_site"
    result = subprocess.run(
        [
            sys.executable,
            str(BUILD_SCRIPT),
            "--output",
            str(out),
            "--repo",
            "generative-computing/mellea-contribs",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
    assert result.returncode == 0, result.stderr
    return out


@pytest.fixture
def index_html(site: Path) -> str:
    return (site / "index.html").read_text()


def test_index_exists(site: Path):
    assert (site / "index.html").exists()


def test_static_assets_copied(site: Path):
    assert (site / "static" / "style.css").exists()
    assert (site / "static" / "app.js").exists()


def test_404_page_exists(site: Path):
    assert (site / "404.html").exists()


def test_no_per_package_directories(site: Path):
    # The SPA inlines everything into the root index.
    for name in KNOWN_PACKAGES:
        assert not (site / name).exists(), f"unexpected per-package dir for {name}"


def test_each_package_has_a_pane(index_html: str):
    for name in KNOWN_PACKAGES:
        assert f'id="pkg-{name}"' in index_html, f"missing pane for {name}"


def test_sidebar_has_overview_and_all_packages(index_html: str):
    assert 'data-target="overview"' in index_html
    for name in KNOWN_PACKAGES:
        assert f'data-target="pkg-{name}"' in index_html


def test_dspy_install_command_uses_git_tag(index_html: str):
    assert (
        "pip install &#34;git+https://github.com/generative-computing/mellea-contribs.git"
        "@mellea-dspy/v0.1.0#subdirectory=mellea_contribs/dspy_backend&#34;"
    ) in index_html


def test_unreleased_package_install_command_targets_main(index_html: str):
    assert "@main#subdirectory=mellea_contribs/tools_package" in index_html


def test_overview_links_to_repo(index_html: str):
    assert "github.com/generative-computing/mellea-contribs" in index_html


def test_panes_hidden_by_default_except_overview(index_html: str):
    # Each package pane carries `hidden`; the JS reveals one based on the hash.
    for name in KNOWN_PACKAGES:
        # Loose check: the opening tag includes both the id and the hidden attribute.
        marker = f'id="pkg-{name}" class="pane" role="tabpanel" hidden'
        assert marker in index_html, f"package {name} pane should be hidden"
