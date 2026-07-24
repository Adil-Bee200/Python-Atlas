import type { ArchitectureGraph } from "../types/architecture";

export interface AnalyzeRequest {
  repo_path: string;
  config_path?: string;
}

export class ApiError extends Error {
  readonly status: number;

  constructor(
    message: string,
    status: number,
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function analyzeRepository(
  request: AnalyzeRequest,
  signal?: AbortSignal,
): Promise<ArchitectureGraph> {
  const response = await fetch("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal,
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as {
      detail?: string;
    } | null;
    throw new ApiError(
      payload?.detail ?? `Analysis failed with status ${response.status}`,
      response.status,
    );
  }

  return (await response.json()) as ArchitectureGraph;
}
