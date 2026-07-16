"""
Input: local repo path
Output: list of Python modules/files

Goal is to scan a local repo and return a list of Python modules/files that can be imported.
Scanning and parsing should not be done together, but rather in two separate steps. The first
step is to scan the repo and return a list of Python files. The second step is to parse the
Python files and return a list of Python modules.
"""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path

from backend.app.config.defaults import DEFAULT_CONFIGURATION
from backend.app.config.models import IgnoreConfig
from backend.app.models.scan_models import PythonModule, ScanResult


def verify_repo_path(repo_path: Path) -> bool:
    if not repo_path.exists():
        raise FileNotFoundError(f"Path does not exist: {repo_path}")
    if not repo_path.is_dir():
        raise NotADirectoryError(f"Expected a directory: {repo_path}")

    return True


def convert_to_module_path(relative_path: Path) -> str:
    if relative_path.name == "__init__.py":
        module_parts = relative_path.parent.parts
    else:
        module_parts = relative_path.with_suffix("").parts

    return ".".join(module_parts)


def is_ignored_path(relative_path: Path, ignored_paths: frozenset[str] | set[str]) -> bool:
    posix = relative_path.as_posix()
    if posix in (".", ""):
        return False
    return any(
        posix == ignored or posix.startswith(f"{ignored}/")
        for ignored in ignored_paths
    )


def is_ignored_module(module_path: str, patterns: tuple[str, ...]) -> bool:
    if not module_path or not patterns:
        return False
    return any(fnmatch.fnmatch(module_path, pattern) for pattern in patterns)


def scan_repo(
    repo_path: Path,
    ignore: IgnoreConfig | None = None,
) -> ScanResult:
    ignore = ignore if ignore is not None else DEFAULT_CONFIGURATION.ignore
    ignored_dirs = frozenset(ignore.directories)
    ignored_paths = frozenset(ignore.paths)
    modules_found: list[PythonModule] = []

    for dirpath, dirnames, filenames in os.walk(repo_path):
        current_rel = Path(dirpath).relative_to(repo_path)

        if is_ignored_path(current_rel, ignored_paths):
            dirnames.clear()
            continue

        dirnames[:] = [
            d
            for d in dirnames
            if d not in ignored_dirs
            and not is_ignored_path(current_rel / d, ignored_paths)
        ]

        for filename in filenames:
            if not filename.endswith(".py"):
                continue

            full_path = Path(dirpath) / filename
            relative_path = full_path.relative_to(repo_path)

            if is_ignored_path(relative_path, ignored_paths):
                continue

            dotted_path = convert_to_module_path(relative_path)
            if is_ignored_module(dotted_path, ignore.modules):
                continue

            modules_found.append(
                PythonModule(path=relative_path, module_path=dotted_path)
            )

    return ScanResult(repo_root=repo_path, modules=tuple(modules_found))
