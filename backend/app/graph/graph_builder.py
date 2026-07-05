from backend.app.models.graph_models import Graph, GraphNode, GraphEdge
from backend.app.models.import_models import ParsedResult

def build_graph(parsed_result: ParsedResult) -> Graph:
    # 1. Create a lookup table for the modules
    module_lookup = {
        module.module_path : module
        for module in parsed_result.modules if module.error is None
    }

    # 2. Create a set of all of edges (imports)
    edges = set()


    """ 
    Notes:
    - We create a lookup of all parsed local modules without errors
    - Build edge set (will deduplicate imports for a given module) of all imports across all parsed modules
    - Only add edges to edge set if the target module exists in the lookup (resolved imports)
    - Add unresolved imports to set of unresolved imports
    - Iterate over edge set and compute fan_in and fan_out for each module
    - Create a GraphNode object for each module
    - Create a GraphEdge object for each edge
    - Create a Graph object with the nodes and edges
    """
