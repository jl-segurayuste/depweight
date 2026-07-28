import ast

from depweight.usage import analyze_file, bound_names, count_usages_per_name


def test_bound_names_import_simple():
    tree = ast.parse("import requests\n")
    assert bound_names(tree) == {"requests": "requests"}


def test_bound_names_import_con_alias():
    tree = ast.parse("import numpy as np\n")
    assert bound_names(tree) == {"np": "numpy"}


def test_bound_names_from_import():
    tree = ast.parse("from pathlib import Path\n")
    assert bound_names(tree) == {"Path": "pathlib"}


def test_bound_names_ignora_imports_relativos():
    tree = ast.parse("from .mod import algo\n")
    assert bound_names(tree) == {}


def test_bound_names_submodulo_usa_top_level():
    tree = ast.parse("import os.path\n")
    assert bound_names(tree) == {"os": "os"}


def test_count_usages_per_name_cuenta_usos_reales():
    tree = ast.parse("import requests\nrequests.get('x')\nrequests.post('y')\n")
    counts = count_usages_per_name(tree, {"requests"})
    assert counts["requests"] == 2


def test_count_usages_per_name_cero_si_no_se_usa():
    tree = ast.parse("import requests\n")
    counts = count_usages_per_name(tree, {"requests"})
    assert counts["requests"] == 0


def test_analyze_file_devuelve_bindings_y_counts(tmp_path):
    p = tmp_path / "mod.py"
    p.write_text("import click\nclick.echo('hola')\n", encoding="utf-8")
    bindings, counts = analyze_file(p)
    assert bindings == {"click": "click"}
    assert counts == {"click": 1}


def test_analyze_file_codigo_invalido_devuelve_none(tmp_path):
    p = tmp_path / "bad.py"
    p.write_text("esto no es python [[[", encoding="utf-8")
    assert analyze_file(p) is None


def test_analyze_file_inexistente_devuelve_none(tmp_path):
    assert analyze_file(tmp_path / "no-existe.py") is None
