from dataclasses import dataclass


@dataclass(frozen=True)
class GraphNode:
    module_path: str
    path: Path 
    fan_in: int
    fan_out: int 

@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    raw_import: str

@dataclass(frozen=True)
class Graph:
    repo_root: Path
    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]
    external_imports: tuple[str, ...]