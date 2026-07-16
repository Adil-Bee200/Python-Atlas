'''
Integration tests for the analyzer module.
'''

from pathlib import Path

from backend.app.analysis.analyzer import analyze_repo
from backend.app.models.graph_models import Graph, GraphNode, GraphEdge
from backend.app.models.import_models import ParsedResult, ParsedModule, ParsedImport


def test_analyze_repo_valid_path(tmp_path: Path):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    (repo_path / "module1.py").write_text("variable1 = 1")
    graph = analyze_repo(repo_path)
    
    assert isinstance(graph, Graph)
    assert graph.repo_root == repo_path
    assert len(graph.nodes) == 1
    assert len(graph.edges) == 0
    assert len(graph.unresolved_imports) == 0
    assert len(graph.errors) == 0
    assert set(graph.nodes) == {
        GraphNode("module1", Path("module1.py"), 0, 0),
    }
    assert set(graph.edges) == set()
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()

def test_analyze_repo_basic_2_modules_1_import(tmp_path: Path):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    (repo_path / "module1.py").write_text("from module2 import variable1")
    (repo_path / "module2.py").write_text("variable1 = 1")
    graph = analyze_repo(repo_path)
    assert isinstance(graph, Graph)
    assert graph.repo_root == repo_path
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    assert len(graph.unresolved_imports) == 0
    assert len(graph.errors) == 0


    assert set(graph.nodes) == {
        GraphNode("module1", Path("module1.py"), 0, 1),
        GraphNode("module2", Path("module2.py"), 1, 0),
    }
    assert set(graph.edges) == {
        GraphEdge("module1", "module2", 1, ("from module2 import variable1",)),
    }
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()

def test_analyze_repo_no_imports_multiple_modules(tmp_path: Path):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    (repo_path / "module1.py").write_text("variable1 = 1")
    (repo_path / "module2.py").write_text("variable2 = 2")
    (repo_path / "module3.py").write_text("variable3 = 3")
    (repo_path / "module4.py").write_text('print("hello world")')
    graph = analyze_repo(repo_path)
    assert isinstance(graph, Graph)
    assert graph.repo_root == repo_path
    assert len(graph.nodes) == 4
    assert len(graph.edges) == 0
    assert len(graph.unresolved_imports) == 0
    assert len(graph.errors) == 0
    assert set(graph.nodes) == {
        GraphNode("module1", Path("module1.py"), 0, 0),
        GraphNode("module2", Path("module2.py"), 0, 0),
        GraphNode("module3", Path("module3.py"), 0, 0),
        GraphNode("module4", Path("module4.py"), 0, 0),
    }
    assert set(graph.edges) == set()
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()

def test_analyze_repo_simple_multiple_imports_1_module(tmp_path: Path):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    (repo_path / "module1.py").write_text("from module2 import variable1, variable2, variable3")
    (repo_path / "module2.py").write_text("variable1 = 1")
    graph = analyze_repo(repo_path)
    assert isinstance(graph, Graph)
    assert graph.repo_root == repo_path
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    assert len(graph.unresolved_imports) == 0
    assert len(graph.errors) == 0

    assert set(graph.nodes) == {
        GraphNode("module1", Path("module1.py"), 0, 1),
        GraphNode("module2", Path("module2.py"), 1, 0),
    }
    assert set(graph.edges) == {
        GraphEdge("module1", "module2", 1, ("from module2 import variable1, variable2, variable3",)),
    }
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()

def test_analyze_duplicate_imports_1_module(tmp_path: Path):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    (repo_path / "module1.py").write_text(    ## KEEP THIS INDENTATION OR ELSE IT WILL CREATE A BROKEN FILE
"""from module2 import variable1
from module2 import variable2
from module2 import variable3""")
    (repo_path / "module2.py").write_text(
"""variable1 = 1
variable2 = 2
variable3 = 3""")
    graph = analyze_repo(repo_path)
    assert isinstance(graph, Graph)
    assert graph.repo_root == repo_path
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    assert len(graph.unresolved_imports) == 0
    assert len(graph.errors) == 0

    assert set(graph.nodes) == {
        GraphNode("module1", Path("module1.py"), 0, 1),
        GraphNode("module2", Path("module2.py"), 1, 0),
    }
    assert set(graph.edges) == {
        GraphEdge("module1", "module2", 3, ("from module2 import variable1", "from module2 import variable2", "from module2 import variable3",)),
    }
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()

def test_analyze_external_imports_1_module(tmp_path: Path):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    (repo_path / "module1.py").write_text(
"""from FastAPI import FastAPI
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

print("hello world")""")
    graph = analyze_repo(repo_path)
    assert isinstance(graph, Graph)
    assert graph.repo_root == repo_path
    assert len(graph.nodes) == 1
    assert len(graph.edges) == 0
    assert len(graph.unresolved_imports) == 7
    assert len(graph.errors) == 0

    assert set(graph.nodes) == {
        GraphNode("module1", Path("module1.py"), 0, 0),
    }
    assert set(graph.edges) == set()
    assert set(graph.unresolved_imports) == {
        "from FastAPI import FastAPI",
        "from pydantic import BaseModel",
        "from typing import List",
        "from sqlalchemy import create_engine, Column, Integer, String",
        "from sqlalchemy.ext.declarative import declarative_base",
        "from sqlalchemy.orm import sessionmaker",
        "from sqlalchemy.pool import StaticPool",
    }
    assert set(graph.errors) == set()

