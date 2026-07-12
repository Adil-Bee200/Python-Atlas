from pathlib import Path

from backend.app.scanner.repo_scanner import scan_repo, verify_repo_path
from backend.app.parser.module_parser import parse_all_modules
from backend.app.graph.graph_builder import build_graph
from backend.app.models.graph_models import Graph
import sys
from backend.app.export.graph_json import print_graph_as_json_string
from backend.app.metrics.centrality import analyze_centrality

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

        print_graph_as_json_string(graph)
        metrics = analyze_centrality(graph)
        print(metrics)