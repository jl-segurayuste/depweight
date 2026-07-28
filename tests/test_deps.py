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
