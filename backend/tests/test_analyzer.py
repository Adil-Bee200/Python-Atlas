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


# Tests for basic functionality
'''
- Only errors (should go to errors)
- Imports to files with errors 
- Only ignored files 
'''

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