from pathlib import Path

from backend.app.models.graph_models import Graph, GraphNode, GraphEdge
from backend.app.models.import_models import ParsedImport, ParsedResult


def _resolve_local_module(
    import_name: str,
    module_lookup: dict[str, Path],
) -> str | None:
    if not import_name:
        return None

    if import_name in module_lookup:
        return import_name

    suffix = f".{import_name}"
    matches = [
        module_path
        for module_path in module_lookup
        if module_path.endswith(suffix)
    ]
    if len(matches) == 1:
        return matches[0]
    return None


def _resolution_candidates(import_entry: ParsedImport) -> tuple[str, ...]:
    """Module names to try for a single import statement.

    For ``from pkg import a, b``, tries ``pkg``, ``pkg.a``, and ``pkg.b``.
    Submodule candidates are only kept later if they resolve to a scanned module.
    """
    candidates: list[str] = []
    if import_entry.module_name:
        candidates.append(import_entry.module_name)

    for name in import_entry.imported_names:
        if name == "*":
            continue
        if import_entry.module_name:
            candidates.append(f"{import_entry.module_name}.{name}")

    return tuple(candidates)


def build_graph(parsed_result: ParsedResult) -> Graph:
    # 1. Create a lookup table for the modules
    module_lookup = {
        module.module_path: Path(module.path)
        for module in parsed_result.modules
        if module.error is None
    }

    # 2. Group resolved imports by (source, target) and collect unique raw imports
    edge_imports: dict[tuple[str, str], set[str]] = {}
    unresolved_imports: set[str] = set()
    errors: set[str] = set()

    for module in parsed_result.modules:
        if module.error is not None:
            errors.add(module.module_path)
            continue
        for import_entry in module.imports:
            resolved_targets: list[str] = []
            seen: set[str] = set()
            for candidate in _resolution_candidates(import_entry):
                resolved = _resolve_local_module(candidate, module_lookup)
                if resolved is not None and resolved not in seen:
                    seen.add(resolved)
                    resolved_targets.append(resolved)

            if not resolved_targets:
                unresolved_imports.add(import_entry.raw_import)
                continue

            for target in resolved_targets:
                edge_key = (module.module_path, target)
                edge_imports.setdefault(edge_key, set()).add(import_entry.raw_import)

    # 3. Compute fan_in and fan_out from unique local module dependencies
    fan_in: dict[str, int] = {}
    fan_out: dict[str, int] = {}

    for source, target in edge_imports:
        fan_in[target] = fan_in.get(target, 0) + 1
        fan_out[source] = fan_out.get(source, 0) + 1

    # 4. Create nodes
    GraphNodes = tuple(
        GraphNode(
            module_path,
            module_lookup[module_path],
            fan_in.get(module_path, 0),
            fan_out.get(module_path, 0),
        )
        for module_path in module_lookup
    )

    # 5. Create edges
    GraphEdges = tuple(
        GraphEdge(
            source,
            target,
            len(raw_imports),
            tuple(sorted(raw_imports)),
        )
        for (source, target), raw_imports in edge_imports.items()
    )

    # 6. Create graph
    return Graph(
        parsed_result.repo_root,
        GraphNodes,
        GraphEdges,
        tuple(unresolved_imports),
        tuple(errors),
    )
