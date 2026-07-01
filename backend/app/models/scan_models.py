from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PythonModule:
    path: Path
    module_path: str # e.g. "backend.app.scanner.repo_scanner" 

@dataclass(frozen=True)
class ScanResult:
    repo_root: Path
    modules: tuple[PythonModule, ...]
