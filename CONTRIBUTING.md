# Contribuir

## Añadir un mapeo paquete → import

Si te encuentras con un paquete cuyo nombre de import no coincide con el
nombre normalizado del paquete en PyPI (como `pyyaml` → `yaml`), añádelo a
`PACKAGE_TO_IMPORT` en `depweight/deps.py` y un test en `tests/test_deps.py`.

## Antes de un PR

- `ruff check .` y `pytest` en verde.
- Nunca ejecutar el código del repo analizado — todo el análisis es estático
  (AST), como en el resto del análisis existente.
