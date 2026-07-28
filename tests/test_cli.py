from conftest import commit_all, write

from depweight.cli import main


def test_analyze_sin_dependencias_exit_0(git_repo, capsys):
    write(git_repo, "app.py", "x = 1\n")
    commit_all(git_repo)
    rc = main(["analyze", str(git_repo)])
    assert rc == 0
    assert "No aplica" in capsys.readouterr().out


def test_analyze_con_narrow_exit_1_si_fail_on_narrow(git_repo, capsys):
    write(git_repo, "requirements.txt", "requests\n")
    write(git_repo, "app.py", "import requests\nrequests.get('x')\n")
    commit_all(git_repo)
    rc = main(["analyze", str(git_repo), "--fail-on-narrow"])
    assert rc == 1


def test_analyze_sin_narrow_exit_0(git_repo, capsys):
    write(git_repo, "requirements.txt", "click\n")
    write(git_repo, "app.py", "import click\n" + "click.echo('x')\n" * 5)
    commit_all(git_repo)
    rc = main(["analyze", str(git_repo), "--fail-on-narrow"])
    assert rc == 0


def test_analyze_json(git_repo, capsys):
    write(git_repo, "requirements.txt", "click\n")
    write(git_repo, "app.py", "import click\nclick.echo('x')\n")
    commit_all(git_repo)
    main(["analyze", str(git_repo), "--json"])
    out = capsys.readouterr().out
    assert '"package"' in out


def test_analyze_threshold_personalizado(git_repo, capsys):
    write(git_repo, "requirements.txt", "click\n")
    write(git_repo, "app.py", "import click\n" + "click.echo('x')\n" * 5)
    commit_all(git_repo)
    rc = main(["analyze", str(git_repo), "--threshold", "10", "--fail-on-narrow"])
    assert rc == 1  # con threshold=10, 5 usos SI es narrow
