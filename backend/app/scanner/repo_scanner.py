""" 
Input: local repo path
Output: list of Python modules/files

Goal is to scan a local repo and return a list of Python modules/files that can be imported.
Scanning and parsing should not be done together, but rather in two separate steps. The first step is to scan the repo and return a list of Python files. 
The second step is to parse the Python files and return a list of Python modules.
"""

import os
from pathlib import Path
from backend.app.config.ignore_rules import DEFAULT_IGNORED_DIRS, DEFAULT_IGNORED_PATHS
import sys

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

def is_ignored_path(relative_path: Path) -> bool:
    posix = relative_path.as_posix()
    return any(
        posix == ignored or posix.startswith(f"{ignored}/")
        for ignored in DEFAULT_IGNORED_PATHS
    )

def scan_repo(repo_path: Path) -> ScanResult:
    modules_found = []

    for dirpath, dirnames, filenames in os.walk(repo_path):
        current_rel = Path(dirpath).relative_to(repo_path)

        if is_ignored_path(current_rel):
            dirnames.clear()
            continue

        dirnames[:] = [
            d for d in dirnames
            if d not in DEFAULT_IGNORED_DIRS and not is_ignored_path(current_rel / d)
        ]

        for filename in filenames:
            if not filename.endswith(".py"):
                continue

            full_path = Path(dirpath) / filename
            relative_path = full_path.relative_to(repo_path)

            if is_ignored_path(relative_path):
                continue

            module_path = convert_to_module_path(relative_path)
            modules_found.append(PythonModule(path=relative_path, module_path=module_path))

    return ScanResult(repo_root=repo_path, modules=tuple(modules_found)) # convert to tuple to make it immutable


if __name__ == "__main__":
    
    # parse path argument 

    if len(sys.argv) < 2:
        print("No path provided")
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("Too many arguments")
        sys.exit(1)
    else:
        user_input = sys.argv[1]
        repo_path = Path(user_input).expanduser().resolve()

        try:
            verify_repo_path(repo_path)
        except (FileNotFoundError, NotADirectoryError) as e:
            print(f"Invalid repository path: {e}")
            sys.exit(1)
        
        scan_result = scan_repo(repo_path)

        print(f"Scanning repository: {repo_path}")
        print(f"Found {len(scan_result.modules)} modules")
        for module in scan_result.modules:
            print(f"{module.path}")
            print(f"    -> {module.module_path}")
        
        sys.exit(0)
        
