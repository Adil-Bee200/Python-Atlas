from pathlib import Path
from dataclasses import asdict
import json
from backend.app.models.graph_models import Graph

def path_to_str_factory(data):
    return {k: str(v) if isinstance(v, Path) else v for k, v in data}

def graph_to_dict(graph: Graph) -> dict:
    return {
        "repo_root" : str(graph.repo_root),
        "nodes" : [asdict(node, dict_factory=path_to_str_factory) for node in graph.nodes],
        "edges" : [asdict(edge) for edge in graph.edges],
        "unresolved_imports" : list(graph.unresolved_imports),
        "errors" : list(graph.errors),
    }

def print_graph_as_json_string(graph: Graph) -> str:
    print(json.dumps(graph_to_dict(graph), indent=4))

def write_graph_as_json_file(graph: Graph, file_path: Path) -> str:
    with open(file_path, "w") as f:
        json.dump(graph_to_dict(graph), f, indent=4)
    print(f"Graph written to {file_path}")