def test_analyze_repo_only_errors(tmp_path: Path):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    (repo_path / "app").mkdir()
    (repo_path / "module1.py").write_text("print(hello world)")
    (repo_path / "app" / "module2.py").write_text("x =")
    (repo_path / "module3.py").write_text(""" from high import low
    from hello import world""")
    (repo_path / "module4.py").write_text(
"""
from module2 import variable1
from FastAPI import FastAPI
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

def test_function(x, """)
    graph = analyze_repo(repo_path)
    assert isinstance(graph, Graph)
    assert graph.repo_root == repo_path
    assert len(graph.nodes) == 0
    assert len(graph.edges) == 0
    assert len(graph.unresolved_imports) == 0
    assert len(graph.errors) == 4
    assert set(graph.nodes) == set()
    assert set(graph.edges) == set()
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == {
        "module1",
        "app.module2",
        "module3",
        "module4",
    }

def test_analyze_repo_files_from_ignored_dirs(tmp_path: Path):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    (repo_path / "module2.py").write_text("variable1 = 1")
    (repo_path / "venv").mkdir()
    (repo_path / "venv" / "__init__.py").write_text(
"""from module2 import variable1
from FastAPI import FastAPI
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool""")
    (repo_path / ".venv").mkdir()
    (repo_path / ".venv" / "randomFile.py").write_text(
"""from module2 import variable1
from FastAPI import FastAPI
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool""")
    (repo_path / "alembic").mkdir()
    (repo_path / "alembic" / "versions").mkdir()
    (repo_path / "alembic" / "versions" / "1234567890.py").write_text(
"""from module2 import variable1
from FastAPI import FastAPI
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool""")
    graph = analyze_repo(repo_path)
    assert isinstance(graph, Graph)
    assert graph.repo_root == repo_path
    assert len(graph.nodes) == 1
    assert len(graph.edges) == 0
    assert len(graph.unresolved_imports) == 0
    assert len(graph.errors) == 0
    assert set(graph.nodes) == {
        GraphNode("module2", Path("module2.py"), 0, 0),
    }
    assert set(graph.edges) == set()
    assert set(graph.unresolved_imports) == set()
    assert set(graph.errors) == set()


def test_analyze_repo_complex_test_repo(tmp_path: Path):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    (repo_path / "app").mkdir()
    (repo_path / "module1.py").write_text(   # buggy file
"""from module2 import variable1
from FastAPI import FastAPI
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

variable1 = 1

print(hello""")
    (repo_path / "app" / "module2.py").write_text(   # file imports from buggy file
"""from module1 import variable1
from FastAPI import FastAPI
from pydantic import BaseModel
from typing import List

variable2 = 2
variable3 = 3

def test_function(x, y):
    return x + y""")
    (repo_path / "module3.py").write_text(   # file imports from normal file but duplicates import
"""from app.module2 import variable2
from app.module2 import variable3
from app.module2 import variable4

print(variable3)""")
    (repo_path / "app" / "module4.py").write_text(   # file imports from file with errors and normal file
"""from app.module2 import variable1
from module1 import variable1
from FastAPI import FastAPI
from pydantic import BaseModel

def test_function(x, y):
    return x + y""")
    graph = analyze_repo(repo_path)
    assert isinstance(graph, Graph)
    assert graph.repo_root == repo_path
    assert len(graph.nodes) == 3
    assert len(graph.edges) == 2
    assert len(graph.unresolved_imports) == 4
    assert len(graph.errors) == 1

    assert set(graph.nodes) == {
        GraphNode("app.module2", Path("app/module2.py"), 2, 0),
        GraphNode("module3", Path("module3.py"), 0, 1),
        GraphNode("app.module4", Path("app/module4.py"), 0, 1),
    }
    assert set(graph.edges) == {
        GraphEdge("module3", "app.module2", 3, ("from app.module2 import variable2", "from app.module2 import variable3", "from app.module2 import variable4",)),
        GraphEdge("app.module4", "app.module2", 1, ("from app.module2 import variable1",)),
    }
    assert set(graph.unresolved_imports) == {
        "from module1 import variable1",
        "from FastAPI import FastAPI",
        "from pydantic import BaseModel",
        "from typing import List",
    }
    assert set(graph.errors) == {
        "module1",
    }


