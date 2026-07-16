from backend.app.models.graph_models import Graph
from backend.app.models.graph_metrics_models import GraphDeadModulesMetrics, GraphDeadModules
import networkx as nx
from backend.app.metrics.utils import convert_graph_to_networkx_graph

def analyze_dead_modules(graph: Graph, entry_points: tuple[str, ...]) -> GraphDeadModulesMetrics:
    # REQUIRES: entry_points is not empty
    G = convert_graph_to_networkx_graph(graph)
    unreached_modules = set(G.nodes)
    unreached_modules -= set(entry_points) ## Remove entry points from unreached modules

    for entry_point in entry_points:
        reachable_modules = nx.descendants(G, entry_point)
        unreached_modules -= reachable_modules

    dead_modules = tuple(GraphDeadModules(module, "Unreached by entry points") for module in unreached_modules)
    return GraphDeadModulesMetrics(
        dead_modules=dead_modules,
        dead_modules_percentage=len(dead_modules) / len(G.nodes),
    )
