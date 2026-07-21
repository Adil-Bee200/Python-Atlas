import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { ModuleFlowNode } from "../../types/architecture";

/**
 * Compact module card: module name, optional layer badge, and a single
 * status line. Detailed metrics belong in the inspector, not the node.
 */
export function ModuleNode({ data, selected }: NodeProps<ModuleFlowNode>) {
  return (
    <div
      className={`rounded-md border bg-atlas-node px-3 py-2 shadow-sm transition-colors ${
        selected
          ? "border-atlas-accent"
          : "border-atlas-border hover:border-atlas-muted"
      }`}
    >
      {/* Edges flow left to right: dependents enter on the left,
          imports leave from the right. */}
      <Handle type="target" position={Position.Left} className="!bg-atlas-border" />

      <div className="font-mono text-xs font-semibold text-atlas-text">
        {data.module}
      </div>

      {data.layer && (
        <div className="mt-1">
          <span className="rounded bg-atlas-panel px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-atlas-muted">
            {data.layer}
          </span>
        </div>
      )}

      {data.status && (
        <div className="mt-1 text-[11px] text-atlas-warn">{data.status}</div>
      )}

      <Handle type="source" position={Position.Right} className="!bg-atlas-border" />
    </div>
  );
}
