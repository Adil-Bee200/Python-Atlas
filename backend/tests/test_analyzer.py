'''
Integration tests for the analyzer module.
'''

from pathlib import Path

from backend.app.analysis.analyzer import analyze_repo
from backend.app.models.graph_models import Graph, GraphNode, GraphEdge
from backend.app.models.import_models import ParsedResult, ParsedModule, ParsedImport


def test_analyze_repo_valid_path(tmp_path: Path):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    (repo_path / "module1.py").write_text("variable1 = 1")
    graph = analyze_repo(repo_path)
    
    assert isinstance(graph, Graph)
    assert graph.repo_root == repo_path
    assert len(graph.nodes) == 1
    assert len(graph.edges) == 0
    assert len(graph.unresolved_imports) == 0
    assert len(graph.errors) == 0
    assert set(graph.nodes) == {
        GraphNode("module1", Path("module1.py"), 0, 0),
    }
    assert set(graph.edges) == set()
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()
