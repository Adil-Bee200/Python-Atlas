from backend.app.models.graph_models import Graph
from backend.app.models.graph_metrics_models import GraphMetrics
from backend.app.metrics.centrality import analyze_centrality
from backend.app.metrics.isolates import analyze_isolates
from backend.app.metrics.cycles import analyze_cycles

def analyze_metrics(graph: Graph) -> GraphMetrics:
    return GraphMetrics(
        centrality=analyze_centrality(graph),
        isolates=analyze_isolates(graph),
        cycles=analyze_cycles(graph),
    )