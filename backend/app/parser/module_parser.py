from pathlib import Path
from backend.app.models.import_models import ParsedModule, ParsedImport, ParsedResult
from backend.app.models.scan_models import ScanResult, PythonModule
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
        # One `from X import ...` statement should produce one ParsedImport per module,
        # regardless of how many names are imported from that module.
        module_name = node.module or ""
        if module_name == "__future__":
            return

        imported_names = ", ".join(alias.name for alias in node.names)
        self.imports.append(
            ParsedImport(
                raw_import=f"from {module_name} import {imported_names}",
                module_name=module_name,
            )
        )



def parse_module(repo_root: Path, module: PythonModule) -> ParsedModule:
    full_path = repo_root / module.path

    source = full_path.read_text(encoding="utf-8")

    try:
        tree = ast.parse(source)
    except Exception as e:
        return ParsedModule(
            path=module.path,
            module_path=module.module_path,
            imports=tuple(),
            error=e,
        )

    tree = ast.parse(source)

    visitor = ImportVisitor()
    visitor.visit(tree)

    return ParsedModule(
        path=module.path,
        module_path=module.module_path,
        imports=tuple(visitor.imports),
    )

def parse_all_modules(scan_result: ScanResult) -> ParsedResult:
    modules = tuple(
        parse_module(scan_result.repo_root, module)
        for module in scan_result.modules
    )
    return ParsedResult(repo_root=scan_result.repo_root, modules=modules)