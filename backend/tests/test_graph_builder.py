from backend.app.graph.graph_builder import build_graph
from backend.app.models.import_models import ParsedResult, ParsedModule, ParsedImport
from backend.app.models.graph_models import Graph, GraphNode, GraphEdge
from pathlib import Path


def test_graph_builder_no_imports_single_module():
    parsed_result = ParsedResult(
        repo_root=Path("test_repo"),
        modules=(
            ParsedModule(
                path=Path("test_repo/test_module.py"),
                module_path="test_module",
                imports=tuple(),
                error=None,
            ),
        ),
    )
    graph = build_graph(parsed_result)
    assert isinstance(graph, Graph)
    assert graph.repo_root == Path("test_repo")
    assert set(graph.nodes) == {
        GraphNode("test_module", Path("test_repo/test_module.py"), 0, 0),
    }
    assert set(graph.edges) == set()
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()

def test_graph_builder_no_imports_multiple_modules():
    parsed_result = ParsedResult(
        repo_root=Path("test_repo"),
        modules=(
            ParsedModule(
                path=Path("test_repo/module1.py"),
                module_path="module1",
                imports=tuple(),
                error=None,
            ),
            ParsedModule(
                path=Path("test_repo/module2.py"),
                module_path="module2",
                imports=tuple(),
                error=None,
            ),
            ParsedModule(
                path=Path("test_repo/module3.py"),
                module_path="module3",
                imports=tuple(),
                error=None,
            ),
        )
    )

    graph = build_graph(parsed_result)
    assert isinstance(graph, Graph)
    assert graph.repo_root == Path("test_repo")
    assert set(graph.nodes) == {
        GraphNode("module1", Path("test_repo/module1.py"), 0, 0),
        GraphNode("module2", Path("test_repo/module2.py"), 0, 0),
        GraphNode("module3", Path("test_repo/module3.py"), 0, 0),
    }
    assert set(graph.edges) == set()
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()

def test_graph_builder_simple_2_modules_1_import():
    parsed_result = ParsedResult(
        repo_root=Path("test_repo"),
        modules = (
            ParsedModule(
                path=Path("test_repo/module1.py"),
                module_path="module1",
                imports=tuple(),
                error=None
            ),
            ParsedModule(
                path=Path("test_repo/module2.py"),
                module_path="module2",
                imports=(
                    ParsedImport(
                        raw_import="from module1 import variable1",
                        module_name="module1"
                    ),
                ),
                error=None
            )
        )
    )

    graph = build_graph(parsed_result)
    assert isinstance(graph, Graph)
    assert graph.repo_root == Path("test_repo")
    assert set(graph.nodes) == {
        GraphNode("module1", Path("test_repo/module1.py"), 1, 0),
        GraphNode("module2", Path("test_repo/module2.py"), 0, 1),
    }
    assert set(graph.edges) == {
        GraphEdge("module2", "module1", 1, ("from module1 import variable1",)),
    }
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()


def test_graph_builder_counts_unique_local_module_dependencies():
    parsed_result = ParsedResult(
        repo_root=Path("test_repo"),
        modules=(
            ParsedModule(
                path=Path("test_repo/module1.py"),
                module_path="module1",
                imports=tuple(),
                error=None,
            ),
            ParsedModule(
                path=Path("test_repo/module2.py"),
                module_path="module2",
                imports=(
                    ParsedImport(
                        raw_import="from module1 import foo",
                        module_name="module1",
                    ),
                    ParsedImport(
                        raw_import="from module1 import bar",
                        module_name="module1",
                    ),
                ),
                error=None,
            ),
        ),
    )

    graph = build_graph(parsed_result)

    assert set(graph.nodes) == {
        GraphNode("module1", Path("test_repo/module1.py"), 1, 0),
        GraphNode("module2", Path("test_repo/module2.py"), 0, 1),
    }
    assert set(graph.edges) == {
        GraphEdge(
            "module2",
            "module1",
            2,
            ("from module1 import bar", "from module1 import foo"),
        ),
    }


