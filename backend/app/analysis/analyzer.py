from pathlib import Path
from dataclasses import replace

from backend.app.config.defaults import DEFAULT_CONFIGURATION
from backend.app.config.models import Configuration
from backend.app.scanner.repo_scanner import scan_repo, verify_repo_path
from backend.app.parser.module_parser import parse_all_modules
from backend.app.graph.graph_builder import build_graph
from backend.app.models.graph_models import Graph
from backend.app.metrics.metrics_aggregator import analyze_metrics


def analyze_repo(
    repo_path: Path | str,
    config: Configuration | None = None,
) -> Graph:
    config = config if config is not None else DEFAULT_CONFIGURATION
    repo_path = Path(repo_path).expanduser().resolve()

    try:
        verify_repo_path(repo_path)
    except (FileNotFoundError, NotADirectoryError) as e:
        raise ValueError(f"Invalid repository path: {e}") from e

    scan_result = scan_repo(repo_path, ignore=config.ignore)
    parsed_result = parse_all_modules(scan_result)
    graph = build_graph(parsed_result)
    metrics = analyze_metrics(graph, entry_points=config.entry_points)
    return replace(graph, metrics=metrics)


def print_graph_summary(graph: Graph) -> None:
    print(f"Analyzing repository at {graph.repo_root}")
    print(f"Total modules: {len(graph.nodes)}")
    print(f"Total local dependencies: {len(graph.edges)}")
    print(f"Total unresolved imports: {len(graph.unresolved_imports)}")
    print(f"Total errors: {len(graph.errors)}")

    print("Top 10 modules by fan-in:")
    sorted_modules = sorted(graph.nodes, key=lambda x: x.fan_in, reverse=True)
    for module in sorted_modules[:10]:
        print(f"{module.module_path}: {module.fan_in}")

    sorted_modules = sorted(graph.nodes, key=lambda x: x.fan_out, reverse=True)
    print("Top 10 modules by fan-out:")
    for module in sorted_modules[:10]:
        print(f"{module.module_path}: {module.fan_out}")

    print("Edges:")
    for edge in graph.edges:
        print(f"{edge.source} -> {edge.target} ({edge.import_count})")

    print("Unresolved imports:")
    for import_str in graph.unresolved_imports:
        print(f"{import_str}")

    print("Errors:")
    for error in graph.errors:
        print(f"{error}")

    if graph.metrics is not None:
        print(graph.metrics)
