from pathlib import Path

from app.scanner.repo_scanner import scan_repo, verify_repo_path
from app.parser.parser import parse_repo
from app.graph.graph_builder import build_graph
from app.models.graph_models import Graph

def analyze_repo(repo_path: Path) -> Graph:
    repo_path = Path(repo_path).expanduser().resolve()

    try:
        verify_repo_path(repo_path)
    except (FileNotFoundError, NotADirectoryError) as e:
        raise ValueError(f"Invalid repository path: {e}")

    scan_result = scan_repo(repo_path)
    parsed_result = parse_repo(scan_result)
    graph = build_graph(parsed_result)
    return graph