from backend.app.config.models import ArchitectureLayer
from backend.app.metrics.architecture_metrics import (
    INCOMPLETE_RESULTS_WARNING,
    analyze_graph_architecture,
    classify_modules_by_layer,
    find_layer_violations,
)
from backend.app.models.graph_metrics_models import (
    LayerAmbiguity,
    LayerAssignment,
    LayerViolation,
)
from backend.tests.utils import _graph

API = ArchitectureLayer(
    name="api",
    module_patterns=("app.api.*",),
    allowed_dependencies=("services",),
)
SERVICES = ArchitectureLayer(
    name="services",
    module_patterns=("app.services.*",),
    allowed_dependencies=("repositories",),
)
REPOSITORIES = ArchitectureLayer(
    name="repositories",
    module_patterns=("app.repositories.*",),
    allowed_dependencies=("models",),
)
MODELS = ArchitectureLayer(
    name="models",
    module_patterns=("app.models.*",),
    allowed_dependencies=(),
)
LAYERS = (API, SERVICES, REPOSITORIES, MODELS)


def test_classify_modules_by_layer_assigns_single_matches():
    graph = _graph(
        (
            "app.api.routes",
            "app.services.users",
            "app.models.user",
            "app.utils.helpers",
        )
    )

    classification = classify_modules_by_layer(graph.nodes, LAYERS)

    assert classification.assignments == (
        LayerAssignment(layer=API, module="app.api.routes"),
        LayerAssignment(layer=SERVICES, module="app.services.users"),
        LayerAssignment(layer=MODELS, module="app.models.user"),
    )
    assert classification.unclassified_modules == ("app.utils.helpers",)
    assert classification.ambiguous_assignments == ()


def test_classify_modules_by_layer_empty_layers():
    graph = _graph(("app.api.routes", "app.models.user"))

    classification = classify_modules_by_layer(graph.nodes, ())

    assert classification.assignments == ()
    assert classification.unclassified_modules == ("app.api.routes", "app.models.user")
    assert classification.ambiguous_assignments == ()


def test_classify_modules_by_layer_reports_ambiguity():
    overlapping = (
        ArchitectureLayer(
            name="api",
            module_patterns=("app.*",),
            allowed_dependencies=("services",),
        ),
        ArchitectureLayer(
            name="services",
            module_patterns=("app.services.*",),
            allowed_dependencies=(),
        ),
    )
    graph = _graph(("app.services.users", "app.api.routes"))

    classification = classify_modules_by_layer(graph.nodes, overlapping)

    assert classification.assignments == (
        LayerAssignment(layer=overlapping[0], module="app.api.routes"),
    )
    assert classification.unclassified_modules == ()
    assert classification.ambiguous_assignments == (
        LayerAmbiguity(
            module="app.services.users",
            matching_layers=("api", "services"),
        ),
    )


def test_find_layer_violations_detects_forbidden_dependency():
    graph = _graph(
        ("app.api.routes", "app.models.user"),
        (("app.api.routes", "app.models.user"),),
    )
    classification = classify_modules_by_layer(graph.nodes, LAYERS)

    violations = find_layer_violations(
        graph.edges, classification.assignments, LAYERS
    )

    assert violations == (
        LayerViolation(
            source_module="app.api.routes",
            target_module="app.models.user",
            source_layer="api",
            target_layer="models",
        ),
    )


def test_find_layer_violations_allows_configured_dependency():
    graph = _graph(
        ("app.api.routes", "app.services.users"),
        (("app.api.routes", "app.services.users"),),
    )
    classification = classify_modules_by_layer(graph.nodes, LAYERS)

    assert find_layer_violations(
        graph.edges, classification.assignments, LAYERS
    ) == ()


def test_find_layer_violations_allows_same_layer_dependency():
    graph = _graph(
        ("app.api.routes", "app.api.deps"),
        (("app.api.routes", "app.api.deps"),),
    )
    classification = classify_modules_by_layer(graph.nodes, LAYERS)

    assert find_layer_violations(
        graph.edges, classification.assignments, LAYERS
    ) == ()


