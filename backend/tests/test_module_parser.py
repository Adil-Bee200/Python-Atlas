from pathlib import Path
from backend.app.parser.module_parser import parse_module, parse_all_modules
from backend.app.models.scan_models import PythonModule, ScanResult

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
    models_import = next(imp for imp in parsed.imports if imp.module_name == "app.models")
    assert models_import.imported_names == ("User", "Post")

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

    assert parsed.error is None
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

    assert parsed.error is None
    assert len(parsed.imports) == 5

def test_parse_module_empty_module(tmp_path):
    ## test: an empty module
    app_dir = tmp_path / "app"
    app_dir.mkdir()

    file_path = app_dir / "main.py"
    file_path.write_text("")

    module = PythonModule(
        path = Path("app/main.py"),
        module_path = "app.main",
    )

    parsed = parse_module(tmp_path, module)

    assert parsed.path == Path("app/main.py")
    assert parsed.module_path == "app.main"
    assert parsed.error is None

    assert len(parsed.imports) == 0

def test_parse_module_invalid_syntax(tmp_path):
    ## test: an invalid syntax module
    app_dir = tmp_path / "app"
    app_dir.mkdir()

    file_path = app_dir / "main.py"
    file_path.write_text("""
    import sys 
    print( # invalid syntax
    """)

    module = PythonModule(
        path = Path("app/main.py"),
        module_path = "app.main",
    )

    parsed = parse_module(tmp_path, module)

    assert parsed.path == Path("app/main.py")
    assert parsed.module_path == "app.main"
    assert parsed.error is not None
    assert isinstance(parsed.error, SyntaxError)


def test_parse_module_no_imports(tmp_path):
    ## test: a module that has no imports
    app_dir = tmp_path / "app"
    app_dir.mkdir()

    file_path = app_dir / "main.py"
    file_path.write_text("""
def main():
    print("Hello, World!")

def other_function():
    x = 1
    y = 2
    return x + y

def other_function_2():
    other_function()
    """)

    module = PythonModule(
        path = Path("app/main.py"),
        module_path = "app.main",
    )

    parsed = parse_module(tmp_path, module)

    assert parsed.path == Path("app/main.py")
    assert parsed.module_path == "app.main"
    assert parsed.error is None
    assert len(parsed.imports) == 0


def test_parse_all_modules_parses_scan_result(tmp_path):
    app_dir = tmp_path / "app"
    app_dir.mkdir()

    (app_dir / "main.py").write_text("import os\nfrom app.config import settings\n")
    (app_dir / "config.py").write_text("from pathlib import Path\n")
    (app_dir / "broken.py").write_text("import sys\nprint(\n")

    scan_result = ScanResult(
        repo_root=tmp_path,
        modules=(
            PythonModule(path=Path("app/main.py"), module_path="app.main"),
            PythonModule(path=Path("app/config.py"), module_path="app.config"),
            PythonModule(path=Path("app/broken.py"), module_path="app.broken"),
        ),
    )

    parsed_result = parse_all_modules(scan_result)

    assert parsed_result.repo_root == tmp_path
    assert len(parsed_result.modules) == 3

    parsed_by_path = {module.path: module for module in parsed_result.modules}

    main = parsed_by_path[Path("app/main.py")]
    config = parsed_by_path[Path("app/config.py")]
    broken = parsed_by_path[Path("app/broken.py")]

    assert main.error is None
    assert {imp.module_name for imp in main.imports} == {"os", "app.config"}

    assert config.error is None
    assert {imp.module_name for imp in config.imports} == {"pathlib"}

    assert broken.error is not None
    assert broken.imports == ()


def test_parse_module_ignores_future_import_only(tmp_path):
    app_dir = tmp_path / "app"
    app_dir.mkdir()

    (app_dir / "main.py").write_text("from __future__ import annotations\n")

    module = PythonModule(path=Path("app/main.py"), module_path="app.main")
    parsed = parse_module(tmp_path, module)

    assert parsed.error is None
    assert parsed.imports == ()


def test_parse_module_ignores_future_import_with_regular_imports(tmp_path):
    app_dir = tmp_path / "app"
    app_dir.mkdir()

    (app_dir / "main.py").write_text(
        "from __future__ import annotations\n"
        "import os\n"
        "from pathlib import Path\n"
    )

    module = PythonModule(path=Path("app/main.py"), module_path="app.main")
    parsed = parse_module(tmp_path, module)

    assert parsed.error is None
    assert {imp.module_name for imp in parsed.imports} == {"os", "pathlib"}
    assert len(parsed.imports) == 2


