from pathlib import Path

import pytest

from backend.app.config.defaults import DEFAULT_CONFIGURATION, DEFAULT_IGNORED_DIRS
from backend.app.config.loader import ConfigOverrides, load_config
from backend.app.config.models import Configuration, IgnoreConfig
from backend.app.main import overrides_from_args, parse_args


def test_load_config_none_returns_defaults():
    config = load_config(None)

    assert config == DEFAULT_CONFIGURATION
    assert config.entry_points == ()
    assert set(config.ignore.directories) >= DEFAULT_IGNORED_DIRS


def test_load_config_missing_file_returns_defaults(tmp_path: Path):
    config = load_config(tmp_path / "missing.yaml")

    assert config == DEFAULT_CONFIGURATION


def test_load_config_empty_file_returns_defaults(tmp_path: Path):
    path = tmp_path / "codeatlas.yaml"
    path.write_text("")

    assert load_config(path) == DEFAULT_CONFIGURATION


def test_load_config_flat_entry_points(tmp_path: Path):
    path = tmp_path / "codeatlas.yaml"
    path.write_text(
        "entry_points:\n"
        "  - app.main\n"
        "  - app.cli\n"
    )

    config = load_config(path)

    assert config.entry_points == ("app.main", "app.cli")
    assert set(config.ignore.directories) >= DEFAULT_IGNORED_DIRS


def test_load_config_nested_entry_points(tmp_path: Path):
    path = tmp_path / "codeatlas.yaml"
    path.write_text(
        "entry_points:\n"
        "  files:\n"
        "    - backend/app/main.py\n"
        "  modules:\n"
        "    - app.worker\n"
    )

    config = load_config(path)

    assert config.entry_points == ("backend/app/main.py", "app.worker")


def test_load_config_merges_ignore_with_defaults(tmp_path: Path):
    path = tmp_path / "codeatlas.yaml"
    path.write_text(
        "ignore:\n"
        "  directories:\n"
        "    - custom_cache\n"
        "  modules:\n"
        "    - scripts\n"
        "  paths:\n"
        "    - vendor/legacy\n"
    )

    config = load_config(path)

    assert "custom_cache" in config.ignore.directories
    assert ".venv" in config.ignore.directories
    assert "scripts" in config.ignore.modules
    assert "tests" in config.ignore.modules
    assert "vendor/legacy" in config.ignore.paths
    assert "alembic/versions" in config.ignore.paths


def test_load_config_dedupes_ignore_entries(tmp_path: Path):
    path = tmp_path / "codeatlas.yaml"
    path.write_text(
        "ignore:\n"
        "  directories:\n"
        "    - .venv\n"
        "    - .venv\n"
        "    - custom\n"
    )

    config = load_config(path)

    assert config.ignore.directories.count(".venv") == 1
    assert config.ignore.directories.count("custom") == 1


def test_load_config_rejects_unknown_keys(tmp_path: Path):
    path = tmp_path / "codeatlas.yaml"
    path.write_text("foo: 1\n")

    with pytest.raises(ValueError, match="Unknown config keys"):
        load_config(path)


def test_load_config_rejects_invalid_entry_points(tmp_path: Path):
    path = tmp_path / "codeatlas.yaml"
    path.write_text("entry_points: not-a-list\n")

    with pytest.raises(ValueError, match="entry_points"):
        load_config(path)


def test_load_config_returns_frozen_configuration(tmp_path: Path):
    path = tmp_path / "codeatlas.yaml"
    path.write_text("entry_points:\n  - app.main\n")

    config = load_config(path)

    assert isinstance(config, Configuration)
    assert isinstance(config.ignore, IgnoreConfig)
    with pytest.raises(Exception):
        config.entry_points = ("other",)  # type: ignore[misc]


def test_cli_entry_points_override_yaml(tmp_path: Path):
    path = tmp_path / "codeatlas.yaml"
    path.write_text(
        "entry_points:\n"
        "  - app.main\n"
        "ignore:\n"
        "  directories:\n"
        "    - custom_cache\n"
    )

    config = load_config(
        path,
        overrides=ConfigOverrides(entry_points=("app.cli", "app.worker")),
    )

    assert config.entry_points == ("app.cli", "app.worker")
    assert "custom_cache" in config.ignore.directories


def test_cli_ignore_dirs_override_yaml_but_keep_defaults(tmp_path: Path):
    path = tmp_path / "codeatlas.yaml"
    path.write_text(
        "ignore:\n"
        "  directories:\n"
        "    - from_yaml\n"
    )

    config = load_config(
        path,
        overrides=ConfigOverrides(ignore_directories=("from_cli",)),
    )

    assert "from_cli" in config.ignore.directories
    assert "from_yaml" not in config.ignore.directories
    assert ".venv" in config.ignore.directories


def test_cli_partial_override_leaves_other_yaml_fields(tmp_path: Path):
    path = tmp_path / "codeatlas.yaml"
    path.write_text(
        "entry_points:\n"
        "  - app.main\n"
        "ignore:\n"
        "  modules:\n"
        "    - scripts\n"
        "  paths:\n"
        "    - vendor/legacy\n"
    )

    config = load_config(
        path,
        overrides=ConfigOverrides(ignore_modules=("jobs",)),
    )

    assert config.entry_points == ("app.main",)
    assert "jobs" in config.ignore.modules
    assert "scripts" not in config.ignore.modules
    assert "vendor/legacy" in config.ignore.paths
    assert "tests" in config.ignore.modules


def test_overrides_from_args_none_when_flags_absent():
    args = parse_args(["some/repo", "--config", "codeatlas.yaml"])
    overrides = overrides_from_args(args)

    assert overrides.entry_points is None
    assert overrides.ignore_directories is None
    assert overrides.ignore_modules is None
    assert overrides.ignore_paths is None


def test_overrides_from_args_captures_repeatable_flags():
    args = parse_args(
        [
            "some/repo",
            "--entry-point",
            "app.main",
            "--entry-point",
            "app.cli",
            "--ignore-dir",
            "build",
            "--ignore-module",
            "scripts",
            "--ignore-path",
            "vendor/old",
        ]
    )
    overrides = overrides_from_args(args)

    assert overrides.entry_points == ("app.main", "app.cli")
    assert overrides.ignore_directories == ("build",)
    assert overrides.ignore_modules == ("scripts",)
    assert overrides.ignore_paths == ("vendor/old",)
