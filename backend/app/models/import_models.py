from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ParsedImport:
    raw_import: str # e.g. "from backend.app.scanner.repo_scanner import scan_repo"
    module_name: str # e.g. "backend.app.scanner.repo_scanner"

@dataclass(frozen=True)
class ParsedModule:
    path: Path # e.g. "backend/app/scanner/repo_scanner.py"
    module_path: str # e.g. "backend.app.scanner.repo_scanner"
    imports: tuple[ParsedImport, ...]
    error: Optional[str] = None

@dataclass(frozen=True)
class ParsedResult:
    repo_root: Path
    modules: tuple[ParsedModule, ...]