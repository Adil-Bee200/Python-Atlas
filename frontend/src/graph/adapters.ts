import { MarkerType, type Edge, type Node } from "@xyflow/react";
import type {
  ArchitectureGraph,
  DependencyEdgeData,
  DependencyStatus,
  ModuleNodeData,
  ModuleStatus,
} from "../types/architecture";

const EMPTY_POSITION = { x: 0, y: 0 };

function cycleEdges(cycles: string[][]): Set<string> {
  const edges = new Set<string>();

  for (const cycle of cycles) {
    if (cycle.length < 2) continue;

    for (let index = 0; index < cycle.length; index += 1) {
      const source = cycle[index];
      const target = cycle[(index + 1) % cycle.length];
      edges.add(`${source}\0${target}`);
    }
  }

  return edges;
}

function nodeStatusLabel(
  statuses: ModuleStatus[],
  fanIn: number,
): string | undefined {
  // Keep one stable, high-signal status on the compact node.
  if (statuses.includes("layer-violation")) return "Layer violation";
  if (statuses.includes("cycle")) return "Cycle member";
  if (statuses.includes("dead")) return "Dead module";
  if (statuses.includes("hub")) return `Hub · ${fanIn} dependents`;
  if (statuses.includes("isolated")) return "Isolated";
  return undefined;
}

/**
 * Convert the backend graph JSON into React Flow's rendering model.
 *
 * Positions intentionally start at the origin. The ELK adapter added in the
 * layout step owns positioning; this adapter only translates data and state.
 */
export function toReactFlowGraph(
  graph: ArchitectureGraph,
): {
  nodes: Node<ModuleNodeData>[];
  edges: Edge<DependencyEdgeData>[];
} {
  const metrics = graph.metrics;
  const layers = new Map(
    metrics?.architecture?.assignments.map(({ module, layer }) => [
      module,
      layer.name,
    ]) ?? [],
  );
  const hubs = new Set(
    metrics?.hub_modules.hub_modules.map(({ module }) => module) ?? [],
  );
  const dead = new Set(
    metrics?.dead_modules?.dead_modules.map(({ module }) => module) ?? [],
  );
  const isolates = new Set(metrics?.isolates.isolates ?? []);
  const cycleMembers = new Set(metrics?.cycles.cycles.flat() ?? []);
  const violatingModules = new Set(
    metrics?.architecture?.violations.flatMap(
      ({ source_module, target_module }) => [source_module, target_module],
    ) ?? [],
  );
  const violatingEdges = new Set(
    metrics?.architecture?.violations.map(
      ({ source_module, target_module }) =>
        `${source_module}\0${target_module}`,
    ) ?? [],
  );
  const edgesInCycles = cycleEdges(metrics?.cycles.cycles ?? []);

  const nodes: Node<ModuleNodeData>[] = graph.nodes.map((node) => {
    const statuses: ModuleStatus[] = [];
    if (hubs.has(node.module_path)) statuses.push("hub");
    if (dead.has(node.module_path)) statuses.push("dead");
    if (isolates.has(node.module_path)) statuses.push("isolated");
    if (cycleMembers.has(node.module_path)) statuses.push("cycle");
    if (violatingModules.has(node.module_path)) statuses.push("layer-violation");

    return {
      id: node.module_path,
      type: "module",
      position: EMPTY_POSITION,
      data: {
        module: node.module_path,
        filePath: node.path,
        layer: layers.get(node.module_path),
        metrics: {
          inDegree: node.fan_in,
          outDegree: node.fan_out,
          pageRank:
            metrics?.centrality.pagerank_centrality[node.module_path] ?? 0,
          betweenness:
            metrics?.centrality.betweenness_centrality[node.module_path] ?? 0,
        },
        statuses,
        status: nodeStatusLabel(statuses, node.fan_in),
      },
    };
  });

  const edges: Edge<DependencyEdgeData>[] = graph.edges.map((edge) => {
    const key = `${edge.source}\0${edge.target}`;
    const statuses: DependencyStatus[] = [];
    if (edgesInCycles.has(key)) statuses.push("cycle");
    if (violatingEdges.has(key)) statuses.push("layer-violation");

    return {
      id: `${edge.source}->${edge.target}`,
      source: edge.source,
      target: edge.target,
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 16,
        height: 16,
        color: "#6e6e6e",
      },
      data: {
        rawImports: edge.raw_imports,
        importCount: edge.import_count,
        statuses,
      },
    };
  });

  return { nodes, edges };
}