def test_find_layer_violations_skips_unclassified_endpoints():
    graph = _graph(
        ("app.api.routes", "app.utils.helpers"),
        (("app.api.routes", "app.utils.helpers"),),
    )
    classification = classify_modules_by_layer(graph.nodes, LAYERS)

    assert find_layer_violations(
        graph.edges, classification.assignments, LAYERS
    ) == ()


def test_analyze_graph_architecture_reports_unclassified_and_empty_layers():
    graph = _graph(
        (
            "app.api.routes",
            "app.services.users",
            "app.utils.helpers",
        ),
        (
            ("app.api.routes", "app.services.users"),
            ("app.services.users", "app.utils.helpers"),
        ),
    )

    metrics = analyze_graph_architecture(graph, LAYERS)

    assert metrics.assignments == (
        LayerAssignment(layer=API, module="app.api.routes"),
        LayerAssignment(layer=SERVICES, module="app.services.users"),
    )
    assert metrics.violations == ()
    assert metrics.unclassified_modules == ("app.utils.helpers",)
    assert metrics.empty_layers == ("repositories", "models")
    assert metrics.ambiguous_assignments == ()
    assert metrics.warnings == ()


def test_analyze_graph_architecture_skips_ambiguous_module_and_continues():
    overlapping = (
        ArchitectureLayer(
            name="api",
            module_patterns=("app.api.*", "app.shared.*"),
            allowed_dependencies=("services",),
        ),
        ArchitectureLayer(
            name="services",
            module_patterns=("app.services.*", "app.shared.*"),
            allowed_dependencies=("models",),
        ),
        ArchitectureLayer(
            name="models",
            module_patterns=("app.models.*",),
            allowed_dependencies=(),
        ),
    )
    graph = _graph(
        (
            "app.api.routes",
            "app.services.users",
            "app.shared.helpers",
            "app.models.user",
        ),
        (
            ("app.api.routes", "app.services.users"),
            ("app.api.routes", "app.shared.helpers"),
            ("app.services.users", "app.models.user"),
            ("app.api.routes", "app.models.user"),
        ),
    )

    metrics = analyze_graph_architecture(graph, overlapping)

    assert metrics.ambiguous_assignments == (
        LayerAmbiguity(
            module="app.shared.helpers",
            matching_layers=("api", "services"),
        ),
    )
    assert metrics.assignments == (
        LayerAssignment(layer=overlapping[0], module="app.api.routes"),
        LayerAssignment(layer=overlapping[1], module="app.services.users"),
        LayerAssignment(layer=overlapping[2], module="app.models.user"),
    )
    assert metrics.unclassified_modules == ()
    assert metrics.empty_layers == ()
    # Edge touching ambiguous module is ignored; remaining violation is kept.
    assert metrics.violations == (
        LayerViolation(
            source_module="app.api.routes",
            target_module="app.models.user",
            source_layer="api",
            target_layer="models",
        ),
    )
    assert metrics.warnings == (INCOMPLETE_RESULTS_WARNING,)


def test_analyze_graph_architecture_full_stack_with_violation():
    graph = _graph(
        (
            "app.api.routes",
            "app.services.users",
            "app.repositories.user_repo",
            "app.models.user",
        ),
        (
            ("app.api.routes", "app.services.users"),
            ("app.services.users", "app.repositories.user_repo"),
            ("app.repositories.user_repo", "app.models.user"),
            ("app.api.routes", "app.models.user"),
        ),
    )

    metrics = analyze_graph_architecture(graph, LAYERS)

    assert len(metrics.assignments) == 4
    assert metrics.unclassified_modules == ()
    assert metrics.empty_layers == ()
    assert metrics.ambiguous_assignments == ()
    assert metrics.warnings == ()
    assert metrics.violations == (
        LayerViolation(
            source_module="app.api.routes",
            target_module="app.models.user",
            source_layer="api",
            target_layer="models",
        ),
    )
