import { ArchitectureGraph } from "../components/graph/ArchitectureGraph";

/**
 * Application shell. For step 1 this is only the graph canvas with a
 * minimal top bar; sidebar and inspector arrive in later steps.
 */
export function RepositoryAnalysisPage() {
  return (
    <div className="flex h-full flex-col bg-slate-50">
      <header className="flex h-14 shrink-0 items-center gap-3 border-b border-slate-200 bg-white px-4">
        <h1 className="text-sm font-semibold text-slate-800">Code Atlas</h1>
        <span className="text-xs text-slate-400">
          static sample graph · arrows read “imports”
        </span>
      </header>
      <main className="min-h-0 flex-1">
        <ArchitectureGraph />
      </main>
    </div>
  );
}
