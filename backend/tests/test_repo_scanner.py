from pathlib import Path
import pytest
from backend.app.scanner.repo_scanner import scan_repo, PythonModule, ScanResult

@pytest.fixture
def create_test_repo(tmp_path: Path) -> Path:
    """Create a test repository with sample Python files."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    (repo_path / "__init__.py").touch()
    (repo_path / "module1.py").write_text("print('Hello, World!')")
    (repo_path / "module2.py").write_text("print('Hello, World!')")
    (repo_path / "app").mkdir()
    (repo_path / "app" / "main.py").write_text("print('Hello, World!')")
    (repo_path / "app" / "__init__.py").touch()
    (repo_path / "README.md").write_text("# docs")
    return repo_path


def test_scan_repo_finds_python_files(create_test_repo: Path):
    result = scan_repo(create_test_repo)

    paths = {module.path for module in result.modules}
    module_paths = {module.module_path for module in result.modules}

    assert paths == {
        Path("module1.py"),
        Path("module2.py"),
        Path("app/main.py"),
        Path("app/__init__.py"),
        Path("__init__.py"),
    }

    assert module_paths == {
        "module1",
        "module2",
        "app.main",
        "app",
        ""
    }
