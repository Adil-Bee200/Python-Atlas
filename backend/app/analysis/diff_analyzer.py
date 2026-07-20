from pathlib import Path

from backend.app.config.models import Configuration
from backend.app.models.graph_metrics_models import ArchitectureDifference
from git import Repo
from backend.app.git.worktree import create_worktree
from backend.app.analysis.repo_analyzer import analyze_repo

def compare_graphs(base_graph: Graph, target_graph: Graph) -> ArchitectureDifference:
    added_modules = set(target_graph.nodes) - set(base_graph.nodes)
    removed_modules = set(base_graph.nodes) - set(target_graph.nodes)
    added_dependencies = set(target_graph.edges) - set(base_graph.edges)
    removed_dependencies = set(base_graph.edges) - set(target_graph.edges)

    added_module_dependencies: dict[str, list[GraphEdge]] = {}
    for module in added_modules:
        dependencies = [edge for edge in target_graph.edges if edge.source == module]
        added_module_dependencies[module] = added_module_dependencies.get(module, []).append(dependencies)
    
    removed_module_dependencies: dict[str, list[GraphEdge]] = {}
    for module in removed_modules:
        dependencies = [edge for edge in base_graph.edges if edge.source == module]
        removed_module_dependencies[module] = removed_module_dependencies.get(module, []).append(dependencies)
    
    module_dependencies = {
        module: ModuleDependencyDifference(
            module=module,
            added_dependencies=tuple(added_module_dependencies[module]),
            removed_dependencies=tuple(removed_module_dependencies[module])
        )
        for module in added_modules | removed_modules
    }

    return ArchitectureDifference(
        base_revision=base_graph.revision,
        target_revision=target_graph.revision,
        added_modules=added_modules,
        removed_modules=removed_modules,
        module_dependencies=module_dependencies
    )

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
    target_revision: str | None = None,) -> ArchitectureDifference:

    resolved_repo_root = resolve_git_repo(repo_root)
    repo = Repo(resolved_repo_root)

    base_commit = resolve_commit(repo, base_revision)

    target_commit = (
        resolve_commit(repo, target_revision)
        if target_revision is not None 
        else None
    )

    with create_worktree(repo, base_commit) as base_path:
        base_graph = analyze_repo(base_path, config)
    
    if target_commit is not None:
        working_tree_path = Path(repo.working_tree_dir)
        target_graph = analyze_repo(working_tree_path, config)
    else:
        with create_worktree(repo, target_commit) as target_path:
            target_graph = analyze_repo(target_path, config)

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
