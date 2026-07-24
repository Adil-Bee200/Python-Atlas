import { useState, type FormEvent } from "react";
import { ArchitectureGraph } from "../components/graph/ArchitectureGraph";
import { useArchitectureGraph } from "../hooks/useArchitectureGraph";

/**
 * Application shell. For step 1 this is only the graph canvas with a
 * minimal top bar; sidebar and inspector arrive in later steps.
 */
export function RepositoryAnalysisPage() {
  const [repoPath, setRepoPath] = useState(".");
  const { nodes, edges, loading, error, analyze } = useArchitectureGraph();

  const submitAnalysis = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const path = repoPath.trim();
    if (path) void analyze(path);
  };

  return (
    <div className="flex h-full flex-col bg-atlas-bg">
      <header className="flex h-14 shrink-0 items-center gap-4 border-b border-atlas-panel bg-atlas-sidebar px-4">
        <h1 className="text-sm font-semibold text-atlas-text">Code Atlas</h1>
        <form className="flex min-w-0 flex-1 items-center gap-2" onSubmit={submitAnalysis}>
          <label className="sr-only" htmlFor="repo-path">
            Repository path
          </label>
          <input
            id="repo-path"
            value={repoPath}
            onChange={(event) => setRepoPath(event.target.value)}
            placeholder="/path/to/repository"
            className="h-8 min-w-0 max-w-xl flex-1 rounded border border-atlas-border bg-atlas-panel px-2.5 font-mono text-xs text-atlas-text outline-none placeholder:text-atlas-muted focus:border-atlas-accent"
          />
          <button
            type="submit"
            disabled={loading || !repoPath.trim()}
            className="h-8 rounded bg-atlas-accent px-3 text-xs font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Analyzing…" : "Analyze"}
          </button>
        </form>
        {nodes.length > 0 && (
          <span className="shrink-0 text-xs text-atlas-muted">
            {nodes.length} modules · {edges.length} dependencies
          </span>
        )}
      </header>
      <main className="relative min-h-0 flex-1">
        <ArchitectureGraph initialNodes={nodes} initialEdges={edges} />
        {!loading && nodes.length === 0 && !error && (
          <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
            <p className="text-sm text-atlas-muted">
              Enter a local repository path and run analysis.
            </p>
          </div>
        )}
        {loading && (
          <div className="absolute inset-x-0 top-4 flex justify-center">
            <div className="rounded border border-atlas-border bg-atlas-panel px-3 py-2 text-xs text-atlas-text">
              Analyzing repository…
            </div>
          </div>
        )}
        {error && (
          <div className="absolute inset-x-0 top-4 flex justify-center px-4">
            <div className="max-w-2xl rounded border border-red-800 bg-atlas-panel px-3 py-2 text-xs text-red-300">
              {error}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
