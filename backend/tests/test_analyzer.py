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
