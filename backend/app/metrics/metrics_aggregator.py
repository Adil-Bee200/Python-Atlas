from backend.app.models.graph_models import Graph
from backend.app.models.graph_metrics_models import GraphMetrics
from backend.app.metrics.centrality import analyze_centrality
from backend.app.metrics.isolates import analyze_isolates
from backend.app.metrics.cycles import analyze_cycles
from backend.app.metrics.hub_modules import analyze_hub_modules


def analyze_metrics(graph: Graph) -> GraphMetrics:
    # Hub modules depend on centrality, so centrality runs first.
    centrality = analyze_centrality(graph)
    isolates = analyze_isolates(graph)
    cycles = analyze_cycles(graph)
    hub_modules = analyze_hub_modules(graph, centrality)

    return GraphMetrics(
        centrality=centrality,
        isolates=isolates,
        cycles=cycles,
        hub_modules=hub_modules,
    )
