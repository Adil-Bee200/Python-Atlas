from backend.app.config.models import ArchitectureLayer
from backend.app.metrics.architecture_metrics import analyze_graph_architecture
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
    layers: tuple[ArchitectureLayer, ...] = (),
) -> GraphMetrics:
    # Hub modules depend on centrality, so centrality runs first.
    centrality = analyze_centrality(graph)
    isolates = analyze_isolates(graph)
    cycles = analyze_cycles(graph)
    hub_modules = analyze_hub_modules(graph, centrality)

    dead_modules = None
    missing_entry_points: tuple[str, ...] = ()

    if entry_points:
        resolution = resolve_entry_points(graph, entry_points)
        missing_entry_points = resolution.missing
        # All-or-nothing: any missing entry point skips dead-module analysis.
        if not missing_entry_points:
            dead_modules = analyze_dead_modules(graph, resolution.resolved)

    architecture = (
        analyze_graph_architecture(graph, layers) if layers else None
    )

    return GraphMetrics(
        centrality=centrality,
        isolates=isolates,
        cycles=cycles,
        hub_modules=hub_modules,
        dead_modules=dead_modules,
        architecture=architecture,
        missing_entry_points=missing_entry_points,
    )
