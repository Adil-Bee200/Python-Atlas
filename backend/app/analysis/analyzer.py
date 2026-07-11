from pathlib import Path

from backend.app.scanner.repo_scanner import scan_repo, verify_repo_path
from backend.app.parser.module_parser import parse_all_modules
from backend.app.graph.graph_builder import build_graph
from backend.app.models.graph_models import Graph

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