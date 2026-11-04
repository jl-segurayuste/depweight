from conftest import write

from depweight.deps import declared_packages, import_candidates


def test_declared_packages_requirements_txt(git_repo):
    write(git_repo, "requirements.txt", "requests>=2.31\nclick\n")
    assert declared_packages(git_repo) == ["requests", "click"]


def test_declared_packages_pyproject_toml(git_repo):
    write(git_repo, "pyproject.toml", '[project]\nname="x"\ndependencies = ["pydantic>=2.6"]\n')
    assert declared_packages(git_repo) == ["pydantic"]


def test_declared_packages_combina_y_deduplica(git_repo):
    write(git_repo, "requirements.txt", "click\n")
    write(git_repo, "pyproject.toml", '[project]\nname="x"\ndependencies = ["click", "requests"]\n')
    assert declared_packages(git_repo) == ["click", "requests"]


def test_declared_packages_ninguno(git_repo):
    assert declared_packages(git_repo) == []


def test_import_candidates_mapeo_conocido():
    assert import_candidates("pyyaml") == ["yaml"]
    assert import_candidates("beautifulsoup4") == ["bs4"]


def test_import_candidates_normaliza_guiones():
    assert import_candidates("some-package") == ["some_package"]


def test_import_candidates_sin_mapeo_usa_nombre_normalizado():
    assert import_candidates("requests") == ["requests"]


def test_import_candidates_mapeo_conocido_ignora_mayusculas():
    # Bug real encontrado 2026-08-09: requirements.txt/pyproject.toml suelen
    # declarar el nombre tal como aparece en PyPI ("PyYAML", "Pillow"), pero
    # el mapa usa claves en minúsculas -- comparar sin normalizar hacía que
    # NINGUNA de estas entradas mapeadas coincidiera nunca al declararse con
    # su capitalización real.
    assert import_candidates("PyYAML") == ["yaml"]
    assert import_candidates("Pillow") == ["PIL"]


def test_import_candidates_sin_mapeo_prueba_tambien_minusculas():
    # Bug real encontrado 2026-08-09: la inmensa mayoría de paquetes sin
    # mapeo explícito también importan en minúsculas aunque se declaren
    # capitalizados ("Django" -> "django") -- sin esto, Django aparecía con
    # 0 usos pese a estar fuertemente usado, el falso positivo exacto que
    # esta herramienta existe para evitar.
    assert import_candidates("Django") == ["Django", "django"]


def test_import_candidates_sin_mapeo_ya_en_minusculas_no_duplica():
    assert import_candidates("requests") == ["requests"]


def test_import_candidates_nombre_normalizado_como_pypi():
    from depweight.deps import import_candidates

    assert import_candidates("python_dateutil") == ["dateutil"]
    assert import_candidates("Python.Dateutil") == ["dateutil"]
    assert import_candidates("psycopg2-binary") == ["psycopg2"]
    assert import_candidates("opencv-python-headless") == ["cv2"]
    assert import_candidates("ruamel.yaml") == ["ruamel.yaml"]
    assert import_candidates("zope.interface") == ["zope.interface"]