def test_graph_builder_import_at_different_levels():
    parsed_result = ParsedResult(
        repo_root=Path("test_repo"),
        modules = (
            ParsedModule(
                path=Path("test_repo/module1.py"),
                module_path="module1",
                imports=(
                    ParsedImport(
                        raw_import="from config.config import CONFIG",
                        module_name="config.config"
                    ),
                ),
                error=None
            ),
            ParsedModule(
                path=Path("test_repo/config/config.py"),
                module_path="config.config",
                imports=(
                    ParsedImport(
                    raw_import="from app.models.model import Model",
                    module_name="app.models.model"
                    ),
                ),
                error=None
            ),
            ParsedModule(
                path=Path("test_repo/app/models/model.py"),
                module_path="app.models.model",
                imports=tuple(),
                error=None
            )
        )
    )

    graph = build_graph(parsed_result)
    assert isinstance(graph, Graph)
    assert graph.repo_root == Path("test_repo")
    assert set(graph.nodes) == {
        GraphNode("module1", Path("test_repo/module1.py"), 0, 1),
        GraphNode("config.config", Path("test_repo/config/config.py"), 1, 1),
        GraphNode("app.models.model", Path("test_repo/app/models/model.py"), 1, 0),
    }
    assert set(graph.edges) == {
        GraphEdge(
            "config.config",
            "app.models.model",
            1,
            ("from app.models.model import Model",),
        ),
        GraphEdge(
            "module1",
            "config.config",
            1,
            ("from config.config import CONFIG",),
        ),
    }
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()


def test_graph_builder_unresolved_imports_simple():
    parsed_result = ParsedResult(
        repo_root=Path("test_repo"),
        modules=(
            ParsedModule(
                path=Path("test_repo/module1.py"),
                module_path="module1",
                imports=(
                    ParsedImport(
                        raw_import="from module2 import variable1",
                        module_name="module2"
                    ),
                    ParsedImport(
                        raw_import="from matplotlib.pyplot import plt",
                        module_name="matplotlib.pyplot"
                    ),
                    ParsedImport(
                        raw_import="from FastAPI import Server",
                        module_name="FastAPI"
                    ),
                    ParsedImport(
                        raw_import="from numpy import array",
                        module_name="numpy"
                    ),
                ),
                error=None,
            ),
        ),
    )

    graph = build_graph(parsed_result)
    assert isinstance(graph, Graph)
    assert graph.repo_root == Path("test_repo")
    assert set(graph.nodes) == {
        GraphNode("module1", Path("test_repo/module1.py"), 0, 0),
    }
    assert set(graph.edges) == set()
    assert set(graph.unresolved_imports) == {
        "from module2 import variable1",
        "from matplotlib.pyplot import plt",
        "from FastAPI import Server",
        "from numpy import array",
    }
    assert set(graph.errors) == set()
    
def test_graph_builder_mix_of_local_and_external_imports():
    parsed_result = ParsedResult(
        repo_root=Path("test_repo"),
        modules=(
            ParsedModule(
                path=Path("test_repo/module1.py"),
                module_path="module1",
                imports=(
                    ParsedImport(
                        raw_import="from FastAPI import app",
                        module_name="FastAPI"
                    ),
                    ParsedImport(
                        raw_import="from numpy import array",
                        module_name="numpy"
                    ),
                ),
                error=None,
            ),
            ParsedModule(
                path=Path("test_repo/module2.py"),
                module_path="module2",
                imports=(
                    ParsedImport(
                        raw_import="from module1 import variable1",
                        module_name="module1"
                    ),
                    ParsedImport(
                        raw_import="from numpy import array",
                        module_name="numpy"
                    ),
                ),
                error=None,
            ),
            ParsedModule(
                path=Path("test_repo/app/models/model.py"),
                module_path="app.models.model",
                imports=(
                    ParsedImport(
                        raw_import="from module1 import variable20",
                        module_name="module1"
                    ),
                ),
                error=None,
            ),
        ),
    )

    graph = build_graph(parsed_result)
    assert isinstance(graph, Graph)
    assert graph.repo_root == Path("test_repo")
    assert set(graph.nodes) == {
        GraphNode("module1", Path("test_repo/module1.py"), 2, 0),
        GraphNode("module2", Path("test_repo/module2.py"), 0, 1),
        GraphNode("app.models.model", Path("test_repo/app/models/model.py"), 0, 1),
    }
    assert set(graph.edges) == {
        GraphEdge("module2", "module1", 1, ("from module1 import variable1",)),
        GraphEdge("app.models.model", "module1", 1, ("from module1 import variable20",)),
    }
    assert set(graph.unresolved_imports) == {
        "from FastAPI import app",
        "from numpy import array",
    }
    assert set(graph.errors) == set()

def test_graph_builder_only_errors():
    parsed_result = ParsedResult(
        repo_root=Path("test_repo"),
        modules=(
            ParsedModule(
                path=Path("test_repo/module1.py"),
                module_path="module1",
                imports=tuple(),
                error=Exception("Error in module1"),
            ),
            ParsedModule(
                path=Path("test_repo/app/models/model.py"),
                module_path="app.models.model",
                imports=tuple(),
                error=Exception("Error in app.models.model"),
            ),
            ParsedModule(
                path=Path("test_repo/config/config.py"),
                module_path="config.config",
                imports=tuple(),
                error=Exception("Error in config.config"),
            ),
        ),
    )
    graph = build_graph(parsed_result)
    assert isinstance(graph, Graph)
    assert graph.repo_root == Path("test_repo")
    assert set(graph.nodes) == set()
    assert set(graph.edges) == set()
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == {"module1", "app.models.model", "config.config"}

