from dataclasses import dataclass

@dataclass(frozen=True)
class GraphCentralityMetrics:
    pagerank_centrality: dict[str, float]
    betweenness_centrality: dict[str, float]
    in_degree_centrality: dict[str, float]
    out_degree_centrality: dict[str, float]

@dataclass(frozen=True)
class GraphIsolatesMetrics:
    isolates: tuple[str, ...]

@dataclass(frozen=True)
class GraphCyclesMetrics:
    cycles: tuple[tuple[str, ...], ...]

@dataclass(frozen=True)
class GraphMetrics:
    centrality: GraphCentralityMetrics
    isolates: GraphIsolatesMetrics
    cycles: GraphCyclesMetrics