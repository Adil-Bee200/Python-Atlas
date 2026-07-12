from pathlib import Path

import networkx as nx
import pytest

from backend.app.metrics.centrality import analyze_centrality
from backend.app.metrics.utils import convert_graph_to_networkx_graph
from backend.app.models.graph_metrics_models import GraphCentralityMetrics
from backend.tests.utils import _graph, _node, _edge
from backend.app.models.graph_models import Graph


def test_analyze_centrality_empty_graph():
    graph = _graph(())
    metrics = analyze_centrality(graph)

    assert isinstance(metrics, GraphCentralityMetrics)
    assert metrics.pagerank_centrality == {}
    assert metrics.betweenness_centrality == {}
    assert metrics.in_degree_centrality == {}
    assert metrics.out_degree_centrality == {}


def test_analyze_centrality_single_isolated_module():
    graph = _graph(("alone",))
    metrics = analyze_centrality(graph)

    assert set(metrics.pagerank_centrality) == {"alone"}
    assert metrics.pagerank_centrality["alone"] == pytest.approx(1.0)
    assert metrics.betweenness_centrality["alone"] == pytest.approx(0.0)
    ## NOTE: NetworkX normalizes by n-1; for n=1 it returns 1.0 as a special case.
    assert metrics.in_degree_centrality["alone"] == pytest.approx(1.0)
    assert metrics.out_degree_centrality["alone"] == pytest.approx(1.0)


def test_analyze_centrality_includes_every_module_in_all_metric_maps():
    graph = _graph(
        ("a", "b", "c", "isolated"),
        edges=(("a", "b"), ("b", "c")),
    )
    metrics = analyze_centrality(graph)
    expected = {"a", "b", "c", "isolated"}

    assert set(metrics.pagerank_centrality) == expected
    assert set(metrics.betweenness_centrality) == expected
    assert set(metrics.in_degree_centrality) == expected
    assert set(metrics.out_degree_centrality) == expected


def test_analyze_centrality_two_modules_one_import_degrees():
    # module2 imports module1  =>  module2 -> module1
    graph = _graph(("module1", "module2"), edges=(("module2", "module1"),))
    metrics = analyze_centrality(graph)

    assert metrics.in_degree_centrality["module1"] == pytest.approx(1.0)
    assert metrics.in_degree_centrality["module2"] == pytest.approx(0.0)
    assert metrics.out_degree_centrality["module1"] == pytest.approx(0.0)
    assert metrics.out_degree_centrality["module2"] == pytest.approx(1.0)
    assert metrics.pagerank_centrality["module1"] > metrics.pagerank_centrality["module2"]


def test_analyze_centrality_star_hub_has_highest_in_degree_and_pagerank():
    # leaves import hub  =>  leaf -> hub
    graph = _graph(
        ("hub", "leaf_a", "leaf_b", "leaf_c"),
        edges=(
            ("leaf_a", "hub"),
            ("leaf_b", "hub"),
            ("leaf_c", "hub"),
        ),
    )
    metrics = analyze_centrality(graph)

    assert metrics.in_degree_centrality["hub"] == pytest.approx(1.0)
    for leaf in ("leaf_a", "leaf_b", "leaf_c"):
        assert metrics.in_degree_centrality[leaf] == pytest.approx(0.0)
        assert metrics.out_degree_centrality[leaf] == pytest.approx(1 / 3)
        assert metrics.pagerank_centrality["hub"] > metrics.pagerank_centrality[leaf]

    assert metrics.out_degree_centrality["hub"] == pytest.approx(0.0)


def test_analyze_centrality_high_fan_out_module_has_highest_out_degree():
    graph = _graph(
        ("aggregator", "dep_a", "dep_b", "dep_c"),
        edges=(
            ("aggregator", "dep_a"),
            ("aggregator", "dep_b"),
            ("aggregator", "dep_c"),
        ),
    )
    metrics = analyze_centrality(graph)

    assert metrics.out_degree_centrality["aggregator"] == pytest.approx(1.0)
    for dep in ("dep_a", "dep_b", "dep_c"):
        assert metrics.out_degree_centrality[dep] == pytest.approx(0.0)
        assert metrics.in_degree_centrality[dep] == pytest.approx(1 / 3)


def test_analyze_centrality_chain_middle_node_has_highest_betweenness():
    # a -> b -> c
    graph = _graph(("a", "b", "c"), edges=(("a", "b"), ("b", "c")))
    metrics = analyze_centrality(graph)

    assert metrics.betweenness_centrality["b"] > metrics.betweenness_centrality["a"]
    assert metrics.betweenness_centrality["b"] > metrics.betweenness_centrality["c"]
    assert metrics.betweenness_centrality["a"] == pytest.approx(0.0)
    assert metrics.betweenness_centrality["c"] == pytest.approx(0.0)


