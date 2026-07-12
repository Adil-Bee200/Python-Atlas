from backend.app.models.graph_models import Graph
from backend.app.models.graph_metrics_models import GraphIsolatesMetrics
from backend.app.metrics.utils import convert_graph_to_networkx_graph
import networkx as nx

# For now only isolated modules are considered, we can look at weakly connected components in the future
def analyze_isolates(graph: Graph) -> GraphIsolatesMetrics:
    G = convert_graph_to_networkx_graph(graph)
    isolates = list(nx.isolates(G))
    return GraphIsolatesMetrics(isolates=tuple(isolates))