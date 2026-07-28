from __future__ import annotations

import tomllib
from pathlib import Path

from packaging.requirements import InvalidRequirement, Requirement

# Nombre de paquete en PyPI -> nombre(s) de import mas probable(s), para los
# casos donde no coinciden simplemente normalizando guiones/mayusculas.
PACKAGE_TO_IMPORT: dict[str, list[str]] = {
    "pyyaml": ["yaml"],
    "beautifulsoup4": ["bs4"],
    "pillow": ["PIL"],
    "opencv-python": ["cv2"],
    "scikit-learn": ["sklearn"],
    "python-dotenv": ["dotenv"],
    "pyjwt": ["jwt"],
    "python-dateutil": ["dateutil"],
    "pycryptodome": ["Crypto"],
    "pyopenssl": ["OpenSSL"],
    "python-docx": ["docx"],
    "python-pptx": ["pptx"],
    "pyserial": ["serial"],
    "pyusb": ["usb"],
    "markdown-it-py": ["markdown_it"],
    "protobuf": ["google.protobuf"],
    "grpcio": ["grpc"],
}


def _parse_requirement_line(line: str) -> Requirement | None:
    line = line.split("#", 1)[0].strip()
    if not line or line.startswith("-"):
        return None
    try:
        return Requirement(line)
    except InvalidRequirement:
        return None


def _declared_names_from_requirements_txt(path: Path) -> list[str]:
    if not path.exists():
        return []
    names = []
    for line in path.read_text(encoding="utf-8").splitlines():
        req = _parse_requirement_line(line)
        if req is not None:
            names.append(req.name)
    return names


def _declared_names_from_pyproject_toml(path: Path) -> list[str]:
    if not path.exists():
        return []
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError:
        return []
    project = data.get("project", {})
    names = []
    for line in project.get("dependencies", []):
        req = _parse_requirement_line(line)
        if req is not None:
            names.append(req.name)
    return names


def declared_packages(repo_path: Path) -> list[str]:
    names = _declared_names_from_requirements_txt(repo_path / "requirements.txt")
    names += _declared_names_from_pyproject_toml(repo_path / "pyproject.toml")
    seen = set()
    ordered = []
    for name in names:
        if name not in seen:
            seen.add(name)
            ordered.append(name)
    return ordered


def import_candidates(package: str) -> list[str]:
    if package in PACKAGE_TO_IMPORT:
        return PACKAGE_TO_IMPORT[package]
    return [package.replace("-", "_")]
