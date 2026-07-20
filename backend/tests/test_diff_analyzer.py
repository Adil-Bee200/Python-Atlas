from dataclasses import replace

from backend.app.analysis.diff_analyzer import (
    EdgeKeyDifference,
    build_module_dependency_differences,
    compare_architecture,
    compare_edge_keys,
    compare_graphs,
    compare_metrics,
    compare_module_sets,
    graph_edge_keys,
    graph_module_paths,
    modules_with_dependency_changes,
)
from backend.app.config.models import ArchitectureLayer
from backend.app.metrics.centrality import analyze_centrality
from backend.app.metrics.cycles import analyze_cycles
from backend.app.metrics.hub_modules import analyze_hub_modules
from backend.app.metrics.isolates import analyze_isolates
from backend.app.models.graph_metrics_models import (
    GraphArchitectureMetrics,
    GraphMetrics,
    LayerAssignment,
    LayerViolation,
    ModuleDependencyDifference,
)
from backend.tests.utils import _graph

API = ArchitectureLayer(name="api", module_patterns=("app.api.*",))
SERVICES = ArchitectureLayer(name="services", module_patterns=("app.services.*",))
MODELS = ArchitectureLayer(name="models", module_patterns=("app.models.*",))


def _metrics_with_architecture(
    graph,
    architecture: GraphArchitectureMetrics,
) -> GraphMetrics:
    centrality = analyze_centrality(graph)
    return GraphMetrics(
        centrality=centrality,
        isolates=analyze_isolates(graph),
        cycles=analyze_cycles(graph),
        hub_modules=analyze_hub_modules(graph, centrality),
        architecture=architecture,
    )


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


def test_compare_architecture_module_add_and_remove():
    base = _graph(("a", "b"), (("a", "b"),))
    target = _graph(("a", "c"), (("a", "c"),))

    diff = compare_architecture(base, target)

    assert diff.added_modules == ("c",)
    assert diff.removed_modules == ("b",)
    assert diff.module_dependencies == {
        "a": ModuleDependencyDifference(
            module="a",
            added_dependencies=("c",),
            removed_dependencies=("b",),
        ),
    }


def test_compare_architecture_dependency_change_on_existing_module():
    base = _graph(("a", "b", "c"), (("a", "b"),))
    target = _graph(("a", "b", "c"), (("a", "c"),))

    diff = compare_architecture(base, target)

    assert diff.added_modules == ()
    assert diff.removed_modules == ()
    assert diff.module_dependencies["a"] == ModuleDependencyDifference(
        module="a",
        added_dependencies=("c",),
        removed_dependencies=("b",),
    )


def test_compare_architecture_ignores_fan_in_fan_out_differences():
    base = _graph(("a", "b"), (("a", "b"),))
    target = replace(
        base,
        nodes=tuple(
            replace(node, fan_in=node.fan_in + 10, fan_out=node.fan_out + 10)
            for node in base.nodes
        ),
    )

    diff = compare_architecture(base, target)

    assert diff.added_modules == ()
    assert diff.removed_modules == ()
    assert diff.module_dependencies == {}


def test_compare_architecture_added_module_with_dependencies():
    base = _graph(("a",), ())
    target = _graph(("a", "b", "c"), (("b", "c"), ("b", "a")))

    diff = compare_architecture(base, target)

    assert diff.added_modules == ("b", "c")
    assert diff.removed_modules == ()
    assert diff.module_dependencies["b"] == ModuleDependencyDifference(
        module="b",
        added_dependencies=("a", "c"),
        removed_dependencies=(),
    )


def test_compare_metrics_returns_none_without_architecture_metrics():
    base = _graph(("app.api.routes",), ())
    target = _graph(("app.api.routes",), ())

    assert compare_metrics(base, target) is None


def test_compare_metrics_assignment_and_violation_changes():
    base = _graph(
        ("app.api.routes", "app.services.users", "app.models.user"),
        (("app.api.routes", "app.services.users"),),
    )
    target = _graph(
        ("app.api.routes", "app.services.users", "app.models.user"),
        (("app.api.routes", "app.models.user"),),
    )

    base = replace(
        base,
        metrics=_metrics_with_architecture(
            base,
            GraphArchitectureMetrics(
                assignments=(
                    LayerAssignment(layer=API, module="app.api.routes"),
                    LayerAssignment(layer=SERVICES, module="app.services.users"),
                ),
                violations=(),
            ),
        ),
    )
    target = replace(
        target,
        metrics=_metrics_with_architecture(
            target,
            GraphArchitectureMetrics(
                assignments=(
                    LayerAssignment(layer=API, module="app.api.routes"),
                    LayerAssignment(layer=MODELS, module="app.models.user"),
                ),
                violations=(
                    LayerViolation(
                        source_module="app.api.routes",
                        target_module="app.models.user",
                        source_layer="api",
                        target_layer="models",
                    ),
                ),
            ),
        ),
    )

    diff = compare_metrics(base, target)

    assert diff is not None
    assert diff.added_assignments == (
        LayerAssignment(layer=MODELS, module="app.models.user"),
    )
    assert diff.removed_assignments == (
        LayerAssignment(layer=SERVICES, module="app.services.users"),
    )
    assert diff.added_violations == (
        LayerViolation(
            source_module="app.api.routes",
            target_module="app.models.user",
            source_layer="api",
            target_layer="models",
        ),
    )
    assert diff.removed_violations == ()


def test_compare_graphs_orchestrates_architecture_and_metrics():
    base = _graph(("app.api.routes", "app.services.users"), (("app.api.routes", "app.services.users"),))
    target = _graph(("app.api.routes", "app.models.user"), (("app.api.routes", "app.models.user"),))

    base = replace(
        base,
        metrics=_metrics_with_architecture(
            base,
            GraphArchitectureMetrics(
                assignments=(
                    LayerAssignment(layer=API, module="app.api.routes"),
                    LayerAssignment(layer=SERVICES, module="app.services.users"),
                ),
            ),
        ),
    )
    target = replace(
        target,
        metrics=_metrics_with_architecture(
            target,
            GraphArchitectureMetrics(
                assignments=(
                    LayerAssignment(layer=API, module="app.api.routes"),
                    LayerAssignment(layer=MODELS, module="app.models.user"),
                ),
                violations=(
                    LayerViolation(
                        source_module="app.api.routes",
                        target_module="app.models.user",
                        source_layer="api",
                        target_layer="models",
                    ),
                ),
            ),
        ),
    )

    diff = compare_graphs(
        base, target, base_revision="base", target_revision="target"
    )

    assert diff.base_revision == "base"
    assert diff.target_revision == "target"
    assert diff.architecture.added_modules == ("app.models.user",)
    assert diff.architecture.removed_modules == ("app.services.users",)
    assert diff.metrics is not None
    assert diff.metrics.added_assignments == (
        LayerAssignment(layer=MODELS, module="app.models.user"),
    )
    assert diff.metrics.removed_assignments == (
        LayerAssignment(layer=SERVICES, module="app.services.users"),
    )


def test_compare_graphs_metrics_none_when_architecture_missing():
    base = _graph(("a", "b"), (("a", "b"),))
    target = _graph(("a", "c"), (("a", "c"),))

    diff = compare_graphs(
        base, target, base_revision="old", target_revision="new"
    )

    assert diff.architecture.added_modules == ("c",)
    assert diff.metrics is None
