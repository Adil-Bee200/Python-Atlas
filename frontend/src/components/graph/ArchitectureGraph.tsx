import { useEffect, useState } from "react";
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  type ReactFlowInstance,
  useEdgesState,
  useNodesState,
} from "@xyflow/react";
import { ModuleNode } from "./ModuleNode";
import type {
  DependencyFlowEdge,
  ModuleFlowNode,
} from "../../types/architecture";

const nodeTypes = { module: ModuleNode };

const defaultEdgeOptions = {
  style: { stroke: "#6e6e6e", strokeWidth: 1.5 },
};

/**
 * Main dependency graph canvas. Pan, zoom, node dragging, selection,
 * minimap and fit view. Data is hardcoded for step 1.
 */
interface ArchitectureGraphProps {
  initialNodes: ModuleFlowNode[];
  initialEdges: DependencyFlowEdge[];
}

export function ArchitectureGraph({
  initialNodes,
  initialEdges,
}: ArchitectureGraphProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [instance, setInstance] =
    useState<ReactFlowInstance<ModuleFlowNode, DependencyFlowEdge> | null>(null);

  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);

    if (initialNodes.length > 0) {
      requestAnimationFrame(() => {
        void instance?.fitView({ padding: 0.2 });
      });
    }
  }, [initialEdges, initialNodes, instance, setEdges, setNodes]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      nodeTypes={nodeTypes}
      defaultEdgeOptions={defaultEdgeOptions}
      nodesConnectable={false}
      edgesReconnectable={false}
      onInit={setInstance}
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
