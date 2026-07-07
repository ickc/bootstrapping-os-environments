from bsos.util.toposort import toposort, toposort_keys


def test_linear_chain_scrambled_input() -> None:
    # c depends on b depends on a; input order doesn't match dependency order
    edges = {"a": [], "b": ["a"], "c": ["b"]}
    assert toposort_keys(["c", "a", "b"], edges) == ["a", "b", "c"]


def test_diamond() -> None:
    # a depends on b and c; both depend on d
    edges = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
    result = toposort_keys(["a", "b", "c", "d"], edges)
    assert set(result) == {"a", "b", "c", "d"}
    assert result.index("d") < result.index("b")
    assert result.index("d") < result.index("c")
    assert result.index("b") < result.index("a")
    assert result.index("c") < result.index("a")


def test_unrelated_items_preserve_original_order() -> None:
    edges: dict[str, list[str]] = {"a": [], "b": [], "c": []}
    assert toposort_keys(["c", "a", "b"], edges) == ["c", "a", "b"]


def test_dependency_outside_key_set_is_ignored() -> None:
    edges = {"a": ["missing"], "b": []}
    assert toposort_keys(["a", "b"], edges) == ["a", "b"]


def test_cycle_does_not_raise_and_each_key_appears_once() -> None:
    # sphinx <-> sphinxcontrib-applehelp, as seen in real conda-forge metadata
    edges = {
        "sphinx": ["sphinxcontrib-applehelp"],
        "sphinxcontrib-applehelp": ["sphinx"],
    }
    result = toposort_keys(["sphinx", "sphinxcontrib-applehelp"], edges)
    assert sorted(result) == ["sphinx", "sphinxcontrib-applehelp"]


def test_cycle_order_depends_on_traversal_order() -> None:
    edges = {
        "sphinx": ["sphinxcontrib-applehelp"],
        "sphinxcontrib-applehelp": ["sphinx"],
    }
    assert toposort_keys(["sphinx", "sphinxcontrib-applehelp"], edges) == [
        "sphinxcontrib-applehelp",
        "sphinx",
    ]
    assert toposort_keys(["sphinxcontrib-applehelp", "sphinx"], edges) == [
        "sphinx",
        "sphinxcontrib-applehelp",
    ]


def test_every_in_set_dependency_precedes_its_dependent() -> None:
    # property check over a larger acyclic graph, not just spot-checked pairs
    edges = {
        "a": [],
        "b": ["a"],
        "c": ["a", "b"],
        "d": ["c"],
        "e": ["a", "d"],
    }
    result = toposort_keys(["e", "d", "c", "b", "a"], edges)
    position = {key: i for i, key in enumerate(result)}
    for key, deps in edges.items():
        for dep in deps:
            assert position[dep] < position[key]


def test_toposort_wrapper_sorts_arbitrary_items_by_key() -> None:
    items = [
        {"name": "c", "deps": ["b"]},
        {"name": "a", "deps": []},
        {"name": "b", "deps": ["a"]},
    ]
    result = toposort(items, key=lambda item: item["name"], depends_on=lambda item: item["deps"])
    assert [item["name"] for item in result] == ["a", "b", "c"]
