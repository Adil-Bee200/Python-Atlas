from __future__ import annotations

import fnmatch
from dataclasses import dataclass

from backend.app.config.models import ArchitectureLayer
from backend.app.models.graph_metrics_models import (
    GraphArchitectureMetrics,
    LayerAmbiguity,
    LayerAssignment,
    LayerViolation,
)
from backend.app.models.graph_models import Graph, GraphEdge, GraphNode

INCOMPLETE_RESULTS_WARNING = (
    "Architecture analysis results are incomplete due to ambiguous layer assignments"
)


@dataclass(frozen=True)
class LayerClassification:
    assignments: tuple[LayerAssignment, ...] = ()
    unclassified_modules: tuple[str, ...] = ()
    ambiguous_assignments: tuple[LayerAmbiguity, ...] = ()


def _module_matches_layer(module_path: str, layer: ArchitectureLayer) -> bool:
    return any(
        fnmatch.fnmatchcase(module_path, pattern)
        for pattern in layer.module_patterns
    )


def _matching_layers(
    module_path: str,
    layers: tuple[ArchitectureLayer, ...],
) -> tuple[ArchitectureLayer, ...]:
    return tuple(layer for layer in layers if _module_matches_layer(module_path, layer))


def classify_modules_by_layer(
    nodes: tuple[GraphNode, ...],
    layers: tuple[ArchitectureLayer, ...],
) -> LayerClassification:
    """Classify modules into layers.

    - 0 matches → unclassified
    - 1 match → assignment
    - 2+ matches → ambiguous (skipped from layer map; analysis continues)
    """
    assignments: list[LayerAssignment] = []
    unclassified: list[str] = []
    ambiguous_assignments: list[LayerAmbiguity] = []

    for node in nodes:
        matches = _matching_layers(node.module_path, layers)
        if len(matches) == 0:
            unclassified.append(node.module_path)
        elif len(matches) == 1:
            assignments.append(
                LayerAssignment(layer=matches[0], module=node.module_path)
            )
        else:
            ambiguous_assignments.append(
                LayerAmbiguity(
                    module=node.module_path,
                    matching_layers=tuple(layer.name for layer in matches),
                )
            )

    ambiguous_assignments.sort(key=lambda item: item.module)
    return LayerClassification(
        assignments=tuple(assignments),
        unclassified_modules=tuple(sorted(unclassified)),
        ambiguous_assignments=tuple(ambiguous_assignments),
    )


def find_layer_violations(
    edges: tuple[GraphEdge, ...],
    assignments: tuple[LayerAssignment, ...],
    layers: tuple[ArchitectureLayer, ...],
) -> tuple[LayerViolation, ...]:
    """Detect forbidden deps between unambiguously classified modules.

    Edges touching unclassified or ambiguous modules are ignored.
    """
    module_to_layer = {assignment.module: assignment.layer for assignment in assignments}
    allowed_by_layer = {
        layer.name: set(layer.allowed_dependencies) for layer in layers
    }

    violations: list[LayerViolation] = []
    for edge in edges:
        source_layer = module_to_layer.get(edge.source)
        target_layer = module_to_layer.get(edge.target)
        if source_layer is None or target_layer is None:
            continue
        if source_layer.name == target_layer.name:
            continue
        if target_layer.name in allowed_by_layer[source_layer.name]:
            continue
        violations.append(
            LayerViolation(
                source_module=edge.source,
                target_module=edge.target,
                source_layer=source_layer.name,
                target_layer=target_layer.name,
            )
        )

    violations.sort(
        key=lambda v: (v.source_module, v.target_module, v.source_layer, v.target_layer)
    )
    return tuple(violations)


def analyze_graph_architecture(
    graph: Graph,
    layers: tuple[ArchitectureLayer, ...],
) -> GraphArchitectureMetrics:
    classification = classify_modules_by_layer(graph.nodes, layers)
    violations = find_layer_violations(
        graph.edges, classification.assignments, layers
    )

    populated_layers = {
        assignment.layer.name for assignment in classification.assignments
    }
    empty_layers = tuple(
        layer.name for layer in layers if layer.name not in populated_layers
    )

    warnings: tuple[str, ...] = ()
    if classification.ambiguous_assignments:
        warnings = (INCOMPLETE_RESULTS_WARNING,)

    return GraphArchitectureMetrics(
        assignments=classification.assignments,
        violations=violations,
        unclassified_modules=classification.unclassified_modules,
        empty_layers=empty_layers,
        ambiguous_assignments=classification.ambiguous_assignments,
        warnings=warnings,
    )
