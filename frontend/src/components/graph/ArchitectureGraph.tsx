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
  style: { stroke: "#6e6e6e", strokeWidth: 1.5 },
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
      colorMode="dark"
      fitView
      fitViewOptions={{ padding: 0.2 }}
      minZoom={0.2}
      maxZoom={2}
      proOptions={{ hideAttribution: true }}
      className="bg-atlas-bg"
    >
      <Background gap={24} size={1.5} color="#333333" />
      <Controls position="bottom-left" />
      <MiniMap
        position="bottom-right"
        pannable
        zoomable
        nodeColor="#3c3c3c"
        nodeStrokeColor="#505050"
        maskColor="rgba(30, 30, 30, 0.75)"
        bgColor="#252526"
      />
    </ReactFlow>
  );
}
