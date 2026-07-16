from backend.app.metrics.dead_modules import analyze_dead_modules
from backend.app.models.graph_models import Graph
from backend.app.models.graph_metrics_models import GraphDeadModulesMetrics, GraphDeadModules
from backend.tests.utils import _graph

def test_analyze_dead_modules_no_dead_modules():
    graph = _graph(("a", "b", "c", "d", "e", "f"), (("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("e", "f")))
    entry_points = ("a",)
    metrics = analyze_dead_modules(graph, entry_points)
    assert metrics == GraphDeadModulesMetrics(dead_modules=(), dead_modules_percentage=0.0)

def test_analyze_dead_modules_with_one_dead_module():
    graph = _graph(("a", "b", "c", "d", "e", "f"), (("a", "b"), ("b", "c"), ("c", "d"), ("d", "e")))
    entry_points = ("a",)
    metrics = analyze_dead_modules(graph, entry_points)
    assert metrics == GraphDeadModulesMetrics(dead_modules=(GraphDeadModules("f", "Unreached by entry points"),), dead_modules_percentage=1/6)

def test_analyze_dead_modules_with_multiple_dead_modules():
    graph = _graph(("a", "b", "c", "d", "e", "f"), (("a", "c"), ("c", "d"), ("d", "e")))
    entry_points = ("a",)
    metrics = analyze_dead_modules(graph, entry_points)
    assert metrics == GraphDeadModulesMetrics(dead_modules=(GraphDeadModules("b", "Unreached by entry points"), GraphDeadModules("f", "Unreached by entry points"),), dead_modules_percentage=2/6)

