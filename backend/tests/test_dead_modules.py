from backend.app.metrics.dead_modules import analyze_dead_modules
from backend.app.models.graph_metrics_models import GraphDeadModules
from backend.tests.utils import _graph

def test_analyze_dead_modules_no_dead_modules():
    graph = _graph(("a", "b", "c", "d", "e", "f"), (("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("e", "f")))
    entry_points = ("a",)
    metrics = analyze_dead_modules(graph, entry_points)
    assert set(metrics.dead_modules) == set()
    assert metrics.dead_modules_percentage == 0.0

def test_analyze_dead_modules_no_entry_points():
    graph = _graph(("a", "b", "c", "d", "e", "f"), (("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("e", "f")))
    entry_points = ()
    metrics = analyze_dead_modules(graph, entry_points)
    assert set(metrics.dead_modules) == {
        GraphDeadModules("a", "Unreached by entry points"),
        GraphDeadModules("b", "Unreached by entry points"),
        GraphDeadModules("c", "Unreached by entry points"),
        GraphDeadModules("d", "Unreached by entry points"),
        GraphDeadModules("e", "Unreached by entry points"),
        GraphDeadModules("f", "Unreached by entry points"),
    }
    assert metrics.dead_modules_percentage == 6/6

def test_analyze_dead_modules_only_entry_points():
    graph = _graph(("a",), ())
    entry_points = ("a",)
    metrics = analyze_dead_modules(graph, entry_points)
    assert set(metrics.dead_modules) == set()
    assert metrics.dead_modules_percentage == 0.0

def test_analyze_dead_modules_no_edges():
    graph = _graph(("a", "b", "c", "d", "e", "f"), ())
    entry_points = ("a",)
    metrics = analyze_dead_modules(graph, entry_points)
    assert set(metrics.dead_modules) == {
        GraphDeadModules("b", "Unreached by entry points"),
        GraphDeadModules("c", "Unreached by entry points"),
        GraphDeadModules("d", "Unreached by entry points"),
        GraphDeadModules("e", "Unreached by entry points"),
        GraphDeadModules("f", "Unreached by entry points"),
    }
    assert metrics.dead_modules_percentage == 5/6

def test_analyze_dead_modules_with_one_dead_module():
    graph = _graph(("a", "b", "c", "d", "e", "f"), (("a", "b"), ("b", "c"), ("c", "d"), ("d", "e")))
    entry_points = ("a",)
    metrics = analyze_dead_modules(graph, entry_points)
    assert set(metrics.dead_modules) == {GraphDeadModules("f", "Unreached by entry points")}
    assert metrics.dead_modules_percentage == 1/6

def test_analyze_dead_modules_with_multiple_dead_modules():
    graph = _graph(("a", "b", "c", "d", "e", "f"), (("a", "c"), ("c", "d"), ("d", "e")))
    entry_points = ("a",)
    metrics = analyze_dead_modules(graph, entry_points)
    assert set(metrics.dead_modules) == {
        GraphDeadModules("b", "Unreached by entry points"),
        GraphDeadModules("f", "Unreached by entry points"),
    }
    assert metrics.dead_modules_percentage == 2/6

def test_analyze_dead_modules_connected_dead_modules():
    graph = _graph(("a", "b", "c", "d", "e", "f"), (("a", "b"), ("a", "c"), ("d", "e"), ("e", "f"), ("d", "f")))
    entry_points = ("a",)
    metrics = analyze_dead_modules(graph, entry_points)
    assert set(metrics.dead_modules) == {
        GraphDeadModules("d", "Unreached by entry points"),
        GraphDeadModules("e", "Unreached by entry points"),
        GraphDeadModules("f", "Unreached by entry points"),
    }
    assert metrics.dead_modules_percentage == 3/6

def test_analyze_dead_modules_with_multiple_entry_points_one_dead_module():
    graph = _graph(("a", "b", "c", "d", "e", "f"), (("a", "b"), ("a", "c"), ("d", "e")))
    entry_points = ("a", "d")
    metrics = analyze_dead_modules(graph, entry_points)
    assert set(metrics.dead_modules) == {
        GraphDeadModules("f", "Unreached by entry points"),
    }
    assert metrics.dead_modules_percentage == 1/6

def test_analyze_dead_modules_with_multiple_entry_points_multiple_dead_modules():
    graph = _graph(("a", "b", "c", "d", "e", "f"), (("a", "b"),))
    entry_points = ("a", "d")
    metrics = analyze_dead_modules(graph, entry_points)
    assert set(metrics.dead_modules) == {
        GraphDeadModules("c", "Unreached by entry points"),
        GraphDeadModules("e", "Unreached by entry points"),
        GraphDeadModules("f", "Unreached by entry points"),
    }
    assert metrics.dead_modules_percentage == 3/6

def test_analyze_dead_modules_all_entry_points_no_edges():
    graph = _graph(("a", "b", "c", "d", "e", "f"), ())
    entry_points = ("a", "b", "c", "d", "e", "f")
    metrics = analyze_dead_modules(graph, entry_points)
    assert set(metrics.dead_modules) == set()
    assert metrics.dead_modules_percentage == 0.0