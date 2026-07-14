from pathlib import Path
from backend.app.models.graph_models import Graph, GraphEdge, GraphNode

def _node(module_path: str, fan_in: int = 0, fan_out: int = 0) -> GraphNode:
    return GraphNode(
        module_path=module_path,
        path=Path(f"{module_path.replace('.', '/')}.py"),
        fan_in=fan_in,
        fan_out=fan_out,
    )


def _edge(source: str, target: str, import_count: int = 1) -> GraphEdge:
    return GraphEdge(
        source=source,
        target=target,
        import_count=import_count,
        raw_imports=(f"from {target} import x",) * import_count,
    )


def _graph(
    module_paths: tuple[str, ...],
    edges: tuple[tuple[str, str], ...] = (),
) -> Graph:
    fan_in = {path: 0 for path in module_paths}
    fan_out = {path: 0 for path in module_paths}
    for source, target in edges:
        fan_out[source] += 1
        fan_in[target] += 1

    return Graph(
        repo_root=Path("test_repo"),
        nodes=tuple(_node(path, fan_in[path], fan_out[path]) for path in module_paths),
        edges=tuple(_edge(source, target) for source, target in edges),
        unresolved_imports=(),
        errors=(),
    )