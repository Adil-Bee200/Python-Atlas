from pathlib import Path

from backend.app.models.graph_models import Graph, GraphNode, GraphEdge
from backend.app.models.import_models import ParsedResult

def build_graph(parsed_result: ParsedResult) -> Graph:
    # 1. Create a lookup table for the modules
    module_lookup = {
        module.module_path : Path(module.path)
        for module in parsed_result.modules if module.error is None
    }

    # 2. Create a set of all of edges (imports) + unresolved imports
    edges = set[tuple[str, str, str]]()
    unresolved_imports = set[str]()
    errors = set[str]()

    for module in parsed_result.modules:
        if module.error is not None:
            errors.add(module.module_path)
            continue
        for import_entry in module.imports:
            if import_entry.module_name not in module_lookup:
                unresolved_imports.add(import_entry.raw_import) # just store the raw import string for now
            else:
                edges.add((module.module_path, import_entry.module_name, import_entry.raw_import))
    
    # 3. Compute fan_in and fan_out from unique local module dependencies
    fan_in = {}
    fan_out = {}

    unique_deps = {(source, target) for source, target, _raw_import in edges}
    for source, target in unique_deps:
        fan_in[target] = fan_in.get(target, 0) + 1
        fan_out[source] = fan_out.get(source, 0) + 1
    
    # 4. Create nodes
    GraphNodes = tuple(
        GraphNode(module_path, module_lookup[module_path], fan_in.get(module_path, 0), fan_out.get(module_path, 0))
        for module_path in module_lookup
    )

    # 5. Create edges
    GraphEdges = tuple(
        GraphEdge(source, target, raw_import)
        for source, target, raw_import in edges
    )

    # 6. Create graph
    graph = Graph(parsed_result.repo_root, GraphNodes, GraphEdges, tuple(unresolved_imports), tuple(errors))

    return graph
    """ 
    Notes:
    - We create a lookup of all parsed local modules without errors
    - Build edge set of all imports across all parsed modules (dedupes identical import statements)
    - Only add edges to edge set if the target module exists in the lookup (resolved imports)
    - Add unresolved imports to set of unresolved imports
    - Compute fan_in and fan_out from unique (source, target) local module pairs
    - Create a GraphNode object for each module
    - Create a GraphEdge object for each edge
    - Create a Graph object with the nodes and edges
    """
