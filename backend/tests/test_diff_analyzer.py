from dataclasses import replace

from backend.app.analysis.diff_analyzer import compare_graphs
from backend.app.models.graph_metrics_models import ModuleDependencyDifference
from backend.tests.utils import _graph


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
    # Same modules/edges; mutate degrees so full-node equality would differ.
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


def test_compare_graphs_ignores_import_count_only_changes():
    base = _graph(("a", "b"), (("a", "b"),))
    target = replace(
        base,
        edges=tuple(
            replace(edge, import_count=edge.import_count + 5) for edge in base.edges
        ),
    )

    diff = compare_graphs(
        base, target, base_revision="a", target_revision="b"
    )

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
