from pathlib import Path

from docs_site.install import install_command


def test_install_command_for_released_package_uses_tag_ref():
    cmd = install_command(
        "generative-computing/mellea-contribs",
        "mellea-dspy",
        "0.1.0",
        Path("mellea_contribs/dspy_backend"),
    )
    assert cmd.has_release is True
    assert cmd.git_ref == "mellea-dspy/v0.1.0"
    assert cmd.pip_command == (
        'pip install "git+https://github.com/generative-computing/mellea-contribs.git'
        '@mellea-dspy/v0.1.0#subdirectory=mellea_contribs/dspy_backend"'
    )


def test_install_command_falls_back_to_main_without_version():
    cmd = install_command(
        "generative-computing/mellea-contribs",
        "mellea-tools",
        None,
        Path("mellea_contribs/tools_package"),
    )
    assert cmd.has_release is False
    assert cmd.git_ref == "main"
    assert cmd.pip_command == (
        'pip install "git+https://github.com/generative-computing/mellea-contribs.git'
        '@main#subdirectory=mellea_contribs/tools_package"'
    )


def test_install_command_falls_back_to_main_with_empty_version():
    cmd = install_command(
        "generative-computing/mellea-contribs",
        "mellea-tools",
        "",
        Path("mellea_contribs/tools_package"),
    )
    assert cmd.has_release is False
    assert cmd.git_ref == "main"
