from __future__ import annotations

import ast
from pathlib import Path


def bound_names(tree: ast.Module) -> dict[str, str]:
    """Nombre local (tras import/alias) -> nombre de módulo top-level."""
    bindings: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                local = alias.asname or alias.name.split(".")[0]
                bindings[local] = top
        elif isinstance(node, ast.ImportFrom):
            if node.module is None or node.level > 0:
                continue  # import relativo -- no es un paquete externo
            top = node.module.split(".")[0]
            for alias in node.names:
                local = alias.asname or alias.name
                bindings[local] = top
    return bindings


def count_usages_per_name(tree: ast.Module, local_names: set[str]) -> dict[str, int]:
    """Cuenta referencias reales (no la propia línea de import) a cada nombre."""
    counts: dict[str, int] = dict.fromkeys(local_names, 0)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id in counts:
            counts[node.id] += 1
    return counts


def analyze_file(path: Path) -> tuple[dict[str, str], dict[str, int]] | None:
    """(nombre local -> módulo, nombre local -> nº de usos) o None si no se pudo leer/parsear."""
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, UnicodeDecodeError, SyntaxError):
        return None
    bindings = bound_names(tree)
    if not bindings:
        return ({}, {})
    counts = count_usages_per_name(tree, set(bindings))
    return (bindings, counts)
