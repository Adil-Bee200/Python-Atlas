from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import yaml

from backend.app.config.defaults import DEFAULT_CONFIGURATION
from backend.app.config.models import (
    ArchitectureConfig,
    ArchitectureLayer,
    Configuration,
    IgnoreConfig,
)


@dataclass(frozen=True)
class ConfigOverrides:
    """Optional CLI overrides. ``None`` means “leave YAML/defaults as-is”."""

    entry_points: tuple[str, ...] | None = None
    architecture: ArchitectureConfig | None = None
    ignore_directories: tuple[str, ...] | None = None
    ignore_modules: tuple[str, ...] | None = None
    ignore_paths: tuple[str, ...] | None = None


def _as_str_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"Config field '{field_name}' must be a list of strings")
    items: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"Config field '{field_name}' must be a list of strings")
        items.append(item)
    return tuple(items)


def _dedupe(items: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(items))


def _parse_entry_points(raw: Any) -> tuple[str, ...]:
    if raw is None:
        return ()
    if isinstance(raw, list):
        return _as_str_tuple(raw, "entry_points")
    if isinstance(raw, dict):
        files = _as_str_tuple(raw.get("files"), "entry_points.files")
        modules = _as_str_tuple(raw.get("modules"), "entry_points.modules")
        unknown = set(raw) - {"files", "modules"}
        if unknown:
            raise ValueError(
                f"Unknown entry_points keys: {', '.join(sorted(unknown))}"
            )
        return files + modules
    raise ValueError(
        "Config field 'entry_points' must be a list of strings "
        "or a mapping with 'files' / 'modules'"
    )


def _parse_architecture_layer(name: str, raw: Any) -> ArchitectureLayer:
    if not isinstance(raw, dict):
        raise ValueError(
            f"Config field 'architecture.layers.{name}' must be a mapping"
        )

    unknown = set(raw) - {"patterns", "may_depend_on"}
    if unknown:
        raise ValueError(
            f"Unknown architecture.layers.{name} keys: "
            f"{', '.join(sorted(unknown))}"
        )

    return ArchitectureLayer(
        name=name,
        module_patterns=_as_str_tuple(
            raw.get("patterns"), f"architecture.layers.{name}.patterns"
        ),
        allowed_dependencies=_as_str_tuple(
            raw.get("may_depend_on"),
            f"architecture.layers.{name}.may_depend_on",
        ),
    )


def _parse_architecture(raw: Any) -> ArchitectureConfig:
    if raw is None:
        return DEFAULT_CONFIGURATION.architecture
    if not isinstance(raw, dict):
        raise ValueError("Config field 'architecture' must be a mapping")

    unknown = set(raw) - {"layers"}
    if unknown:
        raise ValueError(
            f"Unknown architecture keys: {', '.join(sorted(unknown))}"
        )

    layers_raw = raw.get("layers")
    if layers_raw is None:
        return ArchitectureConfig()
    if not isinstance(layers_raw, dict):
        raise ValueError("Config field 'architecture.layers' must be a mapping")

    layers: list[ArchitectureLayer] = []
    for name, layer_raw in layers_raw.items():
        if not isinstance(name, str):
            raise ValueError("Architecture layer names must be strings")
        layers.append(_parse_architecture_layer(name, layer_raw))

    architecture = ArchitectureConfig(layers=tuple(layers))
    _validate_architecture(architecture)
    return architecture


def _validate_architecture(architecture: ArchitectureConfig) -> None:
    layer_names = {layer.name for layer in architecture.layers}
    for layer in architecture.layers:
        for allowed_dependency in layer.allowed_dependencies:
            if allowed_dependency not in layer_names:
                raise ValueError(
                    f"Configuration Error: Layer {layer.name} depends on "
                    f"undefined layer {allowed_dependency}"
                )


def _merge_ignore(user_ignore: Any) -> IgnoreConfig:
    defaults = DEFAULT_CONFIGURATION.ignore
    if user_ignore is None:
        return defaults
    if not isinstance(user_ignore, dict):
        raise ValueError("Config field 'ignore' must be a mapping")

    unknown = set(user_ignore) - {"directories", "modules", "paths"}
    if unknown:
        raise ValueError(f"Unknown ignore keys: {', '.join(sorted(unknown))}")

    directories = defaults.directories + _as_str_tuple(
        user_ignore.get("directories"), "ignore.directories"
    )
    modules = defaults.modules + _as_str_tuple(
        user_ignore.get("modules"), "ignore.modules"
    )
    paths = defaults.paths + _as_str_tuple(user_ignore.get("paths"), "ignore.paths")

    return IgnoreConfig(
        directories=_dedupe(directories),
        modules=_dedupe(modules),
        paths=_dedupe(paths),
    )


def _build_configuration(raw: Any) -> Configuration:
    if raw is None:
        return DEFAULT_CONFIGURATION
    if not isinstance(raw, dict):
        raise ValueError("Config root must be a mapping")

    unknown = set(raw) - {"entry_points", "ignore", "architecture"}
    if unknown:
        raise ValueError(f"Unknown config keys: {', '.join(sorted(unknown))}")

    return Configuration(
        entry_points=_parse_entry_points(raw.get("entry_points")),
        ignore=_merge_ignore(raw.get("ignore")),
        architecture=_parse_architecture(raw.get("architecture")),
    )


def apply_overrides(
    config: Configuration,
    overrides: ConfigOverrides,
) -> Configuration:
    """Apply CLI overrides on top of a loaded configuration.

    Precedence: built-in defaults < YAML < CLI.
    Any override field that is not ``None`` replaces the YAML value for that field.
    Ignore lists still keep built-in defaults and then use the CLI list instead of YAML.
    """
    entry_points = (
        overrides.entry_points
        if overrides.entry_points is not None
        else config.entry_points
    )

    defaults = DEFAULT_CONFIGURATION.ignore
    directories = (
        _dedupe(defaults.directories + overrides.ignore_directories)
        if overrides.ignore_directories is not None
        else config.ignore.directories
    )
    modules = (
        _dedupe(defaults.modules + overrides.ignore_modules)
        if overrides.ignore_modules is not None
        else config.ignore.modules
    )
    paths = (
        _dedupe(defaults.paths + overrides.ignore_paths)
        if overrides.ignore_paths is not None
        else config.ignore.paths
    )
    architecture = (
        overrides.architecture
        if overrides.architecture is not None
        else config.architecture
    )

    return replace(
        config,
        entry_points=entry_points,
        ignore=IgnoreConfig(directories=directories, modules=modules, paths=paths),
        architecture=architecture,
    )


def load_config(
    config_path: str | Path | None = None,
    *,
    overrides: ConfigOverrides | None = None,
) -> Configuration:
    """Load configuration from YAML, then apply optional CLI overrides.

    If ``config_path`` is None or the file does not exist, starts from
    ``DEFAULT_CONFIGURATION``. CLI ``overrides`` always win over YAML.
    """
    if config_path is None:
        config = DEFAULT_CONFIGURATION
    else:
        path = Path(config_path)
        if not path.exists():
            config = DEFAULT_CONFIGURATION
        else:
            with path.open("r", encoding="utf-8") as f:
                raw = yaml.safe_load(f)
            config = _build_configuration(raw)

    if overrides is not None:
        config = apply_overrides(config, overrides)
        _validate_architecture(config.architecture)

    return config
