import networkx as nx
from backend.app.models.graph_models import Graph
from backend.app.models.graph_metrics_models import GraphCyclesMetrics
from backend.app.metrics.utils import convert_graph_to_networkx_graph

def analyze_cycles(graph: Graph) -> GraphCyclesMetrics:
    G = convert_graph_to_networkx_graph(graph)
    cycles = list(nx.simple_cycles(G))
    return GraphCyclesMetrics(cycles=tuple(cycles))