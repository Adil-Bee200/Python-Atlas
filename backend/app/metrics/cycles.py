import networkx as nx
from backend.app.models.graph_models import Graph
from backend.app.models.graph_metrics_models import GraphCyclesMetrics
from backend.app.metrics.utils import convert_graph_to_networkx_graph


def _normalize_cycle(cycle: list[str]) -> tuple[str, ...]:
    if not cycle:
        return ()
    start = cycle.index(min(cycle))
    return tuple(cycle[start:] + cycle[:start])


def analyze_cycles(graph: Graph) -> GraphCyclesMetrics:
    G = convert_graph_to_networkx_graph(graph)
    cycles = sorted(_normalize_cycle(cycle) for cycle in nx.simple_cycles(G))
    return GraphCyclesMetrics(cycles=tuple(cycles))
