from backend.app.graph.graph_builder import build_graph
from backend.app.models.import_models import ParsedResult, ParsedModule
from backend.app.models.graph_models import Graph, GraphNode, GraphEdge
from pathlib import Path

def test_graph_builder_basic():
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
    assert graph.nodes == (
        GraphNode("test_module", Path("test_repo/test_module.py"), 0, 0),
    )
    assert graph.edges == tuple()
    assert graph.unresolved_imports == tuple()
    assert graph.errors == tuple()

""" 
Notes:
Testing scenarios (check for accurate fan_in and fan_out in all cases):
- No imports + multiple modules
- No imports + single module
- Simple 2 modules + 1 import
- Multiple imports but only 1 module (should go to unresolved imports)
- Mix of local and external imports
- Only errors (should go to errors)
- Mix of local and external imports + errors
"""