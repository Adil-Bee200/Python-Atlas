import type { Edge, Node } from "@xyflow/react";

/** Data carried by a module node on the canvas. */
export interface ModuleNodeData extends Record<string, unknown> {
  /** Full module path, e.g. "app.services.payment". */
  module: string;
  /** Configured architecture layer, when known. */
  layer?: string;
  /** Single most important status line, e.g. "Hub · 14 dependents". */
  status?: string;
}

export type ModuleFlowNode = Node<ModuleNodeData, "module">;

/**
 * A directed dependency edge. Semantics are always:
 * source imports target (arrow points at the imported module).
 */
export type DependencyFlowEdge = Edge;