def test_parse_module_ignores_multiple_future_import_names(tmp_path):
    app_dir = tmp_path / "app"
    app_dir.mkdir()

    (app_dir / "main.py").write_text(
        "from __future__ import annotations, print_function\n"
        "import sys\n"
    )

    module = PythonModule(path=Path("app/main.py"), module_path="app.main")
    parsed = parse_module(tmp_path, module)

    assert parsed.error is None
    assert {imp.module_name for imp in parsed.imports} == {"sys"}
    assert len(parsed.imports) == 1

def test_parse_multiple_imports_same_line(tmp_path):
    app_dir = tmp_path / "app"
    app_dir.mkdir()

    (app_dir / "main.py").write_text("""
from app.models import User, Post
from app.config import settings
import logging, pydantic, sys, pytest
import app.submodule.submodule_function as submodule_function
""")

    module = PythonModule(path=Path("app/main.py"), module_path="app.main")
    parsed = parse_module(tmp_path, module)
    imports = {imp.module_name for imp in parsed.imports}

    assert parsed.error is None
    assert imports == {
        "app.models",
        "app.config",
        "logging",
        "pydantic",
        "sys",
        "pytest",
        "app.submodule.submodule_function",
    }
    assert len(parsed.imports) == 7

def test_parse_raw_import_is_preserved(tmp_path):
    app_dir = tmp_path / "app"
    app_dir.mkdir()

    (app_dir / "main.py").write_text("""
from app.models import User, Post
from app.config import settings
import logging, pydantic, sys, pytest
import app.submodule.submodule_function as submodule_function
""")

    module = PythonModule(path=Path("app/main.py"), module_path="app.main")
    parsed = parse_module(tmp_path, module)
    raw_imports = {imp.raw_import for imp in parsed.imports}

    assert parsed.error is None

    assert raw_imports == {
        "from app.models import User, Post",
        "from app.config import settings",
        "import logging",
        "import pydantic",
        "import sys",
        "import pytest",
        "import app.submodule.submodule_function",
    }
    assert len(parsed.imports) == 7

def test_parse_relative_import_same_package(tmp_path):
    app_dir = tmp_path / "app" / "api"
    app_dir.mkdir(parents=True)
    (app_dir / "router.py").write_text(
        "from .routes import alerts, summary\n"
        "from . import deps\n"
    )

    module = PythonModule(path=Path("app/api/router.py"), module_path="app.api.router")
    parsed = parse_module(tmp_path, module)

    by_raw = {imp.raw_import: imp for imp in parsed.imports}
    routes_imp = by_raw["from .routes import alerts, summary"]
    deps_imp = by_raw["from . import deps"]

    assert routes_imp.module_name == "app.api.routes"
    assert routes_imp.imported_names == ("alerts", "summary")
    assert deps_imp.module_name == "app.api"
    assert deps_imp.imported_names == ("deps",)


def test_parse_relative_import_parent_package(tmp_path):
    app_dir = tmp_path / "app" / "api"
    app_dir.mkdir(parents=True)
    (app_dir / "router.py").write_text("from ..core.config import settings\n")

    module = PythonModule(path=Path("app/api/router.py"), module_path="app.api.router")
    parsed = parse_module(tmp_path, module)

    assert len(parsed.imports) == 1
    imp = parsed.imports[0]
    assert imp.raw_import == "from ..core.config import settings"
    assert imp.module_name == "app.core.config"
    assert imp.imported_names == ("settings",)


def test_parse_relative_import_in_package_init(tmp_path):
    app_dir = tmp_path / "app" / "api"
    app_dir.mkdir(parents=True)
    (app_dir / "__init__.py").write_text("from .router import api_router\n")

    module = PythonModule(path=Path("app/api/__init__.py"), module_path="app.api")
    parsed = parse_module(tmp_path, module)

    assert parsed.imports[0].module_name == "app.api.router"
    assert parsed.imports[0].raw_import == "from .router import api_router"


def test_parse_relative_import_beyond_top_level(tmp_path):
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "main.py").write_text("from ....outside import x\n")

    module = PythonModule(path=Path("app/main.py"), module_path="app.main")
    parsed = parse_module(tmp_path, module)

    assert parsed.imports[0].raw_import == "from ....outside import x"
    assert parsed.imports[0].module_name == ""
