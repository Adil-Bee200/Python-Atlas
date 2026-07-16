from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from backend.app.models.graph_models import Graph
from backend.app.scanner.repo_scanner import convert_to_module_path


@dataclass(frozen=True)
class EntryPointsResolution:
    resolved: tuple[str, ...]
    missing: tuple[str, ...]


def _resolve_one(
    entry: str,
    modules: set[str],
    path_to_module: dict[str, str],
) -> str | None:
    if entry in modules:
        return entry

    normalized = entry.replace("\\", "/").lstrip("./")
    if normalized in path_to_module:
        return path_to_module[normalized]

    as_module = convert_to_module_path(Path(normalized))
    if as_module in modules:
        return as_module

    return None


def resolve_entry_points(
    graph: Graph,
    entry_points: tuple[str, ...],
) -> EntryPointsResolution:
    """Resolve configured entry points to graph module paths.

    Every configured entry must map to a node in ``graph.nodes``. Entries that
    cannot be resolved are returned in ``missing`` (original configured strings).
    """
    modules = {node.module_path for node in graph.nodes}
    path_to_module = {
        node.path.as_posix(): node.module_path for node in graph.nodes
    }

    resolved: list[str] = []
    missing: list[str] = []

    for entry in entry_points:
        mapped = _resolve_one(entry, modules, path_to_module)
        if mapped is None:
            missing.append(entry)
        else:
            resolved.append(mapped)

    return EntryPointsResolution(
        resolved=tuple(dict.fromkeys(resolved)),
        missing=tuple(missing),
    )
