from pathlib import Path

import pytest

from backend.app.config.defaults import DEFAULT_CONFIGURATION, DEFAULT_IGNORED_DIRS
from backend.app.config.models import IgnoreConfig
from backend.app.scanner.repo_scanner import scan_repo

@pytest.fixture
def create_test_repo(tmp_path: Path) -> Path:
    """Create a test repository with sample Python files."""
    repo_path = tmp_path / "test_repo"

    # create the repo directory and the app directory
    repo_path.mkdir()
    (repo_path / "app").mkdir()
    (repo_path / "app" / ".venv").mkdir()
    (repo_path / "app" / "__pycache__").mkdir()
    (repo_path / "venv").mkdir()
    (repo_path / "migrations").mkdir()
    (repo_path / ".git").mkdir()



    # create the sample files
    (repo_path / "module1.py").write_text("print('Hello, World!')")
    (repo_path / "module2.py").write_text("print('Hello, World!')")
    (repo_path / "app" / "main.py").write_text("print('Hello, World!')")

    # create files that should be ignored
    (repo_path / "__init__.py").touch()
    (repo_path / "app" / "__init__.py").touch()
    (repo_path / "README.md").write_text("# docs")
    (repo_path / "migrations" / "randomFile.py").touch()
    (repo_path / ".gitignore").write_text("*.pyc")

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



def test_scan_repo_ignores_ignored_dirs(create_test_repo: Path):
    result = scan_repo(create_test_repo)

    paths = {module.path for module in result.modules}
    module_paths = {module.module_path for module in result.modules}

    assert Path("app/.venv") not in paths
    assert Path("app/__pycache__") not in paths
    assert Path("README.md") not in paths
    assert Path("migrations/randomFile.py") not in paths
    assert Path(".gitignore") not in paths
    assert Path(".git") not in paths
    
    assert "app._venv" not in module_paths
    assert "app.__pycache__" not in module_paths
    assert "README" not in module_paths
    assert "migrations.randomFile" not in module_paths
    assert ".gitignore" not in module_paths
    assert ".git" not in module_paths

def test_scan_repo_ignores_ignored_paths(create_test_repo: Path):
    alembic_dir = create_test_repo / "alembic"
    versions_dir = alembic_dir / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)
    (alembic_dir / "env.py").write_text("print('env')")
    (versions_dir / "001_initial.py").write_text("print('migration')")

    # Allow scanning alembic/ itself while still ignoring alembic/versions.
    ignore = IgnoreConfig(
        directories=tuple(sorted(DEFAULT_IGNORED_DIRS - {"alembic"})),
        modules=DEFAULT_CONFIGURATION.ignore.modules,
        paths=DEFAULT_CONFIGURATION.ignore.paths,
    )
    result = scan_repo(create_test_repo, ignore=ignore)
    paths = {module.path for module in result.modules}

    assert Path("alembic/env.py") in paths
    assert Path("alembic/versions/001_initial.py") not in paths


def test_scan_repo_ignores_module_patterns(create_test_repo: Path):
    tests_dir = create_test_repo / "tests"
    tests_dir.mkdir()
    (tests_dir / "__init__.py").write_text("")
    (tests_dir / "test_app.py").write_text("assert True\n")

    result = scan_repo(create_test_repo)
    module_paths = {module.module_path for module in result.modules}

    assert "tests" not in module_paths
    assert "tests.test_app" not in module_paths
    assert "app.main" in module_paths