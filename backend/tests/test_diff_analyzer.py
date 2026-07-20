from dataclasses import replace

from backend.app.analysis.diff_analyzer import (
    EdgeKeyDifference,
    build_module_dependency_differences,
    compare_architecture,
    compare_edge_keys,
    compare_graphs,
    compare_metrics,
    compare_module_sets,
    compare_structure,
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
    GraphCentralityMetrics,
    GraphCyclesMetrics,
    GraphDeadModules,
    GraphDeadModulesMetrics,
    GraphHubModule,
    GraphHubModulesMetrics,
    GraphIsolatesMetrics,
    GraphMetrics,
    LayerAmbiguity,
    LayerAssignment,
    LayerViolation,
    ModuleDependencyDifference,
)
from backend.tests.utils import _graph

API = ArchitectureLayer(name="api", module_patterns=("app.api.*",))
SERVICES = ArchitectureLayer(name="services", module_patterns=("app.services.*",))
MODELS = ArchitectureLayer(name="models", module_patterns=("app.models.*",))


def _full_metrics(
    graph,
    *,
    architecture: GraphArchitectureMetrics | None = None,
    isolates: tuple[str, ...] | None = None,
    cycles: tuple[tuple[str, ...], ...] | None = None,
    hub_modules: tuple[GraphHubModule, ...] = (),
    dead_modules: GraphDeadModulesMetrics | None = None,
) -> GraphMetrics:
    centrality = analyze_centrality(graph)
    return GraphMetrics(
        centrality=centrality,
        isolates=GraphIsolatesMetrics(
            isolates=isolates if isolates is not None else analyze_isolates(graph).isolates
        ),
        cycles=GraphCyclesMetrics(
            cycles=cycles if cycles is not None else analyze_cycles(graph).cycles
        ),
        hub_modules=GraphHubModulesMetrics(
            hub_modules=hub_modules,
            in_degree_threshold=0.0,
            max_out_degree=1.0,
        ),
        dead_modules=dead_modules,
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


def test_compare_structure_module_add_and_remove():
    base = _graph(("a", "b"), (("a", "b"),))
    target = _graph(("a", "c"), (("a", "c"),))

    diff = compare_structure(base, target)

    assert diff.added_modules == ("c",)
    assert diff.removed_modules == ("b",)
    assert diff.module_dependencies == {
        "a": ModuleDependencyDifference(
            module="a",
            added_dependencies=("c",),
            removed_dependencies=("b",),
        ),
    }


def test_compare_structure_dependency_change_on_existing_module():
    base = _graph(("a", "b", "c"), (("a", "b"),))
    target = _graph(("a", "b", "c"), (("a", "c"),))

    diff = compare_structure(base, target)

    assert diff.added_modules == ()
    assert diff.removed_modules == ()
    assert diff.module_dependencies["a"] == ModuleDependencyDifference(
        module="a",
        added_dependencies=("c",),
        removed_dependencies=("b",),
    )


def test_compare_structure_ignores_fan_in_fan_out_differences():
    base = _graph(("a", "b"), (("a", "b"),))
    target = replace(
        base,
        nodes=tuple(
            replace(node, fan_in=node.fan_in + 10, fan_out=node.fan_out + 10)
            for node in base.nodes
        ),
    )

    diff = compare_structure(base, target)

    assert diff.added_modules == ()
    assert diff.removed_modules == ()
    assert diff.module_dependencies == {}


def test_compare_structure_added_module_with_dependencies():
    base = _graph(("a",), ())
    target = _graph(("a", "b", "c"), (("b", "c"), ("b", "a")))

    diff = compare_structure(base, target)

    assert diff.added_modules == ("b", "c")
    assert diff.removed_modules == ()
    assert diff.module_dependencies["b"] == ModuleDependencyDifference(
        module="b",
        added_dependencies=("a", "c"),
        removed_dependencies=(),
    )


def test_compare_architecture_returns_none_without_layer_metrics():
    base = _graph(("app.api.routes",), ())
    target = _graph(("app.api.routes",), ())

    assert compare_architecture(base, target) is None


def test_compare_architecture_layer_field_changes():
    base = _graph(
        ("app.api.routes", "app.services.users", "app.models.user", "app.utils.x"),
        (),
    )
    target = _graph(
        ("app.api.routes", "app.services.users", "app.models.user", "app.utils.x"),
        (),
    )

    base = replace(
        base,
        metrics=_full_metrics(
            base,
            architecture=GraphArchitectureMetrics(
                assignments=(
                    LayerAssignment(layer=API, module="app.api.routes"),
                    LayerAssignment(layer=SERVICES, module="app.services.users"),
                ),
                violations=(),
                unclassified_modules=("app.utils.x",),
                empty_layers=("models",),
                ambiguous_assignments=(),
            ),
        ),
    )
    target = replace(
        target,
        metrics=_full_metrics(
            target,
            architecture=GraphArchitectureMetrics(
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
                unclassified_modules=(),
                empty_layers=("services",),
                ambiguous_assignments=(
                    LayerAmbiguity(
                        module="app.utils.x",
                        matching_layers=("api", "services"),
                    ),
                ),
            ),
        ),
    )

    diff = compare_architecture(base, target)

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
    assert diff.removed_unclassified_modules == ("app.utils.x",)
    assert diff.added_empty_layers == ("services",)
    assert diff.removed_empty_layers == ("models",)
    assert diff.added_ambiguous_assignments == (
        LayerAmbiguity(module="app.utils.x", matching_layers=("api", "services")),
    )


def test_compare_metrics_returns_none_without_graph_metrics():
    base = _graph(("a",), ())
    target = _graph(("a",), ())

    assert compare_metrics(base, target) is None


def test_compare_metrics_isolates_cycles_hubs_and_centrality():
    base = _graph(("a", "b", "c"), (("a", "b"), ("b", "a")))
    target = _graph(("a", "b", "c"), (("a", "b"), ("b", "c"), ("c", "a")))

    base = replace(
        base,
        metrics=_full_metrics(
            base,
            isolates=("c",),
            cycles=(("a", "b"),),
            hub_modules=(
                GraphHubModule(
                    module="a",
                    in_degree=1,
                    out_degree=1,
                    pagerank=0.5,
                    hub_score=0.4,
                ),
            ),
        ),
    )
    # Override centrality so value changes are deterministic.
    base = replace(
        base,
        metrics=replace(
            base.metrics,
            centrality=GraphCentralityMetrics(
                pagerank_centrality={"a": 0.5, "b": 0.3, "c": 0.2},
                betweenness_centrality={"a": 0.1, "b": 0.1, "c": 0.0},
                in_degree_centrality={"a": 0.5, "b": 0.5, "c": 0.0},
                out_degree_centrality={"a": 0.5, "b": 0.5, "c": 0.0},
            ),
        ),
    )
    target = replace(
        target,
        metrics=_full_metrics(
            target,
            isolates=(),
            cycles=(("a", "b", "c"),),
            hub_modules=(
                GraphHubModule(
                    module="b",
                    in_degree=1,
                    out_degree=1,
                    pagerank=0.4,
                    hub_score=0.3,
                ),
            ),
        ),
    )
    target = replace(
        target,
        metrics=replace(
            target.metrics,
            centrality=GraphCentralityMetrics(
                pagerank_centrality={"a": 0.4, "b": 0.3, "c": 0.3},
                betweenness_centrality={"a": 0.1, "b": 0.2, "c": 0.1},
                in_degree_centrality={"a": 0.5, "b": 0.5, "c": 0.5},
                out_degree_centrality={"a": 0.5, "b": 0.5, "c": 0.5},
            ),
        ),
    )

    diff = compare_metrics(base, target)

    assert diff is not None
    assert diff.removed_isolates == ("c",)
    assert diff.added_isolates == ()
    assert diff.removed_cycles == (("a", "b"),)
    assert diff.added_cycles == (("a", "b", "c"),)
    assert diff.added_hub_modules == ("b",)
    assert diff.removed_hub_modules == ("a",)
    assert any(change.module == "a" for change in diff.centrality.pagerank)
    assert any(change.module == "b" for change in diff.centrality.betweenness)


def test_compare_metrics_dead_modules():
    base = _graph(("a", "b", "c"), (("a", "b"),))
    target = _graph(("a", "b", "c"), (("a", "b"), ("a", "c")))

    base = replace(
        base,
        metrics=_full_metrics(
            base,
            dead_modules=GraphDeadModulesMetrics(
                dead_modules=(
                    GraphDeadModules("b", "Unreached by entry points"),
                    GraphDeadModules("c", "Unreached by entry points"),
                ),
                dead_modules_percentage=2 / 3,
            ),
        ),
    )
    target = replace(
        target,
        metrics=_full_metrics(
            target,
            dead_modules=GraphDeadModulesMetrics(
                dead_modules=(
                    GraphDeadModules("b", "Unreached by entry points"),
                ),
                dead_modules_percentage=1 / 3,
            ),
        ),
    )

    diff = compare_metrics(base, target)

    assert diff is not None
    assert diff.added_dead_modules == ()
    assert diff.removed_dead_modules == (
        GraphDeadModules("c", "Unreached by entry points"),
    )
    assert diff.dead_modules_percentage_before == 2 / 3
    assert diff.dead_modules_percentage_after == 1 / 3


def test_compare_metrics_dead_modules_none_treated_as_empty():
    base = _graph(("a", "orphan"), ())
    target = _graph(("a", "orphan"), ())

    base = replace(base, metrics=_full_metrics(base, dead_modules=None))
    target = replace(
        target,
        metrics=_full_metrics(
            target,
            dead_modules=GraphDeadModulesMetrics(
                dead_modules=(
                    GraphDeadModules("orphan", "Unreached by entry points"),
                ),
                dead_modules_percentage=0.5,
            ),
        ),
    )

    diff = compare_metrics(base, target)

    assert diff is not None
    assert diff.added_dead_modules == (
        GraphDeadModules("orphan", "Unreached by entry points"),
    )
    assert diff.removed_dead_modules == ()
    assert diff.dead_modules_percentage_before is None
    assert diff.dead_modules_percentage_after == 0.5


def test_compare_graphs_orchestrates_three_buckets():
    base = _graph(
        ("app.api.routes", "app.services.users"),
        (("app.api.routes", "app.services.users"),),
    )
    target = _graph(
        ("app.api.routes", "app.models.user"),
        (("app.api.routes", "app.models.user"),),
    )

    base = replace(
        base,
        metrics=_full_metrics(
            base,
            architecture=GraphArchitectureMetrics(
                assignments=(
                    LayerAssignment(layer=API, module="app.api.routes"),
                    LayerAssignment(layer=SERVICES, module="app.services.users"),
                ),
            ),
            isolates=("app.services.users",),
        ),
    )
    target = replace(
        target,
        metrics=_full_metrics(
            target,
            architecture=GraphArchitectureMetrics(
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
            isolates=(),
        ),
    )

    diff = compare_graphs(
        base, target, base_revision="base", target_revision="target"
    )

    assert diff.base_revision == "base"
    assert diff.target_revision == "target"
    assert diff.structure.added_modules == ("app.models.user",)
    assert diff.structure.removed_modules == ("app.services.users",)
    assert diff.architecture is not None
    assert diff.architecture.added_assignments == (
        LayerAssignment(layer=MODELS, module="app.models.user"),
    )
    assert diff.metrics is not None
    assert diff.metrics.removed_isolates == ("app.services.users",)


def test_compare_graphs_architecture_none_when_layers_missing():
    base = replace(
        _graph(("a", "b"), (("a", "b"),)),
        metrics=_full_metrics(_graph(("a", "b"), (("a", "b"),))),
    )
    target = replace(
        _graph(("a", "c"), (("a", "c"),)),
        metrics=_full_metrics(_graph(("a", "c"), (("a", "c"),))),
    )

    diff = compare_graphs(
        base, target, base_revision="old", target_revision="new"
    )

    assert diff.structure.added_modules == ("c",)
    assert diff.architecture is None
    assert diff.metrics is not None
