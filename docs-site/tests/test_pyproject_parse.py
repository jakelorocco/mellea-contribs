from docs_site.pyproject_parse import (
    find_mellea_constraint,
    other_dependencies,
    parse_dependency,
)


def test_finds_simple_constraint():
    deps = ["mellea>=0.3.2", "dspy>=3.1.3"]
    assert find_mellea_constraint(deps) == "mellea>=0.3.2"


def test_finds_constraint_with_extras():
    # Used by mellea_contribs/tools_package and mellea_contribs/reqlib_package
    deps = ["mellea[litellm]==0.3.2", "rapidfuzz>=3.14.3"]
    assert find_mellea_constraint(deps) == "mellea[litellm]==0.3.2"


def test_returns_none_when_mellea_missing():
    assert find_mellea_constraint(["dspy>=3.1.3"]) is None


def test_handles_empty_or_none():
    assert find_mellea_constraint([]) is None
    assert find_mellea_constraint(None) is None  # type: ignore[arg-type]


def test_skips_unparseable():
    # An unparseable raw entry should not crash extraction.
    assert find_mellea_constraint(["@@@invalid@@@", "mellea>=0.3.2"]) == "mellea>=0.3.2"


def test_other_dependencies_excludes_mellea():
    deps = ["mellea>=0.3.2", "dspy>=3.1.3", "rapidfuzz>=3.14.3"]
    others = [d.name for d in other_dependencies(deps)]
    assert others == ["dspy", "rapidfuzz"]


def test_other_dependencies_preserves_extras_in_display():
    deps = ["foo[bar,baz]>=1.0"]
    [d] = other_dependencies(deps)
    assert d.display() == "foo[bar,baz]>=1.0"


def test_parse_dependency_returns_none_for_garbage():
    assert parse_dependency("$$$ not a requirement $$$") is None
