from backend.app.config.models import Configuration, IgnoreConfig

DEFAULT_IGNORED_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        "migrations",
        "alembic",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    }
)

DEFAULT_IGNORED_PATHS = frozenset(
    {
        "alembic/versions",
    }
)

DEFAULT_IGNORED_MODULES = frozenset(
    {
        "tests",
        "tests.*",
    }
)

DEFAULT_CONFIGURATION = Configuration(
    entry_points=(),
    ignore=IgnoreConfig(
        directories=tuple(sorted(DEFAULT_IGNORED_DIRS)),
        modules=tuple(sorted(DEFAULT_IGNORED_MODULES)),
        paths=tuple(sorted(DEFAULT_IGNORED_PATHS)),
    ),
)