def test_analyze_repo_nested_package_root_layout(tmp_path: Path):
    repo_path = tmp_path / "dashboard"
    package = repo_path / "backend" / "app"
    (package / "core").mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "core" / "__init__.py").write_text("")
    (package / "core" / "config.py").write_text("settings = {}\n")
    (package / "main.py").write_text(
        "from fastapi import FastAPI\n"
        "from app.core.config import settings\n"
        "app = FastAPI()\n"
    )

    graph = analyze_repo(repo_path)

    assert len(graph.edges) == 1
    assert set(graph.edges) == {
        GraphEdge(
            "backend.app.main",
            "backend.app.core.config",
            1,
            ("from app.core.config import settings",),
        ),
    }
    assert set(graph.unresolved_imports) == {"from fastapi import FastAPI"}
    main_node = next(n for n in graph.nodes if n.module_path == "backend.app.main")
    config_node = next(n for n in graph.nodes if n.module_path == "backend.app.core.config")
    assert main_node.fan_out == 1
    assert config_node.fan_in == 1


def test_analyze_repo_from_package_import_reaches_submodules(tmp_path: Path):
    repo_path = tmp_path / "dashboard"
    routes = repo_path / "backend" / "app" / "api" / "routes"
    routes.mkdir(parents=True)
    (repo_path / "backend" / "app" / "__init__.py").write_text("")
    (repo_path / "backend" / "app" / "api" / "__init__.py").write_text(
        "from app.api.router import api_router\n"
    )
    (repo_path / "backend" / "app" / "api" / "router.py").write_text(
        "from app.api.routes import alerts, summary\n"
    )
    (routes / "__init__.py").write_text("")
    (routes / "alerts.py").write_text("router = object()\n")
    (routes / "summary.py").write_text("router = object()\n")
    (repo_path / "backend" / "app" / "main.py").write_text(
        "from app.api import api_router\n"
    )

    from backend.app.config.models import Configuration, IgnoreConfig
    from backend.app.metrics.entry_points import resolve_entry_points

    config = Configuration(
        entry_points=("backend/app/main.py",),
        ignore=IgnoreConfig(),
    )
    graph = analyze_repo(repo_path, config=config)

    router_targets = {
        edge.target for edge in graph.edges if edge.source == "backend.app.api.router"
    }
    assert "backend.app.api.routes.alerts" in router_targets
    assert "backend.app.api.routes.summary" in router_targets

    resolved = resolve_entry_points(graph, config.entry_points)
    assert resolved.missing == ()
    assert graph.metrics is not None
    assert graph.metrics.dead_modules is not None
    dead = {d.module for d in graph.metrics.dead_modules.dead_modules}
    assert "backend.app.api.routes.alerts" not in dead
    assert "backend.app.api.routes.summary" not in dead


def test_analyze_repo_relative_imports_create_edges_and_reachability(tmp_path: Path):
    repo_path = tmp_path / "dashboard"
    api = repo_path / "app" / "api"
    routes = api / "routes"
    core = repo_path / "app" / "core"
    routes.mkdir(parents=True)
    core.mkdir(parents=True)

    (repo_path / "app" / "__init__.py").write_text("")
    (api / "__init__.py").write_text("from .router import api_router\n")
    (api / "router.py").write_text(
        "from .routes import alerts, summary\n"
        "from ..core.config import settings\n"
    )
    (api / "deps.py").write_text("x = 1\n")
    (routes / "__init__.py").write_text("")
    (routes / "alerts.py").write_text("router = object()\n")
    (routes / "summary.py").write_text("router = object()\n")
    (core / "__init__.py").write_text("")
    (core / "config.py").write_text("settings = {}\n")
    (repo_path / "app" / "main.py").write_text("from .api import api_router\n")

    from backend.app.config.models import Configuration, IgnoreConfig

    config = Configuration(
        entry_points=("app/main.py",),
        ignore=IgnoreConfig(),
    )
    graph = analyze_repo(repo_path, config=config)

    edges = {(e.source, e.target) for e in graph.edges}
    assert ("app.api.router", "app.api.routes.alerts") in edges
    assert ("app.api.router", "app.api.routes.summary") in edges
    assert ("app.api.router", "app.core.config") in edges
    assert ("app.main", "app.api") in edges
    assert ("app.api", "app.api.router") in edges

    assert graph.metrics is not None
    assert graph.metrics.dead_modules is not None
    dead = {d.module for d in graph.metrics.dead_modules.dead_modules}
    assert "app.api.routes.alerts" not in dead
    assert "app.core.config" not in dead
    # deps is never imported
    assert "app.api.deps" in dead


def test_analyze_repo_package_init_reexports_create_direct_edges(tmp_path: Path):
    repo_path = tmp_path / "proj"
    models = repo_path / "app" / "models"
    models.mkdir(parents=True)
    (repo_path / "app" / "__init__.py").write_text("")
    (models / "__init__.py").write_text(
        "from app.models.models import Ticker as Ticker\n"
        "__all__ = ['Ticker']\n"
    )
    (models / "models.py").write_text("class Ticker: pass\n")
    (repo_path / "app" / "main.py").write_text("from app.models import Ticker\n")

    graph = analyze_repo(repo_path)
    main_targets = {e.target for e in graph.edges if e.source == "app.main"}

    assert "app.models" in main_targets
    assert "app.models.models" in main_targets
