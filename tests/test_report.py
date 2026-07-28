from depweight.analyze import DependencyUsage
from depweight.report import to_console, to_json


def test_to_console_sin_narrow_mensaje_limpio():
    results = [DependencyUsage(package="click", import_names=["click"], usage_count=10, files=["a.py"], narrow=False)]
    out = to_console(results, only_narrow=True)
    assert "No hay dependencias" in out


def test_to_console_muestra_narrow():
    results = [
        DependencyUsage(package="requests", import_names=["requests"], usage_count=1, files=["a.py"], narrow=True)
    ]
    out = to_console(results)
    assert "[NARROW]" in out
    assert "requests" in out
    assert "🔧" not in out and "⚠" not in out


def test_to_console_cero_usos_mensaje_especifico():
    results = [DependencyUsage(package="unused", import_names=["unused"], usage_count=0, files=[], narrow=True)]
    out = to_console(results)
    assert "no se encontró ningún uso real" in out


def test_to_json_valido():
    results = [DependencyUsage(package="click", import_names=["click"], usage_count=5, files=[], narrow=False)]
    out = to_json(results)
    assert '"package": "click"' in out
