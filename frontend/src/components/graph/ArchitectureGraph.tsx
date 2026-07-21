import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  useEdgesState,
  useNodesState,
} from "@xyflow/react";
import { ModuleNode } from "./ModuleNode";
import { sampleEdges, sampleNodes } from "../../graph/sampleData";

const nodeTypes = { module: ModuleNode };

const defaultEdgeOptions = {
  style: { stroke: "#94a3b8", strokeWidth: 1.5 },
};

/**
 * Main dependency graph canvas. Pan, zoom, node dragging, selection,
 * minimap and fit view. Data is hardcoded for step 1.
 */
export function ArchitectureGraph() {
  const [nodes, , onNodesChange] = useNodesState(sampleNodes);
  const [edges, , onEdgesChange] = useEdgesState(sampleEdges);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      nodeTypes={nodeTypes}
      defaultEdgeOptions={defaultEdgeOptions}
      fitView
      fitViewOptions={{ padding: 0.2 }}
      minZoom={0.2}
      maxZoom={2}
      proOptions={{ hideAttribution: true }}
    >
      <Background gap={24} size={1.5} color="#e2e8f0" />
      <Controls position="bottom-left" />
      <MiniMap
        position="bottom-right"
        pannable
        zoomable
        nodeColor="#cbd5e1"
        maskColor="rgba(241, 245, 249, 0.7)"
      />
    </ReactFlow>
  );
}
