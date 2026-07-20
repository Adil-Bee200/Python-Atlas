from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from git import Repo
from git.exc import BadName
from git.objects import Commit

from backend.app.analysis.analyzer import analyze_repo
from backend.app.config.models import Configuration
from backend.app.git.worktree import create_worktree
from backend.app.models.graph_metrics_models import (
    ArchitectureDifference,
    GraphArchitectureMetrics,
    GraphCentralityDifference,
    GraphCentralityMetrics,
    GraphDifference,
    GraphMetricsDifference,
    LayerAmbiguity,
    LayerAssignment,
    LayerViolation,
    MetricValueChange,
    ModuleDependencyDifference,
    StructureDifference,
)
from backend.app.models.graph_models import Graph


@dataclass(frozen=True)
class ModuleSetDifference:
    added_modules: tuple[str, ...]
    removed_modules: tuple[str, ...]


@dataclass(frozen=True)
class EdgeKeyDifference:
    added_edge_keys: frozenset[tuple[str, str]]
    removed_edge_keys: frozenset[tuple[str, str]]


def graph_module_paths(graph: Graph) -> set[str]:
    return {node.module_path for node in graph.nodes}


def graph_edge_keys(graph: Graph) -> set[tuple[str, str]]:
    return {(edge.source, edge.target) for edge in graph.edges}


def compare_module_sets(
    base_graph: Graph,
    target_graph: Graph,
) -> ModuleSetDifference:
    base_modules = graph_module_paths(base_graph)
    target_modules = graph_module_paths(target_graph)

    return ModuleSetDifference(
        added_modules=tuple(sorted(target_modules - base_modules)),
        removed_modules=tuple(sorted(base_modules - target_modules)),
    )


def compare_edge_keys(
    base_graph: Graph,
    target_graph: Graph,
) -> EdgeKeyDifference:
    base_keys = graph_edge_keys(base_graph)
    target_keys = graph_edge_keys(target_graph)

    return EdgeKeyDifference(
        added_edge_keys=frozenset(target_keys - base_keys),
        removed_edge_keys=frozenset(base_keys - target_keys),
    )


def modules_with_dependency_changes(
    edge_diff: EdgeKeyDifference,
) -> tuple[str, ...]:
    modules = {
        source for source, _ in edge_diff.added_edge_keys
    } | {
        source for source, _ in edge_diff.removed_edge_keys
    }
    return tuple(sorted(modules))


def build_module_dependency_differences(
    edge_diff: EdgeKeyDifference,
) -> dict[str, ModuleDependencyDifference]:
    module_dependencies: dict[str, ModuleDependencyDifference] = {}
    for module in modules_with_dependency_changes(edge_diff):
        module_dependencies[module] = ModuleDependencyDifference(
            module=module,
            added_dependencies=tuple(
                sorted(
                    target
                    for source, target in edge_diff.added_edge_keys
                    if source == module
                )
            ),
            removed_dependencies=tuple(
                sorted(
                    target
                    for source, target in edge_diff.removed_edge_keys
                    if source == module
                )
            ),
        )
    return module_dependencies


def compare_structure(
    base_graph: Graph,
    target_graph: Graph,
) -> StructureDifference:
    module_set_diff = compare_module_sets(base_graph, target_graph)
    edge_key_diff = compare_edge_keys(base_graph, target_graph)

    return StructureDifference(
        added_modules=module_set_diff.added_modules,
        removed_modules=module_set_diff.removed_modules,
        module_dependencies=build_module_dependency_differences(edge_key_diff),
    )


def _assignment_key(assignment: LayerAssignment) -> tuple[str, str]:
    return (assignment.module, assignment.layer.name)


def _violation_key(violation: LayerViolation) -> tuple[str, str, str, str]:
    return (
        violation.source_module,
        violation.target_module,
        violation.source_layer,
        violation.target_layer,
    )


def _ambiguity_key(ambiguity: LayerAmbiguity) -> tuple[str, tuple[str, ...]]:
    return (ambiguity.module, ambiguity.matching_layers)


def _architecture_metrics(
    graph: Graph,
) -> GraphArchitectureMetrics | None:
    if graph.metrics is None:
        return None
    return graph.metrics.architecture


