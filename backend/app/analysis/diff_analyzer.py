from __future__ import annotations

from pathlib import Path

from git import Repo
from git.exc import BadName
from git.objects import Commit

from backend.app.analysis.analyzer import analyze_repo
from backend.app.config.models import Configuration
from backend.app.git.worktree import create_worktree
from backend.app.models.graph_metrics_models import (
    ArchitectureDifference,
    ModuleDependencyDifference,
)
from backend.app.models.graph_models import Graph


def compare_graphs(
    base_graph: Graph,
    target_graph: Graph,
    base_revision: str,
    target_revision: str,
) -> ArchitectureDifference:
    base_modules = {node.module_path for node in base_graph.nodes}
    target_modules = {node.module_path for node in target_graph.nodes}

    added_modules = tuple(sorted(target_modules - base_modules))
    removed_modules = tuple(sorted(base_modules - target_modules))

    base_edge_keys = {(edge.source, edge.target) for edge in base_graph.edges}
    target_edge_keys = {(edge.source, edge.target) for edge in target_graph.edges}

    added_edge_keys = target_edge_keys - base_edge_keys
    removed_edge_keys = base_edge_keys - target_edge_keys

    modules_with_dep_changes = {
        source for source, _ in added_edge_keys
    } | {
        source for source, _ in removed_edge_keys
    }

    module_dependencies: dict[str, ModuleDependencyDifference] = {}
    for module in sorted(modules_with_dep_changes):
        module_dependencies[module] = ModuleDependencyDifference(
            module=module,
            added_dependencies=tuple(
                sorted(target for source, target in added_edge_keys if source == module)
            ),
            removed_dependencies=tuple(
                sorted(
                    target for source, target in removed_edge_keys if source == module
                )
            ),
        )

    return ArchitectureDifference(
        base_revision=base_revision,
        target_revision=target_revision,
        added_modules=added_modules,
        removed_modules=removed_modules,
        module_dependencies=module_dependencies,
    )


def resolve_commit(repo: Repo, revision: str) -> Commit:
    try:
        return repo.commit(revision)
    except BadName as e:
        raise ValueError(f"Revision '{revision}' is not a valid commit: {e}") from e


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
    target_revision: str | None = None,
) -> ArchitectureDifference:
    resolved_repo_root = resolve_git_repo(repo_root)
    repo = Repo(resolved_repo_root)

    base_commit = resolve_commit(repo, base_revision)
    target_commit = (
        resolve_commit(repo, target_revision)
        if target_revision is not None
        else None
    )
    target_revision_label = (
        target_revision if target_revision is not None else "WORKING_TREE"
    )

    with create_worktree(repo, base_commit) as base_path:
        base_graph = analyze_repo(base_path, config)

    if target_commit is None:
        working_tree_path = Path(repo.working_tree_dir)
        target_graph = analyze_repo(working_tree_path, config)
    else:
        with create_worktree(repo, target_commit) as target_path:
            target_graph = analyze_repo(target_path, config)

    return compare_graphs(
        base_graph,
        target_graph,
        base_revision=base_revision,
        target_revision=target_revision_label,
    )
