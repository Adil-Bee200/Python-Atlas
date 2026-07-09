from backend.app.graph.graph_builder import build_graph
from backend.app.models.import_models import ParsedResult, ParsedModule, ParsedImport
from backend.app.models.graph_models import Graph, GraphNode, GraphEdge
from pathlib import Path


def test_graph_builder_no_imports_single_module():
    parsed_result = ParsedResult(
        repo_root=Path("test_repo"),
        modules=(
            ParsedModule(
                path=Path("test_repo/test_module.py"),
                module_path="test_module",
                imports=tuple(),
                error=None,
            ),
        ),
    )
    graph = build_graph(parsed_result)
    assert isinstance(graph, Graph)
    assert graph.repo_root == Path("test_repo")
    assert set(graph.nodes) == {
        GraphNode("test_module", Path("test_repo/test_module.py"), 0, 0),
    }
    assert set(graph.edges) == set()
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()

def test_graph_builder_no_imports_multiple_modules():
    parsed_result = ParsedResult(
        repo_root=Path("test_repo"),
        modules=(
            ParsedModule(
                path=Path("test_repo/module1.py"),
                module_path="module1",
                imports=tuple(),
                error=None,
            ),
            ParsedModule(
                path=Path("test_repo/module2.py"),
                module_path="module2",
                imports=tuple(),
                error=None,
            ),
            ParsedModule(
                path=Path("test_repo/module3.py"),
                module_path="module3",
                imports=tuple(),
                error=None,
            ),
        )
    )

    graph = build_graph(parsed_result)
    assert isinstance(graph, Graph)
    assert graph.repo_root == Path("test_repo")
    assert set(graph.nodes) == {
        GraphNode("module1", Path("test_repo/module1.py"), 0, 0),
        GraphNode("module2", Path("test_repo/module2.py"), 0, 0),
        GraphNode("module3", Path("test_repo/module3.py"), 0, 0),
    }
    assert set(graph.edges) == set()
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()

def test_graph_builder_simple_2_modules_1_import():
    parsed_result = ParsedResult(
        repo_root=Path("test_repo"),
        modules = (
            ParsedModule(
                path=Path("test_repo/module1.py"),
                module_path="module1",
                imports=tuple(),
                error=None
            ),
            ParsedModule(
                path=Path("test_repo/module2.py"),
                module_path="module2",
                imports=(
                    ParsedImport(
                        raw_import="from module1 import variable1",
                        module_name="module1"
                    ),
                ),
                error=None
            )
        )
    )

    graph = build_graph(parsed_result)
    assert isinstance(graph, Graph)
    assert graph.repo_root == Path("test_repo")
    assert set(graph.nodes) == {
        GraphNode("module1", Path("test_repo/module1.py"), 1, 0),
        GraphNode("module2", Path("test_repo/module2.py"), 0, 1),
    }
    assert set(graph.edges) == {
        GraphEdge("module2", "module1", "from module1 import variable1"),
    }
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()

def test_graph_builder_import_at_different_levels():
    parsed_result = ParsedResult(
        repo_root=Path("test_repo"),
        modules = (
            ParsedModule(
                path=Path("test_repo/module1.py"),
                module_path="module1",
                imports=(
                    ParsedImport(
                        raw_import="from config.config import CONFIG",
                        module_name="config.config"
                    ),
                ),
                error=None
            ),
            ParsedModule(
                path=Path("test_repo/config/config.py"),
                module_path="config.config",
                imports=(
                    ParsedImport(
                    raw_import="from app.models.model import Model",
                    module_name="app.models.model"
                    ),
                ),
                error=None
            ),
            ParsedModule(
                path=Path("test_repo/app/models/model.py"),
                module_path="app.models.model",
                imports=tuple(),
                error=None
            )
        )
    )

    graph = build_graph(parsed_result)
    assert isinstance(graph, Graph)
    assert graph.repo_root == Path("test_repo")
    assert set(graph.nodes) == {
        GraphNode("module1", Path("test_repo/module1.py"), 0, 1),
        GraphNode("config.config", Path("test_repo/config/config.py"), 1, 1),
        GraphNode("app.models.model", Path("test_repo/app/models/model.py"), 1, 0),
    }
    assert set(graph.edges) == {
        GraphEdge("config.config", "app.models.model", "from app.models.model import Model"),
        GraphEdge("module1", "config.config", "from config.config import CONFIG"),
    }
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()

""" 
Notes:
Testing scenarios (check for accurate fan_in and fan_out in all cases):
- No imports + multiple modules DONE
- No imports + single module DONE
- Simple 2 modules + 1 import
- Multiple imports but only 1 module (should go to unresolved imports)
- Mix of local and external imports
- Only errors (should go to errors)
- Mix of local and external imports + errors
"""