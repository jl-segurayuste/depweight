# depweight

No solo el grafo de dependencias — cuánto se usa *realmente* cada una, para
saber si de verdad la necesitas entera o solo hace falta una función suelta.

```
$ depweight analyze .

[NARROW] requests -- 1 uso(s) en 1 fichero(s)
         Revisa si de verdad necesitas requests entera: scripts/ping.py
[NARROW] pandas -- 0 uso(s) en 0 fichero(s)
         Declarada pero no se encontró ningún uso real.

Total: 2 dependencia(s) de uso estrecho de 8 analizada(s).
```

## Por qué existe

Un grafo de dependencias te dice *qué* depende de *qué*, pero no *cuánto* de
verdad se usa. Es habitual arrastrar una librería entera (con su propio árbol
de subdependencias) para una sola llamada — `depweight` cuenta los usos
reales de cada dependencia declarada (vía AST, no regex) y señala las que
tienen un uso tan estrecho que merece la pena preguntarse si compensa.

## Instalación

Todavía no está en PyPI:

```bash
pip install git+https://github.com/jl-segurayuste/depweight.git
```

## Uso

```bash
depweight analyze .                       # solo las de uso estrecho
depweight analyze . --all                 # todas, incluidas las normales
depweight analyze . --threshold 5         # umbral de "estrecho" (por defecto 3)
depweight analyze . --json
depweight analyze . --fail-on-narrow      # código de salida 1 si hay alguna
```

Lee `requirements.txt`/`pyproject.toml` para las dependencias declaradas, y
recorre los ficheros `.py` rastreados por git (vía `git ls-files`, respeta
`.gitignore`) contando referencias reales a cada una vía `ast` — nunca
ejecuta el código analizado.

## Desarrollo

```bash
pip install -e ".[dev]"
ruff check .
pytest
```
