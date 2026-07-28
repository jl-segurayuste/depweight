from __future__ import annotations

import argparse
import sys
from pathlib import Path

from depweight.analyze import analyze_repo
from depweight.report import to_console, to_json


def _cmd_analyze(args: argparse.Namespace) -> int:
    repo_path = Path(args.path).resolve()
    results = analyze_repo(repo_path, threshold=args.threshold)

    if not results:
        print("No aplica: no se encontró requirements.txt ni pyproject.toml, o no declara dependencias.")
        return 0

    if args.json:
        print(to_json(results))
    else:
        print(to_console(results, only_narrow=not args.all))

    if args.fail_on_narrow and any(r.narrow for r in results):
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="depweight")
    sub = parser.add_subparsers(dest="command", required=True)

    p_analyze = sub.add_parser("analyze", help="Cuánto se usa realmente cada dependencia declarada")
    p_analyze.add_argument("path", nargs="?", default=".")
    p_analyze.add_argument(
        "--threshold",
        type=int,
        default=3,
        help="Nº de usos máximo para considerar una dependencia de uso 'estrecho' (por defecto 3)",
    )
    p_analyze.add_argument("--all", action="store_true", help="Muestra también las que tienen uso normal")
    p_analyze.add_argument("--json", action="store_true")
    p_analyze.add_argument("--fail-on-narrow", action="store_true")
    p_analyze.set_defaults(func=_cmd_analyze)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
