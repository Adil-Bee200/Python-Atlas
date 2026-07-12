from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GraphNode:
    module_path: str
    path: Path 
    fan_in: int # the number of unique local modules that depend on this module
    fan_out: int # the number of unique local modules this module depends on

@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    import_count: int
    raw_imports: tuple[str, ...]

@dataclass(frozen=True)
class Graph:
    repo_root: Path
    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]
    unresolved_imports: tuple[str, ...] # at this stage theres no way to know if its a bad import or a external import
    errors: tuple[str, ...]

@dataclass(frozen=True)
class GraphMetrics:
    in_degree_centrality: dict[str, float]
    out_degree_centrality: dict[str, float]
    betweenness_centrality: dict[str, float]
    pagerank_centrality: dict[str, float]