def test_analyze_centrality_bridge_module_has_highest_betweenness():
    # left_a -> left_b -> bridge -> right_a -> right_b
    graph = _graph(
        ("left_a", "left_b", "bridge", "right_a", "right_b"),
        edges=(
            ("left_a", "left_b"),
            ("left_b", "bridge"),
            ("bridge", "right_a"),
            ("right_a", "right_b"),
        ),
    )
    metrics = analyze_centrality(graph)

    bridge_score = metrics.betweenness_centrality["bridge"]
    for module in ("left_a", "left_b", "right_a", "right_b"):
        assert bridge_score > metrics.betweenness_centrality[module]


def test_analyze_centrality_directed_cycle_has_symmetric_degree_metrics():
    graph = _graph(
        ("a", "b", "c"),
        edges=(("a", "b"), ("b", "c"), ("c", "a")),
    )
    metrics = analyze_centrality(graph)

    for module in ("a", "b", "c"):
        assert metrics.in_degree_centrality[module] == pytest.approx(0.5)
        assert metrics.out_degree_centrality[module] == pytest.approx(0.5)
        assert metrics.pagerank_centrality[module] == pytest.approx(1 / 3, abs=1e-6)
        assert metrics.betweenness_centrality[module] == pytest.approx(
            metrics.betweenness_centrality["a"]  # all modules have the same betweenness centrality in a cycle
        )


def test_analyze_centrality_isolated_module_among_connected_graph_has_zero_degree():
    graph = _graph(
        ("a", "b", "orphan"),
        edges=(("a", "b"),),
    )
    metrics = analyze_centrality(graph)

    assert metrics.in_degree_centrality["orphan"] == pytest.approx(0.0)
    assert metrics.out_degree_centrality["orphan"] == pytest.approx(0.0)
    assert metrics.betweenness_centrality["orphan"] == pytest.approx(0.0)
    assert metrics.pagerank_centrality["orphan"] < metrics.pagerank_centrality["b"]


def test_analyze_centrality_pagerank_sums_to_one():
    graph = _graph(
        ("a", "b", "c", "d"),
        edges=(("a", "b"), ("b", "c"), ("d", "c"), ("a", "c")),
    )
    metrics = analyze_centrality(graph)

    assert sum(metrics.pagerank_centrality.values()) == pytest.approx(1.0)


def test_analyze_centrality_matches_networkx_directly():
    graph = _graph(
        ("core", "api", "cli", "util"),
        edges=(
            ("api", "core"),
            ("cli", "core"),
            ("cli", "util"),
            ("api", "util"),
        ),
    )
    metrics = analyze_centrality(graph)
    nx_graph = convert_graph_to_networkx_graph(graph)

    expected_pagerank = nx.pagerank(nx_graph)
    expected_betweenness = nx.betweenness_centrality(nx_graph)
    expected_in_degree = nx.in_degree_centrality(nx_graph)
    expected_out_degree = nx.out_degree_centrality(nx_graph)

    for module in ("core", "api", "cli", "util"):
        assert metrics.pagerank_centrality[module] == pytest.approx(expected_pagerank[module])
        assert metrics.betweenness_centrality[module] == pytest.approx(
            expected_betweenness[module]
        )
        assert metrics.in_degree_centrality[module] == pytest.approx(expected_in_degree[module])
        assert metrics.out_degree_centrality[module] == pytest.approx(
            expected_out_degree[module]
        )


def test_analyze_centrality_nested_module_paths():
    graph = _graph(
        ("app.core.config", "app.api.users", "app.models.user"),
        edges=(
            ("app.api.users", "app.models.user"),
            ("app.api.users", "app.core.config"),
            ("app.models.user", "app.core.config"),
        ),
    )
    metrics = analyze_centrality(graph)

    assert metrics.in_degree_centrality["app.core.config"] == pytest.approx(1.0)
    assert metrics.out_degree_centrality["app.api.users"] == pytest.approx(1.0)
    assert metrics.pagerank_centrality["app.core.config"] > metrics.pagerank_centrality[
        "app.api.users"
    ]


def test_analyze_centrality_metric_values_are_non_negative():
    graph = _graph(
        ("a", "b", "c", "d"),
        edges=(("a", "b"), ("b", "c"), ("c", "a"), ("d", "a")),
    )
    metrics = analyze_centrality(graph)

    for values in (
        metrics.pagerank_centrality,
        metrics.betweenness_centrality,
        metrics.in_degree_centrality,
        metrics.out_degree_centrality,
    ):
        for score in values.values():
            assert score >= 0.0
