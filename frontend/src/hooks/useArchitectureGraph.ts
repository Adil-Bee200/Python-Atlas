import { useCallback, useRef, useState } from "react";
import { analyzeRepository } from "../api/analyze";
import { toReactFlowGraph } from "../graph/adapters";
import type {
  DependencyFlowEdge,
  ModuleFlowNode,
} from "../types/architecture";

interface ArchitectureGraphState {
  nodes: ModuleFlowNode[];
  edges: DependencyFlowEdge[];
  loading: boolean;
  error: string | null;
  analyze: (repoPath: string, configPath?: string) => Promise<void>;
}

export function useArchitectureGraph(): ArchitectureGraphState {
  const [nodes, setNodes] = useState<ModuleFlowNode[]>([]);
  const [edges, setEdges] = useState<DependencyFlowEdge[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const activeRequest = useRef<AbortController | null>(null);

  const analyze = useCallback(
    async (repoPath: string, configPath?: string) => {
      activeRequest.current?.abort();
      const controller = new AbortController();
      activeRequest.current = controller;
      setLoading(true);
      setError(null);

      try {
        const graph = await analyzeRepository(
          {
            repo_path: repoPath,
            ...(configPath ? { config_path: configPath } : {}),
          },
          controller.signal,
        );
        const flowGraph = toReactFlowGraph(graph);
        setNodes(flowGraph.nodes as ModuleFlowNode[]);
        setEdges(flowGraph.edges);
      } catch (requestError) {
        if (controller.signal.aborted) return;
        setError(
          requestError instanceof Error
            ? requestError.message
            : "Unable to analyze repository",
        );
      } finally {
        if (activeRequest.current === controller) {
          activeRequest.current = null;
          setLoading(false);
        }
      }
    },
    [],
  );

  return { nodes, edges, loading, error, analyze };
}
