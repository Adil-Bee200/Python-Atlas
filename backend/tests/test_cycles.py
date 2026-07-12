from pathlib import Path

import pytest

from backend.app.metrics.cycles import analyze_cycles
from backend.app.models.graph_metrics_models import GraphCyclesMetrics
from backend.tests.utils import _graph, _node, _edge
from backend.app.models.graph_models import Graph


def test_analyze_cycles_empty_graph():
    metrics = analyze_cycles(_graph(()))

    assert isinstance(metrics, GraphCyclesMetrics)
    assert metrics.cycles == ()


def test_analyze_cycles_single_module_no_edges():
    metrics = analyze_cycles(_graph(("alone",)))

    assert metrics.cycles == ()


def test_analyze_cycles_single_module_self_loop(): # self-loop is a cycle
    metrics = analyze_cycles(
        _graph(("app.core.config",), edges=(("app.core.config", "app.core.config"),))
    )

    assert isinstance(metrics, GraphCyclesMetrics)
    assert metrics.cycles == (("app.core.config",),)


def test_analyze_cycles_one_way_dependency_is_not_a_cycle():
    metrics = analyze_cycles(
        _graph(("importer", "importee"), edges=(("importer", "importee"),))
    )

    assert metrics.cycles == ()


def test_analyze_cycles_chain_has_no_cycles():
    metrics = analyze_cycles(
        _graph(("a", "b", "c"), edges=(("a", "b"), ("b", "c")))
    )

    assert metrics.cycles == ()


def test_analyze_cycles_two_module_cycle():
    metrics = analyze_cycles(
        _graph(
            ("app.core.config", "app.api.users"),
            edges=(
                ("app.core.config", "app.api.users"),
                ("app.api.users", "app.core.config"),
            ),
        )
    )

    assert isinstance(metrics, GraphCyclesMetrics)
    assert metrics.cycles == (("app.api.users", "app.core.config"),)


def test_analyze_cycles_three_module_cycle():
    metrics = analyze_cycles(
        _graph(
            ("app.core.config", "app.api.users", "app.db.models"),
            edges=(
                ("app.core.config", "app.api.users"),
                ("app.api.users", "app.db.models"),
                ("app.db.models", "app.core.config"),
            ),
        )
    )

    assert isinstance(metrics, GraphCyclesMetrics)
    assert metrics.cycles == (("app.api.users", "app.db.models", "app.core.config"),)


def test_analyze_cycles_ignores_modules_outside_the_cycle():
    metrics = analyze_cycles(
        _graph(
            ("a", "b", "orphan", "leaf"),
            edges=(("a", "b"), ("b", "a"), ("leaf", "a")),
        )
    )

    assert metrics.cycles == (("a", "b"),)


def test_analyze_cycles_multiple_disjoint_cycles_are_sorted():
    metrics = analyze_cycles(
        _graph(
            ("a", "b", "c", "d"),
            edges=(
                ("c", "d"),
                ("d", "c"),
                ("a", "b"),
                ("b", "a"),
            ),
        )
    )

    # Lexicographic sort makes it so ("a", "b") before ("c", "d")
    assert metrics.cycles == (("a", "b"), ("c", "d"))


def test_analyze_cycles_overlapping_cycles():
    # Triangle plus the reverse edge on one side yields two directed cycles.
    metrics = analyze_cycles(
        _graph(
            ("a", "b", "c"),
            edges=(
                ("a", "b"),
                ("b", "c"),
                ("c", "a"),
                ("a", "c"),
                ("c", "b"),
                ("b", "a"),
            ),
        )
    )

    assert metrics.cycles == (
        ("a", "b"),
        ("a", "b", "c"),
        ("a", "c"),
        ("a", "c", "b"),
        ("b", "c"),
    )


def test_analyze_cycles_returns_frozen_metrics_type():
    metrics = analyze_cycles(_graph(("a", "b"), edges=(("a", "b"), ("b", "a"))))

    assert isinstance(metrics, GraphCyclesMetrics)
    assert isinstance(metrics.cycles, tuple)
    with pytest.raises(AttributeError):
        metrics.cycles = () 

def test_analyze_cycles_duplicate_edges_still_one_cycle():
    graph = Graph(
        repo_root=Path("test_repo"),
        nodes=(_node("a"), _node("b")),
        edges=(
            _edge("a", "b", import_count=3),
            _edge("b", "a", import_count=2),
            _edge("a", "b", import_count=1),
        ),
        unresolved_imports=(),
        errors=(),
    )
    metrics = analyze_cycles(graph)

    assert metrics.cycles == (("a", "b"),)


def test_analyze_cycles_ignores_unresolved_imports_and_errors_fields():
    graph = Graph(
        repo_root=Path("test_repo"),
        nodes=(_node("a"), _node("b")),
        edges=(_edge("a", "b"), _edge("b", "a")),
        unresolved_imports=("from numpy import array",),
        errors=("broken_module",),
    )
    metrics = analyze_cycles(graph)

    assert metrics.cycles == (("a", "b"),)
