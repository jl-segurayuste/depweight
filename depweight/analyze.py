from __future__ import annotations

import subprocess
from pathlib import Path

from pydantic import BaseModel

from depweight.deps import declared_packages, import_candidates
from depweight.usage import analyze_file

# Las carga otra dependencia por dentro: no se importan nunca y aun así hacen falta. Antes salían
# con "0 usos" y quitarlas rompía la aplicación (sin itsdangerous no hay SessionMiddleware, sin
# python-multipart no hay Form()).
IMPLIED_BY: dict[str, set[str]] = {
    "python-multipart": {"fastapi", "starlette"},       # formularios y subidas
    "itsdangerous": {"fastapi", "starlette", "flask"},   # sesiones firmadas
    "jinja2": {"fastapi", "starlette", "flask"},         # plantillas
    "uvicorn": {"fastapi", "starlette"},                 # servidor ASGI
    "gunicorn": {"flask", "django", "fastapi"},
    "psycopg2": {"sqlalchemy", "django"},
    "psycopg2-binary": {"sqlalchemy", "django"},
    "psycopg": {"sqlalchemy", "django"},
    "asyncpg": {"sqlalchemy"},
    "pymysql": {"sqlalchemy"},
    "aiosqlite": {"sqlalchemy"},
    "email-validator": {"pydantic"},                     # EmailStr
    "pyyaml": {"uvicorn"},
}


class DependencyUsage(BaseModel):
    package: str
    import_names: list[str]
    usage_count: int
    files: list[str]
    narrow: bool
    implied_by: list[str] = []


def _tracked_python_files(repo_path: Path) -> list[Path] | None:
    """None si `git ls-files` no pudo ejecutarse (no es un repo git) --
    distinto de una lista vacía real, para no confundir "no pude mirar" con
    "no hay ningún .py", que llevaría a marcar cualquier dependencia como
    "0 usos" de forma enganosa.
    """
    result = subprocess.run(
        ["git", "-c", "core.quotePath=false", "ls-files", "*.py"], cwd=repo_path, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        return None
    return [repo_path / line for line in result.stdout.splitlines() if line]


def analyze_repo(repo_path: Path, *, threshold: int = 3) -> list[DependencyUsage] | None:
    """Para cada dependencia declarada, cuántos sitios reales del código la usan.

    threshold: si el nº total de usos es <= threshold, se marca "narrow" --
    candidata a revisar si de verdad hace falta la dependencia entera.
    None: no aplica (no hay dependencias declaradas, o repo_path no es un
    repo git y no se pudo determinar qué ficheros mirar).
    """
    packages = declared_packages(repo_path)
    if not packages:
        return None

    files = _tracked_python_files(repo_path)
    if files is None:
        return None

    # módulo top-level -> {fichero relativo: nº de usos en ese fichero}
    module_usage: dict[str, dict[str, int]] = {}
    for path in files:
        analyzed = analyze_file(path)
        if analyzed is None:
            continue
        bindings, counts = analyzed
        rel = str(path.relative_to(repo_path))
        for local, module in bindings.items():
            per_file = module_usage.setdefault(module, {})
            per_file[rel] = per_file.get(rel, 0) + counts.get(local, 0)

    results: list[DependencyUsage] = []
    for package in packages:
        candidates = import_candidates(package)
        total = 0
        files_using: dict[str, int] = {}
        matched: list[str] = []

        for candidate in candidates:
            top = candidate.split(".")[0]
            per_file = module_usage.get(top)
            if per_file is None:
                continue
            matched.append(candidate)
            for rel, count in per_file.items():
                files_using[rel] = files_using.get(rel, 0) + count
                total += count

        results.append(
            DependencyUsage(
                package=package,
                import_names=matched or candidates,
                usage_count=total,
                files=sorted(f for f, c in files_using.items() if c > 0),
                narrow=total <= threshold,
            )
        )

    used = {r.package.lower().replace("_", "-") for r in results if r.usage_count > 0}
    for r in results:
        implied = sorted(IMPLIED_BY.get(r.package.lower().replace("_", "-"), set()) & used)
        if implied:
            r.implied_by = implied
            r.narrow = False
    return results
