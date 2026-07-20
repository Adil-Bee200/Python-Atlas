from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any
import json

from backend.app.models.graph_metrics_models import GraphDifference
from backend.app.models.graph_models import Graph


def _json_ready(value: Any) -> Any:
    """Recursively convert dataclasses, Paths, and tuples into JSON-safe values."""
    if is_dataclass(value) and not isinstance(value, type):
        return {k: _json_ready(v) for k, v in asdict(value).items()}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {k: _json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def path_to_str_factory(data):
    return {k: str(v) if isinstance(v, Path) else v for k, v in data}


def graph_to_dict(graph: Graph) -> dict:
    return {
        "repo_root": str(graph.repo_root),
        "nodes": [asdict(node, dict_factory=path_to_str_factory) for node in graph.nodes],
        "edges": [asdict(edge) for edge in graph.edges],
        "unresolved_imports": list(graph.unresolved_imports),
        "errors": list(graph.errors),
        "metrics": _json_ready(graph.metrics) if graph.metrics is not None else None,
    }


def graph_difference_to_dict(difference: GraphDifference) -> dict:
    return _json_ready(difference)


def print_graph_as_json_string(graph: Graph) -> None:
    print(json.dumps(graph_to_dict(graph), indent=4))


def write_graph_as_json_file(graph: Graph, file_path: Path | str) -> None:
    with open(file_path, "w") as f:
        json.dump(graph_to_dict(graph), f, indent=4)
    print(f"Graph written to {file_path}")


def write_graph_difference_as_json_file(
    difference: GraphDifference,
    file_path: Path | str,
) -> None:
    with open(file_path, "w") as f:
        json.dump(graph_difference_to_dict(difference), f, indent=4)
    print(f"Graph difference written to {file_path}")
