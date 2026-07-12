import networkx as nx
from backend.app.models.graph_models import Graph

def convert_graph_to_networkx_graph(graph: Graph) -> nx.Graph:
    G = nx.DiGraph()
    for node in graph.nodes:
        G.add_node(node.module_path) 
    for edge in graph.edges:
        G.add_edge(edge.source, edge.target) 
    return G