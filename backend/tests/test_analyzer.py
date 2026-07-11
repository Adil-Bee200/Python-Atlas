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


# Tests for basic functionality
'''
- Simple duplicate imports
- Multiple imports but only 1 module (should go to unresolved imports)
- Mix of local and external imports
- Only errors (should go to errors)
- Imports to files with errors 
'''

def test_analyze_repo_basic_2_modules_1_import(tmp_path: Path):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    (repo_path / "module1.py").write_text("from module2 import variable1")
    (repo_path / "module2.py").write_text("variable1 = 1")
    graph = analyze_repo(repo_path)
    assert isinstance(graph, Graph)
    assert graph.repo_root == repo_path
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    assert len(graph.unresolved_imports) == 0
    assert len(graph.errors) == 0


    assert set(graph.nodes) == {
        GraphNode("module1", Path("module1.py"), 0, 1),
        GraphNode("module2", Path("module2.py"), 1, 0),
    }
    assert set(graph.edges) == {
        GraphEdge("module1", "module2", 1, ("from module2 import variable1",)),
    }
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()

#No imports + multiple modules
def test_analyze_repo_no_imports_multiple_modules(tmp_path: Path):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    (repo_path / "module1.py").write_text("variable1 = 1")
    (repo_path / "module2.py").write_text("variable2 = 2")
    (repo_path / "module3.py").write_text("variable3 = 3")
    (repo_path / "module4.py").write_text('print("hello world")')
    graph = analyze_repo(repo_path)
    assert isinstance(graph, Graph)
    assert graph.repo_root == repo_path
    assert len(graph.nodes) == 4
    assert len(graph.edges) == 0
    assert len(graph.unresolved_imports) == 0
    assert len(graph.errors) == 0
    assert set(graph.nodes) == {
        GraphNode("module1", Path("module1.py"), 0, 0),
        GraphNode("module2", Path("module2.py"), 0, 0),
        GraphNode("module3", Path("module3.py"), 0, 0),
        GraphNode("module4", Path("module4.py"), 0, 0),
    }
    assert set(graph.edges) == set()
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()

# Simple duplicate imports
def test_analyze_repo_simple_duplicate_imports(tmp_path: Path):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    (repo_path / "module1.py").write_text("from module2 import variable1, variable2, variable3")
    (repo_path / "module2.py").write_text("variable1 = 1")
    graph = analyze_repo(repo_path)
    assert isinstance(graph, Graph)
    assert graph.repo_root == repo_path
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    assert len(graph.unresolved_imports) == 0
    assert len(graph.errors) == 0

    assert set(graph.nodes) == {
        GraphNode("module1", Path("module1.py"), 0, 1),
        GraphNode("module2", Path("module2.py"), 1, 0),
    }
    assert set(graph.edges) == {
        GraphEdge("module1", "module2", 1, ("from module2 import variable1, variable2, variable3",)),
    }
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()