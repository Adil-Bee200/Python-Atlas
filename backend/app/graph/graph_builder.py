from pathlib import Path

from backend.app.models.graph_models import Graph, GraphNode, GraphEdge
from backend.app.models.import_models import ParsedResult


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


def build_graph(parsed_result: ParsedResult) -> Graph:
    # 1. Create a lookup table for the modules
    module_lookup = {
        module.module_path : Path(module.path)
        for module in parsed_result.modules if module.error is None
    }

    # 2. Group resolved imports by (source, target) and collect unique raw imports
    edge_imports: dict[tuple[str, str], set[str]] = {}
    unresolved_imports = set[str]()
    errors = set[str]()

    for module in parsed_result.modules:
        if module.error is not None:
            errors.add(module.module_path)
            continue
        for import_entry in module.imports:
            resolved = _resolve_local_module(import_entry.module_name, module_lookup)
            if resolved is None:
                unresolved_imports.add(import_entry.raw_import)
            else:
                edge_key = (module.module_path, resolved)
                edge_imports.setdefault(edge_key, set()).add(import_entry.raw_import)

    # 3. Compute fan_in and fan_out from unique local module dependencies
    fan_in = {}
    fan_out = {}

    for source, target in edge_imports:
        fan_in[target] = fan_in.get(target, 0) + 1
        fan_out[source] = fan_out.get(source, 0) + 1

    # 4. Create nodes
    GraphNodes = tuple(
        GraphNode(module_path, module_lookup[module_path], fan_in.get(module_path, 0), fan_out.get(module_path, 0))
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
    graph = Graph(parsed_result.repo_root, GraphNodes, GraphEdges, tuple(unresolved_imports), tuple(errors))

    return graph
