from pathlib import Path

from backend.app.scanner.repo_scanner import scan_repo, verify_repo_path
from backend.app.parser.module_parser import parse_all_modules
from backend.app.graph.graph_builder import build_graph
from backend.app.models.graph_models import Graph
import sys
from dataclasses import asdict
import json

def analyze_repo(repo_path: Path) -> Graph:
    repo_path = Path(repo_path).expanduser().resolve()

    try:
        verify_repo_path(repo_path)
    except (FileNotFoundError, NotADirectoryError) as e:
        raise ValueError(f"Invalid repository path: {e}")

    scan_result = scan_repo(repo_path)
    parsed_result = parse_all_modules(scan_result)
    graph = build_graph(parsed_result)
    return graph


def print_graph_summary(graph: Graph):
    print(f"Analyzing repository at {graph.repo_root}")
    print(f"Total modules: {len(graph.nodes)}")
    print(f"Total local dependencies: {len(graph.edges)}")
    print(f"Total unresolved imports: {len(graph.unresolved_imports)}")
    print(f"Total errors: {len(graph.errors)}")

    print(f"Top 10 modules by fan-in:")
    sorted_modules = sorted(graph.nodes, key=lambda x: x.fan_in, reverse=True)
    for module in sorted_modules[:10]:
        print(f"{module.module_path}: {module.fan_in}")

    sorted_modules = sorted(graph.nodes, key=lambda x: x.fan_out, reverse=True)
    print(f"Top 10 modules by fan-out:")
    for module in sorted_modules[:10]:
        print(f"{module.module_path}: {module.fan_out}")

    print(f"Edges: ")
    for edge in graph.edges:
        print(f"{edge.source} -> {edge.target} ({edge.import_count})")

    print(f"Unresolved imports: ")
    for import_str in graph.unresolved_imports:
        print(f"{import_str}")
    
    print(f"Errors: ")
    for error in graph.errors:
        print(f"{error}")

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

def print_graph_to_json(graph: Graph) -> str:
    print(json.dumps(graph_to_dict(graph), indent=4))

def write_json_to_file(graph: Graph, file_path: Path) -> str:
    with open(file_path, "w") as f:
        json.dump(graph_to_dict(graph), f, indent=4)
    print(f"Graph written to {file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No path provided")
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("Too many arguments")
        sys.exit(1)
    else:
        user_input = sys.argv[1]

        try:
            graph = analyze_repo(user_input)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

        print_graph_to_json(graph)
        write_json_to_file(graph, "graph.json")