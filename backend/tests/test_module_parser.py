from pathlib import Path
from backend.app.parser.module_parser import parse_module
from backend.app.models.scan_models import PythonModule

def test_parse_module_extracts_top_level_imports(tmp_path):
    ## test: a module that imports only at the top-level
    app_dir = tmp_path / "app"
    app_dir.mkdir()

    file_path = app_dir / "main.py"
    file_path.write_text(
        """
import os
import sys as system
from pathlib import Path
from app.models import User, Post


def main():
    print("Hello, World!")

    for i in range(10):
        print(i)
    
    ## some commments
    x = 1
    y = 2
    z = x + y
"""
    )

    module = PythonModule(
        path=Path("app/main.py"),
        module_path="app.main",
    )

    parsed = parse_module(tmp_path, module)

    assert parsed.path == Path("app/main.py")
    assert parsed.module_path == "app.main"

    imports = {imp.module_name for imp in parsed.imports}

    assert imports == {
        "os",
        "sys",
        "pathlib",
        "app.models",
    }

    assert len(parsed.imports) == 4

def test_parse_module_extracts_imports_from_submodule(tmp_path):
    ## test: a module that imports from a submodule
    app_dir = tmp_path / "app"
    app_dir.mkdir()

    submodule_dir = app_dir / "submodule"
    submodule_dir.mkdir()

    submodule_file_path = submodule_dir / "submodule.py"
    submodule_file_path.write_text(
        """
from app.models import User, Post
from app.config import settings
import logging
import pydantic
import app.other_module.main as other_module_main
from app.submodule.submodule_function import submodule_function

def submodule_function():
    print("Hello, World!")
    logging.info("Hello, World!")
    pydantic.validate_model(User)

"""
    )

    module = PythonModule(
        path = Path("app/submodule/submodule.py"),
        module_path = "app.submodule.submodule",
    )

    parsed = parse_module(tmp_path, module)

    assert parsed.path == Path("app/submodule/submodule.py")
    assert parsed.module_path == "app.submodule.submodule"

    imports = {imp.module_name for imp in parsed.imports}

    assert imports == {
        "app.models",
        "app.config",
        "logging",
        "pydantic",
        "app.submodule.submodule_function",
        "app.other_module.main",
    }

    assert len(parsed.imports) == 6


def test_parse_module_import_not_at_top_level(tmp_path):
    ## test: a module that imports not at the top-level
    app_dir = tmp_path / "app"
    app_dir.mkdir()

    submodule_dir = app_dir / "submodule"
    submodule_dir.mkdir()
    
    submodule_file_path = submodule_dir / "submodule.py"
    submodule_file_path.write_text(
        """
from app.models import User, Post

def submodule_function():
    import logging
    logging.info("Hello, World!")

def other_submodule_function():
    from app.config import settings
    settings.load_config()
    return settings

def main():
    submodule_function()
    other_submodule_function()

    from app.api import api
    from app.api.routes import routes

    api.run(routes)
"""
    )

    module = PythonModule(
        path = Path("app/submodule/submodule.py"),
        module_path = "app.submodule.submodule",
    )

    parsed = parse_module(tmp_path, module)

    assert parsed.path == Path("app/submodule/submodule.py")
    assert parsed.module_path == "app.submodule.submodule"

    imports = {imp.module_name for imp in parsed.imports}

    assert imports == {
        "app.models",
        "app.config",
        "app.api",
        "app.api.routes",
        "logging",
    }

    assert len(parsed.imports) == 5
