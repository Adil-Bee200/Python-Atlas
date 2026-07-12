from backend.app.models.graph_models import Graph, GraphMetrics
import networkx as nx

def initialize_networkx_graph(graph: Graph) -> nx.Graph:
    G = nx.DiGraph()
    for node in graph.nodes:
        G.add_node(node.module_path)
    for edge in graph.edges:
        G.add_edge(edge.source, edge.target)
    return G

def analyze_centrality(graph: Graph) -> GraphMetrics:
    G = initialize_networkx_graph(graph)

    pagerank_centrality = nx.pagerank(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    in_degree_centrality = nx.in_degree_centrality(G)
    out_degree_centrality = nx.out_degree_centrality(G)

    pagerank_centrality_dict = {}
    betweenness_centrality_dict = {}
    in_degree_centrality_dict = {}
    out_degree_centrality_dict = {}

    for node in graph.nodes:
        pagerank_centrality_dict[node.module_path] = pagerank_centrality[node.module_path]
        betweenness_centrality_dict[node.module_path] = betweenness_centrality[node.module_path]
        in_degree_centrality_dict[node.module_path] = in_degree_centrality[node.module_path]
        out_degree_centrality_dict[node.module_path] = out_degree_centrality[node.module_path]

    return GraphMetrics(
        pagerank_centrality=pagerank_centrality_dict,
        betweenness_centrality=betweenness_centrality_dict,
        in_degree_centrality=in_degree_centrality_dict,
        out_degree_centrality=out_degree_centrality_dict
    )