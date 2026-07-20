from dataclasses import replace

from backend.app.analysis.diff_analyzer import (
    EdgeKeyDifference,
    build_module_dependency_differences,
    compare_edge_keys,
    compare_graphs,
    compare_module_sets,
    compare_modules,
    graph_edge_keys,
    graph_module_paths,
    modules_with_dependency_changes,
)
from backend.app.models.graph_metrics_models import ModuleDependencyDifference
from backend.tests.utils import _graph


def test_graph_module_paths():
    graph = _graph(("a", "b", "c"), (("a", "b"),))

    assert graph_module_paths(graph) == {"a", "b", "c"}


def test_graph_edge_keys():
    graph = _graph(("a", "b"), (("a", "b"), ("b", "a")))

    assert graph_edge_keys(graph) == {("a", "b"), ("b", "a")}


def test_compare_module_sets():
    base = _graph(("a", "b"), ())
    target = _graph(("a", "c", "d"), ())

    diff = compare_module_sets(base, target)

    assert diff.added_modules == ("c", "d")
    assert diff.removed_modules == ("b",)


def test_compare_module_sets_no_changes():
    graph = _graph(("a", "b"), (("a", "b"),))

    diff = compare_module_sets(graph, graph)

    assert diff.added_modules == ()
    assert diff.removed_modules == ()


def test_compare_edge_keys():
    base = _graph(("a", "b", "c"), (("a", "b"),))
    target = _graph(("a", "b", "c"), (("a", "c"),))

    diff = compare_edge_keys(base, target)

    assert diff.added_edge_keys == frozenset({("a", "c")})
    assert diff.removed_edge_keys == frozenset({("a", "b")})


def test_compare_edge_keys_ignores_import_count_only_changes():
    base = _graph(("a", "b"), (("a", "b"),))
    target = replace(
        base,
        edges=tuple(
            replace(edge, import_count=edge.import_count + 5) for edge in base.edges
        ),
    )

    diff = compare_edge_keys(base, target)

    assert diff.added_edge_keys == frozenset()
    assert diff.removed_edge_keys == frozenset()


def test_modules_with_dependency_changes():
    edge_diff = EdgeKeyDifference(
        added_edge_keys=frozenset({("a", "c"), ("b", "d")}),
        removed_edge_keys=frozenset({("a", "b"), ("c", "d")}),
    )

    assert modules_with_dependency_changes(edge_diff) == ("a", "b", "c")


def test_build_module_dependency_differences():
    edge_diff = EdgeKeyDifference(
        added_edge_keys=frozenset({("a", "c"), ("b", "d")}),
        removed_edge_keys=frozenset({("a", "b")}),
    )

    result = build_module_dependency_differences(edge_diff)

    assert result == {
        "a": ModuleDependencyDifference(
            module="a",
            added_dependencies=("c",),
            removed_dependencies=("b",),
        ),
        "b": ModuleDependencyDifference(
            module="b",
            added_dependencies=("d",),
            removed_dependencies=(),
        ),
    }


def test_compare_modules_composes_helpers():
    base = _graph(("a", "b"), (("a", "b"),))
    target = _graph(("a", "c"), (("a", "c"),))

    diff = compare_modules(base, target)

    assert diff.added_modules == ("c",)
    assert diff.removed_modules == ("b",)
    assert diff.module_dependencies == {
        "a": ModuleDependencyDifference(
            module="a",
            added_dependencies=("c",),
            removed_dependencies=("b",),
        ),
    }


def test_compare_graphs_module_add_and_remove():
    base = _graph(("a", "b"), (("a", "b"),))
    target = _graph(("a", "c"), (("a", "c"),))

    diff = compare_graphs(
        base, target, base_revision="base", target_revision="target"
    )

    assert diff.added_modules == ("c",)
    assert diff.removed_modules == ("b",)
    assert diff.module_dependencies == {
        "a": ModuleDependencyDifference(
            module="a",
            added_dependencies=("c",),
            removed_dependencies=("b",),
        ),
    }


def test_compare_graphs_dependency_change_on_existing_module():
    base = _graph(("a", "b", "c"), (("a", "b"),))
    target = _graph(("a", "b", "c"), (("a", "c"),))

    diff = compare_graphs(
        base, target, base_revision="HEAD~1", target_revision="HEAD"
    )

    assert diff.added_modules == ()
    assert diff.removed_modules == ()
    assert diff.module_dependencies["a"] == ModuleDependencyDifference(
        module="a",
        added_dependencies=("c",),
        removed_dependencies=("b",),
    )


def test_compare_graphs_ignores_fan_in_fan_out_differences():
    base = _graph(("a", "b"), (("a", "b"),))
    target = replace(
        base,
        nodes=tuple(
            replace(node, fan_in=node.fan_in + 10, fan_out=node.fan_out + 10)
            for node in base.nodes
        ),
    )

    diff = compare_graphs(
        base, target, base_revision="a", target_revision="b"
    )

    assert diff.added_modules == ()
    assert diff.removed_modules == ()
    assert diff.module_dependencies == {}


def test_compare_graphs_added_module_with_dependencies():
    base = _graph(("a",), ())
    target = _graph(("a", "b", "c"), (("b", "c"), ("b", "a")))

    diff = compare_graphs(
        base, target, base_revision="old", target_revision="new"
    )

    assert diff.added_modules == ("b", "c")
    assert diff.removed_modules == ()
    assert diff.module_dependencies["b"] == ModuleDependencyDifference(
        module="b",
        added_dependencies=("a", "c"),
        removed_dependencies=(),
    )
