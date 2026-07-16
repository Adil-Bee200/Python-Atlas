from pathlib import Path

from backend.app.models.graph_models import Graph
from backend.app.scanner.repo_scanner import convert_to_module_path


def resolve_entry_points(
    graph: Graph,
    entry_points: tuple[str, ...],
) -> tuple[str, ...]:
    """Map configured entry points (module paths or file paths) to graph module paths."""
    modules = {node.module_path for node in graph.nodes}
    path_to_module = {
        node.path.as_posix(): node.module_path for node in graph.nodes
    }

    resolved: list[str] = []
    for entry in entry_points:
        if entry in modules:
            resolved.append(entry)
            continue

        normalized = entry.replace("\\", "/").lstrip("./")
        if normalized in path_to_module:
            resolved.append(path_to_module[normalized])
            continue

        as_module = convert_to_module_path(Path(normalized))
        if as_module in modules:
            resolved.append(as_module)

    return tuple(dict.fromkeys(resolved))
