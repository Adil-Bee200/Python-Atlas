'''
Hub modules: heavily depended-on, lightly dependent modules.

Criteria (using existing centrality metrics):
- High in-degree centrality (widely imported)
- Low out-degree centrality (few outbound deps)
- High PageRank (influence through the import graph)
'''

import numpy as np

from backend.app.models.graph_models import Graph
from backend.app.models.graph_metrics_models import (
    GraphCentralityMetrics,
    GraphHubModule,
    GraphHubModulesMetrics,
)

HUB_MODULES_MIN_IN_DEGREE = 3
HUB_MODULES_MAX_OUT_DEGREE = 2
HUB_MODULES_MAX_OUT_DEGREE_FLOOR = 0.05
DEFAULT_IN_DEGREE_PERCENTILE = 90.0


def analyze_hub_modules(
    graph: Graph,
    centrality: GraphCentralityMetrics,
    in_degree_percentile: float = DEFAULT_IN_DEGREE_PERCENTILE,
) -> GraphHubModulesMetrics:
    n = len(graph.nodes)

    if n < 3:
        # Too few modules for meaningful hubs + also avoids division by zero.
        return GraphHubModulesMetrics(
            hub_modules=(),
            in_degree_threshold=0.0,
            max_out_degree=0.0,
        )

    denom = n - 1
    in_degree_threshold = max(
        HUB_MODULES_MIN_IN_DEGREE / denom,
        float(np.percentile(list(centrality.in_degree_centrality.values()), in_degree_percentile)),
    )
    max_out_degree = max(
        HUB_MODULES_MAX_OUT_DEGREE / denom,
        HUB_MODULES_MAX_OUT_DEGREE_FLOOR,
    )

    hubs: list[GraphHubModule] = []
    for node in graph.nodes:
        path = node.module_path
        in_c = centrality.in_degree_centrality[path]
        out_c = centrality.out_degree_centrality[path]
        pagerank = centrality.pagerank_centrality[path]

        if in_c < in_degree_threshold or out_c > max_out_degree:
            continue

        hubs.append(
            GraphHubModule(
                module=path,
                in_degree=node.fan_in,
                out_degree=node.fan_out,
                pagerank=pagerank,
                hub_score=pagerank * in_c / (1.0 + out_c),
            )
        )

    hubs.sort(key=lambda hub: hub.hub_score, reverse=True)
    return GraphHubModulesMetrics(
        hub_modules=tuple(hubs),
        in_degree_threshold=in_degree_threshold,
        max_out_degree=max_out_degree,
    )
