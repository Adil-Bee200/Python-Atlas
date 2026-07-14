import pytest

from backend.app.metrics.centrality import analyze_centrality
from backend.app.metrics.hub_modules import (
    DEFAULT_IN_DEGREE_PERCENTILE,
    HUB_MODULES_MAX_OUT_DEGREE,
    HUB_MODULES_MAX_OUT_DEGREE_FLOOR,
    HUB_MODULES_MIN_IN_DEGREE,
    analyze_hub_modules,
)
from backend.app.metrics.metrics_aggregator import analyze_metrics
from backend.app.models.graph_metrics_models import GraphHubModulesMetrics
from backend.tests.utils import _graph


def test_analyze_hub_modules_too_few_nodes_returns_empty():
    graph = _graph(("a", "b"), edges=(("a", "b"),))
    centrality = analyze_centrality(graph)

    metrics = analyze_hub_modules(graph, centrality)

    assert isinstance(metrics, GraphHubModulesMetrics)
    assert metrics.hub_modules == ()
    assert metrics.in_degree_threshold == 0.0
    assert metrics.max_out_degree == 0.0


def test_analyze_hub_modules_star_identifies_hub():
    # Leaves import hub => leaf -> hub. Hub has high in / zero out.
    graph = _graph(
        ("hub", "leaf_a", "leaf_b", "leaf_c"),
        edges=(
            ("leaf_a", "hub"),
            ("leaf_b", "hub"),
            ("leaf_c", "hub"),
        ),
    )
    centrality = analyze_centrality(graph)
    metrics = analyze_hub_modules(graph, centrality)

    assert len(metrics.hub_modules) == 1
    hub = metrics.hub_modules[0]
    assert hub.module == "hub"
    assert hub.in_degree == 3
    assert hub.out_degree == 0
    assert hub.pagerank == pytest.approx(centrality.pagerank_centrality["hub"])
    assert hub.hub_score > 0


def test_analyze_hub_modules_high_fan_out_is_not_a_hub():
    graph = _graph(
        ("aggregator", "dep_a", "dep_b", "dep_c"),
        edges=(
            ("aggregator", "dep_a"),
            ("aggregator", "dep_b"),
            ("aggregator", "dep_c"),
        ),
    )
    centrality = analyze_centrality(graph)
    metrics = analyze_hub_modules(graph, centrality)

    assert metrics.hub_modules == ()


def test_analyze_hub_modules_thresholds_use_networkx_normalization():
    graph = _graph(
        ("hub", "a", "b", "c", "d"),
        edges=(
            ("a", "hub"),
            ("b", "hub"),
            ("c", "hub"),
            ("d", "hub"),
        ),
    )
    centrality = analyze_centrality(graph)
    metrics = analyze_hub_modules(graph, centrality)

    n = len(graph.nodes)
    denom = n - 1
    expected_min_in = HUB_MODULES_MIN_IN_DEGREE / denom
    expected_max_out = max(
        HUB_MODULES_MAX_OUT_DEGREE / denom,
        HUB_MODULES_MAX_OUT_DEGREE_FLOOR,
    )

    assert metrics.in_degree_threshold >= expected_min_in
    assert metrics.max_out_degree == pytest.approx(expected_max_out)


def test_analyze_hub_modules_sorted_by_hub_score_descending():
    # Two hubs: core is imported by more modules than util.
    # Use a milder percentile so both clear the in-degree bar.
    graph = _graph(
        ("core", "util", "a", "b", "c", "d"),
        edges=(
            ("a", "core"),
            ("b", "core"),
            ("c", "core"),
            ("d", "core"),
            ("a", "util"),
            ("b", "util"),
            ("c", "util"),
        ),
    )
    centrality = analyze_centrality(graph)
    metrics = analyze_hub_modules(graph, centrality, in_degree_percentile=50.0)

    hub_names = [hub.module for hub in metrics.hub_modules]
    assert "core" in hub_names
    assert "util" in hub_names
    scores = [hub.hub_score for hub in metrics.hub_modules]
    assert scores == sorted(scores, reverse=True)
    assert metrics.hub_modules[0].module == "core"


def test_analyze_hub_modules_custom_percentile():
    graph = _graph(
        ("hub", "a", "b", "c"),
        edges=(
            ("a", "hub"),
            ("b", "hub"),
            ("c", "hub"),
        ),
    )
    centrality = analyze_centrality(graph)
    default = analyze_hub_modules(graph, centrality, DEFAULT_IN_DEGREE_PERCENTILE)
    strict = analyze_hub_modules(graph, centrality, 99.0)

    assert strict.in_degree_threshold >= default.in_degree_threshold


def test_analyze_metrics_includes_hub_modules():
    graph = _graph(
        ("hub", "leaf_a", "leaf_b", "leaf_c"),
        edges=(
            ("leaf_a", "hub"),
            ("leaf_b", "hub"),
            ("leaf_c", "hub"),
        ),
    )
    metrics = analyze_metrics(graph)

    assert metrics.hub_modules.hub_modules[0].module == "hub"
