from backend.app.metrics.centrality import analyze_centrality
from backend.app.metrics.cycles import analyze_cycles
from backend.app.metrics.dead_modules import analyze_dead_modules
from backend.app.metrics.hub_modules import analyze_hub_modules
from backend.app.metrics.isolates import analyze_isolates
from backend.app.metrics.entry_points import resolve_entry_points
from backend.app.models.graph_models import Graph
from backend.app.models.graph_metrics_models import GraphMetrics


def analyze_metrics(
    graph: Graph,
    entry_points: tuple[str, ...] = (),
) -> GraphMetrics:
    # Hub modules depend on centrality, so centrality runs first.
    centrality = analyze_centrality(graph)
    isolates = analyze_isolates(graph)
    cycles = analyze_cycles(graph)
    hub_modules = analyze_hub_modules(graph, centrality)

    dead_modules = None
    resolved_entry_points = resolve_entry_points(graph, entry_points)
    if resolved_entry_points:
        dead_modules = analyze_dead_modules(graph, resolved_entry_points)

    return GraphMetrics(
        centrality=centrality,
        isolates=isolates,
        cycles=cycles,
        hub_modules=hub_modules,
        dead_modules=dead_modules,
    )
