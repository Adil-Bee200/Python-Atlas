from pathlib import Path

from backend.app.config.models import Configuration
from backend.app.models.graph_metrics_models import ArchitectureDifference

def resolve_git_repo(path: Path) -> Path:
    current_path = path.resolve()
    
    if current_path.is_file():
        current_path = current_path.parent

    if not current_path.exists():
        raise ValueError(f"Path '{path}' does not exist.")
    
    while not (current_path / ".git").exists():
        if current_path.parent == current_path:
            raise ValueError(f"'{path}' is not inside a Git repository.")
        current_path = current_path.parent
    
    return current_path


def analyze_repo_diff(
    repo_root: Path, 
    config: Configuration,
    base_revision: str = "HEAD~1",
    target_revision: str | None = None,) -> ArchitectureDifference:



    """ 
    Steps:
    0. Resolve the repo root, is it a git repository?
    1. Resolve the base and target revisions
    2. Materialize both revisions
    3. Get the graph for each revision
    4. Compare the graph and metrics 
    5. Return the difference
    """

    # TODO: Implement this
    pass
