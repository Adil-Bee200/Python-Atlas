from pathlib import Path

from backend.app.config.models import Configuration
from backend.app.models.graph_metrics_models import ArchitectureDifference
from git import Repo

def resolve_commit(repo: Repo, revision: str) -> Commit:
    # Checks if the revision is a commit and returns the commit object
    try:
        return repo.commit(revision)
    except BadName as e:
        raise ValueError(f"Revision '{revision}' is not a valid commit: {e}")
    

def resolve_git_repo(path: Path) -> Path:
    # Checks if the path is a git repository and returns the root directory
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
    target_revision: str = None,) -> ArchitectureDifference:

    repo = Repo(resolve_git_repo(repo_root))

    if not target_revision: # default to working tree
        target = WorkingTreeTarget(repo)
    else:
        target = resolve_commit(repo, target_revision)
    
    base = resolve_commit(repo, base_revision)

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
