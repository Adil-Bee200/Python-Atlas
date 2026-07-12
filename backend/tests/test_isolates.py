from pathlib import Path

import pytest

from backend.app.metrics.isolates import analyze_isolates
from backend.app.models.graph_metrics_models import GraphIsolatesMetrics
from backend.tests.utils import _graph, _node, _edge
from backend.app.models.graph_models import Graph


def test_analyze_isolates_empty_graph():
    metrics = analyze_isolates(_graph(()))

    assert isinstance(metrics, GraphIsolatesMetrics)
    assert metrics.isolates == ()


def test_analyze_isolates_single_module_is_isolated():
    metrics = analyze_isolates(_graph(("alone",)))

    assert metrics.isolates == ("alone",)


def test_analyze_isolates_all_modules_disconnected():
    metrics = analyze_isolates(_graph(("a", "b", "c")))

    assert set(metrics.isolates) == {"a", "b", "c"}
    assert len(metrics.isolates) == 3
    assert isinstance(metrics.isolates, tuple)


def test_analyze_isolates_fully_connected_pair_has_none():
    metrics = analyze_isolates(_graph(("a", "b"), edges=(("a", "b"),)))

    assert metrics.isolates == ()


def test_analyze_isolates_mixed_connected_and_orphans():
    metrics = analyze_isolates(
        _graph(
            ("core", "api", "orphan_a", "orphan_b"),
            edges=(("api", "core"),),
        )
    )

    assert set(metrics.isolates) == {"orphan_a", "orphan_b"}
    assert len(metrics.isolates) == 2


def test_analyze_isolates_one_way_dependency_means_neither_is_isolated():
    # Importer has out-degree, importee has in-degree = both degree > 0.
    metrics = analyze_isolates(_graph(("importer", "importee"), edges=(("importer", "importee"),)))

    assert metrics.isolates == ()


def test_analyze_isolates_chain_has_no_isolates():
    metrics = analyze_isolates(
        _graph(("a", "b", "c"), edges=(("a", "b"), ("b", "c")))
    )

    assert metrics.isolates == ()


def test_analyze_isolates_star_leaves_are_not_isolates():
    metrics = analyze_isolates(
        _graph(
            ("hub", "leaf_a", "leaf_b", "orphan"),
            edges=(("leaf_a", "hub"), ("leaf_b", "hub")),
        )
    )

    assert metrics.isolates == ("orphan",)


def test_analyze_isolates_self_loop_is_not_isolated():
    # NetworkX treats a node with only a self-loop as non-isolated (degree > 0).
    metrics = analyze_isolates(_graph(("loopy",), edges=(("loopy", "loopy"),)))

    assert metrics.isolates == ()


def test_analyze_isolates_nested_module_paths():
    metrics = analyze_isolates(
        _graph(
            ("app.core.config", "app.api.users", "app.utils.helpers", "scripts.oneshot"),
            edges=(("app.api.users", "app.core.config"),),
        )
    )

    assert set(metrics.isolates) == {"app.utils.helpers", "scripts.oneshot"}


def test_analyze_isolates_returns_frozen_metrics_type():
    metrics = analyze_isolates(_graph(("a", "b")))

    assert isinstance(metrics, GraphIsolatesMetrics)
    assert isinstance(metrics.isolates, tuple)
    with pytest.raises(AttributeError):
        metrics.isolates = ("changed",)  # type: ignore[misc]


def test_analyze_isolates_duplicate_edges_still_not_isolated():
    graph = Graph(
        repo_root=Path("test_repo"),
        nodes=(_node("a"), _node("b"), _node("orphan")),
        edges=(
            _edge("a", "b", import_count=3),
            _edge("a", "b", import_count=1),
        ),
        unresolved_imports=(),
        errors=(),
    )
    metrics = analyze_isolates(graph)

    assert metrics.isolates == ("orphan",)


def test_analyze_isolates_ignores_unresolved_imports_and_errors_fields():
    graph = Graph(
        repo_root=Path("test_repo"),
        nodes=(_node("a"), _node("b")),
        edges=(),
        unresolved_imports=("from numpy import array",),
        errors=("broken_module",),
    )
    metrics = analyze_isolates(graph)

    assert set(metrics.isolates) == {"a", "b"}
