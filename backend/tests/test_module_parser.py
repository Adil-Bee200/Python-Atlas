from pathlib import Path
from backend.app.parser.module_parser import parse_module
from backend.app.models.scan_models import PythonModule

def test_parse_module_extracts_top_level_imports(tmp_path):
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