import ELK, { type ElkNode } from "elkjs/lib/elk.bundled.js";
import type { Edge, Node } from "@xyflow/react";
import type {
  DependencyEdgeData,
  ModuleNodeData,
} from "../types/architecture";

/** ELK directions. RIGHT is the V1 default (entry → service → repository). */
export type LayoutDirection = "RIGHT" | "DOWN";

const NODE_HEIGHT = 72;
const NODE_WIDTH_MIN = 168;
const NODE_WIDTH_MAX = 360;
const CHAR_WIDTH_PX = 7.2;
const NODE_PADDING_X = 40;

const elk = new ELK();

function estimateNodeWidth(module: string): number {
  return Math.min(
    NODE_WIDTH_MAX,
    Math.max(NODE_WIDTH_MIN, Math.round(module.length * CHAR_WIDTH_PX + NODE_PADDING_X)),
  );
}

/**
 * Position React Flow nodes with ELK's layered algorithm.
 *
 * Keeps adapter output untouched: adapters translate data; this module owns
 * geometry. Edge routing paths are left to React Flow for now.
 */
export async function layoutGraph(
  nodes: Node<ModuleNodeData>[],
  edges: Edge<DependencyEdgeData>[],
  direction: LayoutDirection = "RIGHT",
): Promise<{
  nodes: Node<ModuleNodeData>[];
  edges: Edge<DependencyEdgeData>[];
}> {
  if (nodes.length === 0) {
    return { nodes, edges };
  }

  const widths = new Map(
    nodes.map((node) => [node.id, estimateNodeWidth(node.data.module)]),
  );

  const elkGraph: ElkNode = {
    id: "root",
    layoutOptions: {
      "elk.algorithm": "layered",
      "elk.direction": direction,
      "elk.edgeRouting": "ORTHOGONAL",
      "elk.spacing.nodeNode": "48",
      "elk.layered.spacing.nodeNodeBetweenLayers": "96",
      "elk.layered.nodePlacement.strategy": "NETWORK_SIMPLEX",
      "elk.layered.crossingMinimization.strategy": "LAYER_SWEEP",
    },
    children: nodes.map((node) => ({
      id: node.id,
      width: widths.get(node.id),
      height: NODE_HEIGHT,
    })),
    edges: edges.map((edge) => ({
      id: edge.id,
      sources: [edge.source],
      targets: [edge.target],
    })),
  };

  const layouted = await elk.layout(elkGraph);
  const positions = new Map(
    (layouted.children ?? []).map((child) => [
      child.id,
      { x: child.x ?? 0, y: child.y ?? 0 },
    ]),
  );

  return {
    nodes: nodes.map((node) => ({
      ...node,
      position: positions.get(node.id) ?? node.position,
      // Keep measured ELK size so labels and layout stay aligned.
      style: { ...node.style, width: widths.get(node.id), height: NODE_HEIGHT },
    })),
    edges,
  };
}
