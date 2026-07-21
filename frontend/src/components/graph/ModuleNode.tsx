import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { ModuleFlowNode } from "../../types/architecture";

/**
 * Compact module card: module name, optional layer badge, and a single
 * status line. Detailed metrics belong in the inspector, not the node.
 */
export function ModuleNode({ data, selected }: NodeProps<ModuleFlowNode>) {
  return (
    <div
      className={`rounded-md border bg-white px-3 py-2 shadow-sm transition-colors ${
        selected
          ? "border-blue-500 ring-2 ring-blue-200"
          : "border-slate-300 hover:border-slate-400"
      }`}
    >
      {/* Edges flow left to right: dependents enter on the left,
          imports leave from the right. */}
      <Handle type="target" position={Position.Left} className="!bg-slate-400" />

      <div className="font-mono text-xs font-semibold text-slate-800">
        {data.module}
      </div>

      {data.layer && (
        <div className="mt-1">
          <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-slate-500">
            {data.layer}
          </span>
        </div>
      )}

      {data.status && (
        <div className="mt-1 text-[11px] text-amber-700">{data.status}</div>
      )}

      <Handle type="source" position={Position.Right} className="!bg-slate-400" />
    </div>
  );
}
