""" 
Input: local repo path
Output: list of Python modules/files
"""

import os
from pathlib import Path
from backend.app.config.ignore_rules import DEFAULT_IGNORED_DIRS


@dataclass(frozen=True)
class PythonModule:
    path: Path
    module_path: str # e.g. "backend.app.scanner.repo_scanner" basically a python import path

@dataclass
class ScanResult:
    repo_root: Path
    modules: list[PythonModule]
    
