from __future__ import annotations

from pathlib import Path

from backend.app.models.import_models import ParsedImport, ParsedModule, ParsedResult
from backend.app.models.scan_models import PythonModule, ScanResult
import ast


def _package_parts(module_path: str, file_path: Path) -> list[str]:
    """Return the package that relative imports are resolved against."""
    parts = module_path.split(".") if module_path else []
    if file_path.name == "__init__.py":
        return parts
    return parts[:-1] if parts else []


def resolve_relative_module_name(
    *,
    current_module_path: str,
    file_path: Path,
    level: int,
    module: str | None,
) -> str | None:
    """Resolve a relative import to an absolute dotted module name.

    ``level`` is the number of leading dots (1 for ``.``, 2 for ``..``, ...).
    Returns ``None`` if the import goes beyond the top-level package.
    """
    if level <= 0:
        return module

    package_parts = _package_parts(current_module_path, file_path)
    if level > len(package_parts):
        return None

    base_parts = package_parts[: len(package_parts) - (level - 1)]
    if module:
        return ".".join(base_parts + module.split("."))
    return ".".join(base_parts)


def _format_from_import(level: int, module: str | None, imported_names: tuple[str, ...]) -> str:
    if level > 0:
        target = f"{'.' * level}{module or ''}"
    else:
        target = module or ""
    return f"from {target} import {', '.join(imported_names)}"


class ImportVisitor(ast.NodeVisitor):
    def __init__(self, current_module_path: str, file_path: Path):
        self.imports: list[ParsedImport] = []
        self.current_module_path = current_module_path
        self.file_path = file_path

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(
                ParsedImport(
                    raw_import=f"import {alias.name}",
                    module_name=alias.name,
                )
            )

    def visit_ImportFrom(self, node: ast.ImportFrom):
        level = node.level or 0
        module = node.module
        if level == 0 and module == "__future__":
            return

        imported_names = tuple(alias.name for alias in node.names)
        raw_import = _format_from_import(level, module, imported_names)

        if level > 0:
            absolute = resolve_relative_module_name(
                current_module_path=self.current_module_path,
                file_path=self.file_path,
                level=level,
                module=module,
            )
            module_name = absolute or ""
        else:
            module_name = module or ""

        self.imports.append(
            ParsedImport(
                raw_import=raw_import,
                module_name=module_name,
                imported_names=imported_names,
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

    visitor = ImportVisitor(module.module_path, module.path)
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
