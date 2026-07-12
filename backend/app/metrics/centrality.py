from backend.app.models.graph_models import Graph
from backend.app.models.graph_metrics_models import GraphCentralityMetrics
import networkx as nx
from backend.app.metrics.utils import convert_graph_to_networkx_graph

''' 
Metric choice reasoning:
- Pagerank: Measures influence recursively. A file has high pagerank centrality if it is imported by other highly-imported files. 
It exposes system-critical core modules.
- Betweenness centrality: Identifies modules that connect different regions or subsystems of the dependency graph.
Finds modules that sit on many shortest paths between other modules. These are architectural bridges or bottlenecks.
- In-degree centrality: Measures how broadly a module is depended upon.
- Out-degree centrality: Measures how broadly a module depends on other modules.
'''

def analyze_centrality(graph: Graph) -> GraphCentralityMetrics:
    G = convert_graph_to_networkx_graph(graph)

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

    return GraphCentralityMetrics(
        pagerank_centrality=pagerank_centrality_dict,
        betweenness_centrality=betweenness_centrality_dict,
        in_degree_centrality=in_degree_centrality_dict,
        out_degree_centrality=out_degree_centrality_dict
    )