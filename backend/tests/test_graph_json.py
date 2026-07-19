from pathlib import Path

from backend.app.export.graph_json import graph_to_dict, write_graph_as_json_file
from backend.app.metrics.metrics_aggregator import analyze_metrics
from backend.app.models.graph_metrics_models import GraphMetrics
from backend.tests.utils import _graph


def test_graph_to_dict_includes_metrics():
    graph = _graph(("a", "b"), (("a", "b"),))
    metrics = analyze_metrics(graph)
    graph_with_metrics = type(graph)(
        repo_root=graph.repo_root,
        nodes=graph.nodes,
        edges=graph.edges,
        unresolved_imports=graph.unresolved_imports,
        errors=graph.errors,
        metrics=metrics,
    )

    payload = graph_to_dict(graph_with_metrics)

    assert payload["metrics"] is not None
    assert "centrality" in payload["metrics"]
    assert "isolates" in payload["metrics"]
    assert "cycles" in payload["metrics"]
    assert "hub_modules" in payload["metrics"]
    assert payload["metrics"]["centrality"]["pagerank_centrality"]["a"] > 0
    assert isinstance(payload["metrics"], dict)


def test_graph_to_dict_metrics_null_when_absent():
    graph = _graph(("a", "b"), (("a", "b"),))

    payload = graph_to_dict(graph)

    assert payload["metrics"] is None


def test_write_graph_as_json_file_round_trips_metrics(tmp_path: Path):
    import json
    from dataclasses import replace

    graph = _graph(("a", "b"), (("a", "b"),))
    graph = replace(graph, metrics=analyze_metrics(graph))
    out = tmp_path / "graph.json"

    write_graph_as_json_file(graph, out)

    loaded = json.loads(out.read_text())
    assert loaded["metrics"]["isolates"]["isolates"] == []
    assert set(loaded["metrics"]["centrality"]["in_degree_centrality"]) == {"a", "b"}
    assert isinstance(graph.metrics, GraphMetrics)
