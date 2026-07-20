from dataclasses import dataclass, field

from backend.app.config.models import ArchitectureLayer


@dataclass(frozen=True)
class ModuleDependencyDifference:
    module: str
    added_dependencies: tuple[str, ...]
    removed_dependencies: tuple[str, ...]


@dataclass(frozen=True)
class StructureDifference:
    added_modules: tuple[str, ...]
    removed_modules: tuple[str, ...]
    module_dependencies: dict[str, ModuleDependencyDifference]


@dataclass(frozen=True)
class LayerAssignment:
    layer: ArchitectureLayer
    module: str


@dataclass(frozen=True)
class LayerAmbiguity:
    module: str
    matching_layers: tuple[str, ...]


@dataclass(frozen=True)
class LayerClassification:
    assignments: tuple[LayerAssignment, ...] = ()
    unclassified_modules: tuple[str, ...] = ()
    ambiguous_assignments: tuple[LayerAmbiguity, ...] = ()


@dataclass(frozen=True)
class LayerViolation:
    source_module: str
    target_module: str
    source_layer: str
    target_layer: str


@dataclass(frozen=True)
class ArchitectureDifference:
    added_assignments: tuple[LayerAssignment, ...] = ()
    removed_assignments: tuple[LayerAssignment, ...] = ()
    added_violations: tuple[LayerViolation, ...] = ()
    removed_violations: tuple[LayerViolation, ...] = ()
    added_unclassified_modules: tuple[str, ...] = ()
    removed_unclassified_modules: tuple[str, ...] = ()
    added_empty_layers: tuple[str, ...] = ()
    removed_empty_layers: tuple[str, ...] = ()
    added_ambiguous_assignments: tuple[LayerAmbiguity, ...] = ()
    removed_ambiguous_assignments: tuple[LayerAmbiguity, ...] = ()


@dataclass(frozen=True)
class MetricValueChange:
    module: str
    before: float
    after: float


@dataclass(frozen=True)
class GraphCentralityDifference:
    pagerank: tuple[MetricValueChange, ...] = ()
    betweenness: tuple[MetricValueChange, ...] = ()
    in_degree: tuple[MetricValueChange, ...] = ()
    out_degree: tuple[MetricValueChange, ...] = ()


@dataclass(frozen=True)
class GraphDeadModules:
    module: str
    reason: str


@dataclass(frozen=True)
class GraphDeadModulesMetrics:
    dead_modules: tuple[GraphDeadModules, ...]
    dead_modules_percentage: float


@dataclass(frozen=True)
class GraphMetricsDifference:
    centrality: GraphCentralityDifference = field(
        default_factory=GraphCentralityDifference
    )
    added_isolates: tuple[str, ...] = ()
    removed_isolates: tuple[str, ...] = ()
    added_cycles: tuple[tuple[str, ...], ...] = ()
    removed_cycles: tuple[tuple[str, ...], ...] = ()
    added_hub_modules: tuple[str, ...] = ()
    removed_hub_modules: tuple[str, ...] = ()
    added_dead_modules: tuple[GraphDeadModules, ...] = ()
    removed_dead_modules: tuple[GraphDeadModules, ...] = ()
    dead_modules_percentage_before: float | None = None
    dead_modules_percentage_after: float | None = None


@dataclass(frozen=True)
class GraphDifference:
    base_revision: str
    target_revision: str
    structure: StructureDifference
    architecture: ArchitectureDifference | None = None
    metrics: GraphMetricsDifference | None = None


@dataclass(frozen=True)
class GraphArchitectureMetrics:
    assignments: tuple[LayerAssignment, ...] = ()
    violations: tuple[LayerViolation, ...] = ()
    unclassified_modules: tuple[str, ...] = ()
    empty_layers: tuple[str, ...] = ()
    ambiguous_assignments: tuple[LayerAmbiguity, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class GraphHubModule:
    module: str
    in_degree: int
    out_degree: int
    pagerank: float
    hub_score: float


@dataclass(frozen=True)
class GraphHubModulesMetrics:
    hub_modules: tuple[GraphHubModule, ...]
    in_degree_threshold: float
    max_out_degree: float


@dataclass(frozen=True)
class GraphCentralityMetrics:
    pagerank_centrality: dict[str, float]
    betweenness_centrality: dict[str, float]
    in_degree_centrality: dict[str, float]
    out_degree_centrality: dict[str, float]


@dataclass(frozen=True)
class GraphIsolatesMetrics:
    isolates: tuple[str, ...]


@dataclass(frozen=True)
class GraphCyclesMetrics:
    cycles: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class GraphMetrics:
    centrality: GraphCentralityMetrics
    isolates: GraphIsolatesMetrics
    cycles: GraphCyclesMetrics
    hub_modules: GraphHubModulesMetrics
    dead_modules: GraphDeadModulesMetrics | None = None
    architecture: GraphArchitectureMetrics | None = None
    missing_entry_points: tuple[str, ...] = ()
