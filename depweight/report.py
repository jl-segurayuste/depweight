from __future__ import annotations

import json

from depweight.analyze import DependencyUsage


def to_console(results: list[DependencyUsage], *, only_narrow: bool = False) -> str:
    shown = [r for r in results if r.narrow] if only_narrow else results
    if not shown:
        return "No hay dependencias con uso estrecho -- todo parece justificado."

    lines = []
    for r in sorted(shown, key=lambda x: x.usage_count):
        label = "[NARROW]" if r.narrow else "[OK    ]"
        lines.append(f"{label} {r.package} -- {r.usage_count} uso(s) en {len(r.files)} fichero(s)")
        if r.implied_by:
            lines.append(f"         Hace falta para {', '.join(r.implied_by)} (la carga o la usa por dentro), aunque apenas se importe.")
        elif r.usage_count == 0:
            lines.append("         Declarada pero no se encontró ningún uso real.")
        elif r.narrow:
            lines.append(f"         Revisa si de verdad necesitas {r.package} entera: {', '.join(r.files[:3])}")

    narrow_count = sum(1 for r in results if r.narrow)
    lines.append("")
    lines.append(f"Total: {narrow_count} dependencia(s) de uso estrecho de {len(results)} analizada(s).")
    return "\n".join(lines)


def to_json(results: list[DependencyUsage]) -> str:
    return json.dumps([r.model_dump() for r in results], ensure_ascii=False, indent=2)
