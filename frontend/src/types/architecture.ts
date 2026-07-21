import type { Edge, Node } from "@xyflow/react";

/** JSON contract currently emitted by backend.app.export.graph_json. */
export interface ArchitectureGraph {
  repo_root: string;
  nodes: ArchitectureNode[];
  edges: ArchitectureEdge[];
  unresolved_imports: string[];
  errors: string[];
  metrics: ArchitectureMetrics | null;
}

export interface ArchitectureNode {
  module_path: string;
  path: string;
  fan_in: number;
  fan_out: number;
}

export interface ArchitectureEdge {
  source: string;
  target: string;
  import_count: number;
  raw_imports: string[];
}

export interface ArchitectureMetrics {
  centrality: {
    pagerank_centrality: Record<string, number>;
    betweenness_centrality: Record<string, number>;
    in_degree_centrality: Record<string, number>;
    out_degree_centrality: Record<string, number>;
  };
  isolates: { isolates: string[] };
  cycles: { cycles: string[][] };
  hub_modules: {
    hub_modules: Array<{
      module: string;
      in_degree: number;
      out_degree: number;
      pagerank: number;
      hub_score: number;
    }>;
    in_degree_threshold: number;
    max_out_degree: number;
  };
  dead_modules: {
    dead_modules: Array<{ module: string; reason: string }>;
    dead_modules_percentage: number;
  } | null;
  architecture: {
    assignments: Array<{
      module: string;
      layer: {
        name: string;
        module_patterns: string[];
        allowed_dependencies: string[];
      };
    }>;
    violations: Array<{
      source_module: string;
      target_module: string;
      source_layer: string;
      target_layer: string;
    }>;
    unclassified_modules: string[];
    empty_layers: string[];
    ambiguous_assignments: Array<{
      module: string;
      matching_layers: string[];
    }>;
    warnings: string[];
  } | null;
  missing_entry_points: string[];
}

export type ModuleStatus =
  | "hub"
  | "dead"
  | "isolated"
  | "cycle"
  | "layer-violation";

/** Data carried by a module node on the canvas and future inspector. */
export interface ModuleNodeData extends Record<string, unknown> {
  module: string;
  filePath: string;
  layer?: string;
  metrics: {
    inDegree: number;
    outDegree: number;
    pageRank: number;
    betweenness: number;
  };
  statuses: ModuleStatus[];
  /** One compact status shown on the node; full detail belongs in inspector. */
  status?: string;
}

export type ModuleFlowNode = Node<ModuleNodeData, "module">;

export type DependencyStatus = "cycle" | "layer-violation";

export interface DependencyEdgeData extends Record<string, unknown> {
  rawImports: string[];
  importCount: number;
  statuses: DependencyStatus[];
}

/** source imports target; the arrow always points at the imported module. */
export type DependencyFlowEdge = Edge<DependencyEdgeData>;