def compare_architecture(
    base_graph: Graph,
    target_graph: Graph,
) -> ArchitectureDifference | None:
    base_arch = _architecture_metrics(base_graph)
    target_arch = _architecture_metrics(target_graph)
    if base_arch is None or target_arch is None:
        return None

    base_assignments = {
        _assignment_key(assignment): assignment
        for assignment in base_arch.assignments
    }
    target_assignments = {
        _assignment_key(assignment): assignment
        for assignment in target_arch.assignments
    }
    added_assignment_keys = set(target_assignments) - set(base_assignments)
    removed_assignment_keys = set(base_assignments) - set(target_assignments)

    base_violations = {
        _violation_key(violation): violation for violation in base_arch.violations
    }
    target_violations = {
        _violation_key(violation): violation for violation in target_arch.violations
    }
    added_violation_keys = set(target_violations) - set(base_violations)
    removed_violation_keys = set(base_violations) - set(target_violations)

    base_unclassified = set(base_arch.unclassified_modules)
    target_unclassified = set(target_arch.unclassified_modules)

    base_empty = set(base_arch.empty_layers)
    target_empty = set(target_arch.empty_layers)

    base_ambiguous = {
        _ambiguity_key(item): item for item in base_arch.ambiguous_assignments
    }
    target_ambiguous = {
        _ambiguity_key(item): item for item in target_arch.ambiguous_assignments
    }
    added_ambiguous_keys = set(target_ambiguous) - set(base_ambiguous)
    removed_ambiguous_keys = set(base_ambiguous) - set(target_ambiguous)

    return ArchitectureDifference(
        added_assignments=tuple(
            target_assignments[key] for key in sorted(added_assignment_keys)
        ),
        removed_assignments=tuple(
            base_assignments[key] for key in sorted(removed_assignment_keys)
        ),
        added_violations=tuple(
            target_violations[key] for key in sorted(added_violation_keys)
        ),
        removed_violations=tuple(
            base_violations[key] for key in sorted(removed_violation_keys)
        ),
        added_unclassified_modules=tuple(
            sorted(target_unclassified - base_unclassified)
        ),
        removed_unclassified_modules=tuple(
            sorted(base_unclassified - target_unclassified)
        ),
        added_empty_layers=tuple(sorted(target_empty - base_empty)),
        removed_empty_layers=tuple(sorted(base_empty - target_empty)),
        added_ambiguous_assignments=tuple(
            target_ambiguous[key] for key in sorted(added_ambiguous_keys)
        ),
        removed_ambiguous_assignments=tuple(
            base_ambiguous[key] for key in sorted(removed_ambiguous_keys)
        ),
    )


def _normalize_cycle(cycle: tuple[str, ...]) -> tuple[str, ...]:
    if not cycle:
        return cycle
    start = cycle.index(min(cycle))
    return cycle[start:] + cycle[:start]


def _centrality_changes(
    base_values: dict[str, float],
    target_values: dict[str, float],
) -> tuple[MetricValueChange, ...]:
    changes: list[MetricValueChange] = []
    for module in sorted(set(base_values) & set(target_values)):
        before = base_values[module]
        after = target_values[module]
        if before != after:
            changes.append(
                MetricValueChange(module=module, before=before, after=after)
            )
    return tuple(changes)


def _compare_centrality(
    base: GraphCentralityMetrics,
    target: GraphCentralityMetrics,
) -> GraphCentralityDifference:
    return GraphCentralityDifference(
        pagerank=_centrality_changes(
            base.pagerank_centrality, target.pagerank_centrality
        ),
        betweenness=_centrality_changes(
            base.betweenness_centrality, target.betweenness_centrality
        ),
        in_degree=_centrality_changes(
            base.in_degree_centrality, target.in_degree_centrality
        ),
        out_degree=_centrality_changes(
            base.out_degree_centrality, target.out_degree_centrality
        ),
    )


def compare_metrics(
    base_graph: Graph,
    target_graph: Graph,
) -> GraphMetricsDifference | None:
    if base_graph.metrics is None or target_graph.metrics is None:
        return None

    base = base_graph.metrics
    target = target_graph.metrics

    base_isolates = set(base.isolates.isolates)
    target_isolates = set(target.isolates.isolates)

    base_cycles = {_normalize_cycle(cycle) for cycle in base.cycles.cycles}
    target_cycles = {_normalize_cycle(cycle) for cycle in target.cycles.cycles}

    base_hubs = {hub.module for hub in base.hub_modules.hub_modules}
    target_hubs = {hub.module for hub in target.hub_modules.hub_modules}

    return GraphMetricsDifference(
        centrality=_compare_centrality(base.centrality, target.centrality),
        added_isolates=tuple(sorted(target_isolates - base_isolates)),
        removed_isolates=tuple(sorted(base_isolates - target_isolates)),
        added_cycles=tuple(sorted(target_cycles - base_cycles)),
        removed_cycles=tuple(sorted(base_cycles - target_cycles)),
        added_hub_modules=tuple(sorted(target_hubs - base_hubs)),
        removed_hub_modules=tuple(sorted(base_hubs - target_hubs)),
    )


def compare_graphs(
    base_graph: Graph,
    target_graph: Graph,
    *,
    base_revision: str,
    target_revision: str,
) -> GraphDifference:
    return GraphDifference(
        base_revision=base_revision,
        target_revision=target_revision,
        structure=compare_structure(base_graph, target_graph),
        architecture=compare_architecture(base_graph, target_graph),
        metrics=compare_metrics(base_graph, target_graph),
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
) -> GraphDifference:
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