def test_graph_builder_mix_of_local_and_external_imports_and_errors():
    parsed_result = ParsedResult(
        repo_root=Path("test_repo"),
        modules=(
            ParsedModule(
                path=Path("test_repo/module1.py"),
                module_path="module1",
                imports=tuple(),
                error=Exception("Error in module1"),
            ),
            ParsedModule(
                path=Path("test_repo/module2.py"),
                module_path="module2",
                imports=(
                    ParsedImport(
                        raw_import="from module1 import variable1",
                        module_name="module1"
                    ),
                    ParsedImport(
                        raw_import="from numpy import array",
                        module_name="numpy"
                    ),
                    ParsedImport(
                        raw_import="from app.models.model import Model",
                        module_name="app.models.model"
                    ),
                ),
                error=None,
            ),
            ParsedModule(
                path=Path("test_repo/app/models/model.py"),
                module_path="app.models.model",
                imports=(
                    ParsedImport(
                        raw_import="from module2 import variable20",
                        module_name="module2"
                    ),
                ),
                error=None,
            ),
            ParsedModule(
                path=Path("test_repo/config/config.py"),
                module_path="config.config",
                imports=(
                    ParsedImport(
                        raw_import="from module2 import variable20",
                        module_name="module2"
                    ),
                    ParsedImport(
                        raw_import="from FastAPI import app",
                        module_name="FastAPI"
                    ),
                ),
                error=None,
            ),
            ParsedModule(
                path=Path("test_repo/module3.py"),
                module_path="module3",
                imports=tuple(),
                error=Exception("Error in module3"),
            ),
            ParsedModule(
                path=Path("test_repo/app/api/users.py"),
                module_path="app.api.users",
                imports=(
                    ParsedImport(
                        raw_import="from app.models.model import Model1",
                        module_name="app.models.model"
                    ),
                    ParsedImport(
                        raw_import="from app.models.model import Model2",
                        module_name="app.models.model"
                    ),
                    ParsedImport(
                        raw_import="from module3 import variable30",
                        module_name="module3"
                    ),
                ),
                error=None,
            ),
        ),
    )
    graph = build_graph(parsed_result)
    assert isinstance(graph, Graph)
    assert graph.repo_root == Path("test_repo")
    assert set(graph.nodes) == {
        GraphNode("module2", Path("test_repo/module2.py"), 2, 1),
        GraphNode("app.models.model", Path("test_repo/app/models/model.py"), 2, 1),
        GraphNode("config.config", Path("test_repo/config/config.py"), 0, 1),
        GraphNode("app.api.users", Path("test_repo/app/api/users.py"), 0, 1),
    }
    assert set(graph.edges) == {
        GraphEdge("module2", "app.models.model", 1, ("from app.models.model import Model",)),
        GraphEdge("app.models.model", "module2", 1, ("from module2 import variable20",)),
        GraphEdge("config.config", "module2", 1, ("from module2 import variable20",)),
        GraphEdge("app.api.users", "app.models.model", 2, ("from app.models.model import Model1", "from app.models.model import Model2",)),
    }
    assert set(graph.unresolved_imports) == {
        "from module1 import variable1",
        "from numpy import array",
        "from FastAPI import app",
        "from module3 import variable30",
    }
    assert set(graph.errors) == {
        "module1",
        "module3",
    }


def test_graph_builder_resolves_imports_under_nested_package_root():
    parsed_result = ParsedResult(
        repo_root=Path("repo"),
        modules=(
            ParsedModule(
                path=Path("backend/app/main.py"),
                module_path="backend.app.main",
                imports=(
                    ParsedImport(
                        raw_import="from app.core.config import settings",
                        module_name="app.core.config",
                    ),
                    ParsedImport(
                        raw_import="from fastapi import FastAPI",
                        module_name="fastapi",
                    ),
                ),
                error=None,
            ),
            ParsedModule(
                path=Path("backend/app/core/config.py"),
                module_path="backend.app.core.config",
                imports=tuple(),
                error=None,
            ),
            ParsedModule(
                path=Path("backend/app/core/__init__.py"),
                module_path="backend.app.core",
                imports=tuple(),
                error=None,
            ),
        ),
    )

    graph = build_graph(parsed_result)
    assert set(graph.edges) == {
        GraphEdge(
            "backend.app.main",
            "backend.app.core.config",
            1,
            ("from app.core.config import settings",),
        ),
    }
    assert set(graph.unresolved_imports) == {"from fastapi import FastAPI"}
    assert {node.module_path: (node.fan_in, node.fan_out) for node in graph.nodes} == {
        "backend.app.main": (0, 1),
        "backend.app.core.config": (1, 0),
        "backend.app.core": (0, 0),
    }


