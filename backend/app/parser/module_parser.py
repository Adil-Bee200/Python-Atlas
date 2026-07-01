from pathlib import Path
from backend.app.models.import_models import ParsedModule, ParsedImport, ParsedResult
from backend.app.models.scan_models import ScanResult

def parse_module(module_path: Path) -> ParsedModule:
    # TODO: Reads one module and returns a ParsedModule object
    
    return ParsedModule(path= module_path, module_path= module_path.module_path, imports= tuple())

def parse_all_modules(scan_result: ScanResult) -> ParsedResult:
    # TODO: Reads all modules in the scan result and returns a ParsedResult object

    return ParsedResult(repo_root= scan_result.repo_root, modules= tuple())
