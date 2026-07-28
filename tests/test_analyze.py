from conftest import commit_all, write

from depweight.analyze import analyze_repo


def test_dependencia_usada_mucho_no_es_narrow(git_repo):
    write(git_repo, "requirements.txt", "click\n")
    write(
        git_repo,
        "app.py",
        "import click\n"
        "click.echo('a')\n"
        "click.echo('b')\n"
        "click.echo('c')\n"
        "click.echo('d')\n",
    )
    commit_all(git_repo)
    results = analyze_repo(git_repo, threshold=3)
    click_usage = next(r for r in results if r.package == "click")
    assert click_usage.usage_count == 4
    assert click_usage.narrow is False


def test_dependencia_usada_poco_es_narrow(git_repo):
    write(git_repo, "requirements.txt", "requests\n")
    write(git_repo, "app.py", "import requests\nrequests.get('x')\n")
    commit_all(git_repo)
    results = analyze_repo(git_repo, threshold=3)
    req_usage = next(r for r in results if r.package == "requests")
    assert req_usage.usage_count == 1
    assert req_usage.narrow is True


def test_dependencia_declarada_sin_ningun_uso(git_repo):
    write(git_repo, "requirements.txt", "unused-pkg\n")
    write(git_repo, "app.py", "x = 1\n")
    commit_all(git_repo)
    results = analyze_repo(git_repo, threshold=3)
    usage = next(r for r in results if r.package == "unused-pkg")
    assert usage.usage_count == 0
    assert usage.files == []
    assert usage.narrow is True


def test_uso_repartido_en_varios_ficheros_se_suma(git_repo):
    write(git_repo, "requirements.txt", "click\n")
    write(git_repo, "a.py", "import click\nclick.echo('a')\n")
    write(git_repo, "b.py", "import click\nclick.echo('b')\nclick.echo('c')\n")
    commit_all(git_repo)
    results = analyze_repo(git_repo, threshold=3)
    click_usage = next(r for r in results if r.package == "click")
    assert click_usage.usage_count == 3
    assert set(click_usage.files) == {"a.py", "b.py"}


def test_mapeo_pyyaml_a_yaml_funciona(git_repo):
    write(git_repo, "requirements.txt", "pyyaml\n")
    write(git_repo, "app.py", "import yaml\nyaml.safe_load('x')\n")
    commit_all(git_repo)
    results = analyze_repo(git_repo, threshold=3)
    usage = next(r for r in results if r.package == "pyyaml")
    assert usage.usage_count == 1
    assert usage.import_names == ["yaml"]


def test_sin_dependencias_declaradas_devuelve_none(git_repo):
    write(git_repo, "app.py", "x = 1\n")
    commit_all(git_repo)
    assert analyze_repo(git_repo) is None


def test_sin_repo_git_devuelve_none_no_falsos_cero_usos(tmp_path):
    # requirements.txt existe pero no hay .git -- no se puede determinar que
    # ficheros mirar, y NO debe reportarse como "0 usos" (falso positivo).
    write(tmp_path, "requirements.txt", "requests\n")
    write(tmp_path, "app.py", "import requests\nrequests.get('x')\n")
    assert analyze_repo(tmp_path) is None