def test_graph_builder_ambiguous_suffix_stays_unresolved():
    parsed_result = ParsedResult(
        repo_root=Path("repo"),
        modules=(
            ParsedModule(
                path=Path("backend/app/main.py"),
                module_path="backend.app.main",
                imports=(
                    ParsedImport(
                        raw_import="from app.config import settings",
                        module_name="app.config",
                        imported_names=("settings",),
                    ),
                ),
                error=None,
            ),
            ParsedModule(
                path=Path("backend/app/config.py"),
                module_path="backend.app.config",
                imports=tuple(),
                error=None,
            ),
            ParsedModule(
                path=Path("services/app/config.py"),
                module_path="services.app.config",
                imports=tuple(),
                error=None,
            ),
        ),
    )

    graph = build_graph(parsed_result)
    assert graph.edges == ()
    assert set(graph.unresolved_imports) == {"from app.config import settings"}


def test_graph_builder_expands_from_package_import_to_submodules():
    parsed_result = ParsedResult(
        repo_root=Path("repo"),
        modules=(
            ParsedModule(
                path=Path("backend/app/api/router.py"),
                module_path="backend.app.api.router",
                imports=(
                    ParsedImport(
                        raw_import="from app.api.routes import alerts, summary",
                        module_name="app.api.routes",
                        imported_names=("alerts", "summary"),
                    ),
                ),
                error=None,
            ),
            ParsedModule(
                path=Path("backend/app/api/routes/__init__.py"),
                module_path="backend.app.api.routes",
                imports=tuple(),
                error=None,
            ),
            ParsedModule(
                path=Path("backend/app/api/routes/alerts.py"),
                module_path="backend.app.api.routes.alerts",
                imports=tuple(),
                error=None,
            ),
            ParsedModule(
                path=Path("backend/app/api/routes/summary.py"),
                module_path="backend.app.api.routes.summary",
                imports=tuple(),
                error=None,
            ),
        ),
    )

    graph = build_graph(parsed_result)
    targets = {edge.target for edge in graph.edges if edge.source == "backend.app.api.router"}

    assert targets == {
        "backend.app.api.routes",
        "backend.app.api.routes.alerts",
        "backend.app.api.routes.summary",
    }
    assert graph.unresolved_imports == ()


def test_graph_builder_symbol_import_does_not_create_fake_module_edge():
    parsed_result = ParsedResult(
        repo_root=Path("repo"),
        modules=(
            ParsedModule(
                path=Path("main.py"),
                module_path="main",
                imports=(
                    ParsedImport(
                        raw_import="from models import User",
                        module_name="models",
                        imported_names=("User",),
                    ),
                ),
                error=None,
            ),
            ParsedModule(
                path=Path("models.py"),
                module_path="models",
                imports=tuple(),
                error=None,
            ),
        ),
    )

    graph = build_graph(parsed_result)

    assert set(graph.edges) == {
        GraphEdge("main", "models", 1, ("from models import User",)),
    }
    assert graph.unresolved_imports == ()


def test_graph_builder_uses_resolved_relative_module_names():
    parsed_result = ParsedResult(
        repo_root=Path("repo"),
        modules=(
            ParsedModule(
                path=Path("app/api/router.py"),
                module_path="app.api.router",
                imports=(
                    ParsedImport(
                        raw_import="from .routes import alerts",
                        module_name="app.api.routes",
                        imported_names=("alerts",),
                    ),
                    ParsedImport(
                        raw_import="from ..core.config import settings",
                        module_name="app.core.config",
                        imported_names=("settings",),
                    ),
                ),
                error=None,
            ),
            ParsedModule(
                path=Path("app/api/routes/__init__.py"),
                module_path="app.api.routes",
                imports=tuple(),
                error=None,
            ),
            ParsedModule(
                path=Path("app/api/routes/alerts.py"),
                module_path="app.api.routes.alerts",
                imports=tuple(),
                error=None,
            ),
            ParsedModule(
                path=Path("app/core/config.py"),
                module_path="app.core.config",
                imports=tuple(),
                error=None,
            ),
        ),
    )

    graph = build_graph(parsed_result)
    targets = {edge.target for edge in graph.edges if edge.source == "app.api.router"}

    assert targets == {
        "app.api.routes",
        "app.api.routes.alerts",
        "app.core.config",
    }
    assert graph.unresolved_imports == ()
