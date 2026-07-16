from backend.app.metrics.entry_points import resolve_entry_points
from backend.app.metrics.metrics_aggregator import analyze_metrics
from backend.tests.utils import _graph


def test_resolve_entry_points_all_found_as_modules():
    graph = _graph(("app.main", "app.util"))

    resolution = resolve_entry_points(graph, ("app.main", "app.util"))

    assert resolution.resolved == ("app.main", "app.util")
    assert resolution.missing == ()


def test_resolve_entry_points_from_file_paths():
    graph = _graph(("app.main", "app.util"))

    resolution = resolve_entry_points(graph, ("app/main.py",))

    assert resolution.resolved == ("app.main",)
    assert resolution.missing == ()


def test_resolve_entry_points_reports_missing_originals():
    graph = _graph(("app.main",))

    resolution = resolve_entry_points(
        graph,
        ("app.main", "missing.module", "also/missing.py"),
    )

    assert resolution.resolved == ("app.main",)
    assert resolution.missing == ("missing.module", "also/missing.py")


def test_analyze_metrics_skips_dead_modules_if_any_entry_point_missing():
    graph = _graph(
        ("main", "util", "orphan"),
        edges=(("main", "util"),),
    )

    metrics = analyze_metrics(graph, entry_points=("main", "does.not.exist"))

    assert metrics.dead_modules is None
    assert metrics.missing_entry_points == ("does.not.exist",)


def test_analyze_metrics_does_not_use_partial_valid_entry_points():
    graph = _graph(
        ("main", "util", "orphan"),
        edges=(("main", "util"),),
    )

    # Even though "main" is valid, a single missing entry point blocks analysis.
    metrics = analyze_metrics(graph, entry_points=("main", "ghost"))

    assert metrics.dead_modules is None
    assert metrics.missing_entry_points == ("ghost",)


def test_analyze_metrics_runs_dead_modules_only_when_all_entry_points_exist():
    graph = _graph(
        ("main", "util", "orphan"),
        edges=(("main", "util"),),
    )

    metrics = analyze_metrics(graph, entry_points=("main",))

    assert metrics.missing_entry_points == ()
    assert metrics.dead_modules is not None
    assert {d.module for d in metrics.dead_modules.dead_modules} == {"orphan"}
