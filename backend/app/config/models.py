from dataclasses import dataclass, field

@dataclass(frozen=True)
class ArchitectureLayer:
    name: str
    module_patterns: tuple[str, ...] = ()
    allowed_dependencies: tuple[str, ...] = ()


@dataclass(frozen=True)
class ArchitectureConfig:
    layers: tuple[ArchitectureLayer, ...]

@dataclass(frozen=True)
class IgnoreConfig:
    directories: tuple[str, ...] = ()
    modules: tuple[str, ...] = ()
    paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class Configuration:
    ignore: IgnoreConfig = field(default_factory=IgnoreConfig)
    entry_points: tuple[str, ...] = ()
    architecture: ArchitectureConfig | None = None