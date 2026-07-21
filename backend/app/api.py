from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.analysis.analyzer import analyze_repo
from backend.app.config.loader import load_config
from backend.app.export.graph_json import graph_to_dict


class AnalyzeRequest(BaseModel):
    repo_path: str = Field(min_length=1)
    config_path: str | None = None


app = FastAPI(title="Code Atlas API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest) -> dict:
    """Analyze a local repository and return the stable graph JSON contract."""
    try:
        config_path = _resolve_config_path(request)
        config = load_config(config_path)
        graph = analyze_repo(request.repo_path, config=config)
        return graph_to_dict(graph)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


def _resolve_config_path(request: AnalyzeRequest) -> Path | None:
    if request.config_path is not None:
        config_path = Path(request.config_path).expanduser().resolve()
        if not config_path.is_file():
            raise ValueError(f"Invalid configuration path: {config_path}")
        return config_path

    repo_config = Path(request.repo_path).expanduser().resolve() / "codeatlas.yaml"
    return repo_config if repo_config.is_file() else None


def run() -> None:
    """Run the local development API via the ``atlas-api`` console script."""
    import uvicorn

    uvicorn.run("backend.app.api:app", host="127.0.0.1", port=8000, reload=True)
