from pathlib import Path
from backend.app.models.import_models import ParsedModule, ParsedImport, ParsedResult
from backend.app.models.scan_models import ScanResult
import ast 

class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports : list[ParsedImport] = []
    
    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(
                ParsedImport(
                    raw_import=f"import {alias.name}",
                    module_name=alias.name,
                )
            )
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        for alias in node.names:
            module_name = node.module or ""
            imported_names = ", ".join(alias.name for alias in node.names)
            self.imports.append(
                ParsedImport(
                    raw_import=f"from {module_name} import {imported_names}",
                    module_name=module_name,
                )
            )



def parse_module(module_path: Path) -> ParsedModule:
    # TODO: Reads one module and returns a ParsedModule object

    return parse_module(module_path)

def parse_all_modules(scan_result: ScanResult) -> ParsedResult:
    # TODO: Reads all modules in the scan result and returns a ParsedResult object



    return ParsedResult(repo_root= scan_result.repo_root, modules= tuple())
