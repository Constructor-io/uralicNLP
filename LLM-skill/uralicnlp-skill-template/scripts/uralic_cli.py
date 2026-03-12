#!/usr/bin/env python3
"""Command-line interface for offline __LANG_NAME__ processing with UralicNLP.

This script is intended to be invoked by ChatGPT while using the skill.
It supports:
- analyze: morphological analysis (lemma+tags)
- generate: inflect/generate surface forms from full analysis string
- lemmatize: lemmatize a word
- translate: look up translations for a lemma

All outputs are JSON to make them easy to consume.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


LANG = "__LANG_ISO__"
SCRIPT_DIR = Path(__file__).resolve().parent
ANALYZER_PATH = SCRIPT_DIR / "analyser-gt-desc.hfstol"
GENERATOR_PATH = SCRIPT_DIR / "generator-gt-norm.hfstol"
DICT1_PATH = SCRIPT_DIR / "dict1.hfstol"
DICT2_PATH = SCRIPT_DIR / "dict2.hfstol"


def _require_uralicnlp():
    try:
        from uralicNLP import uralicApi  # type: ignore
        return uralicApi
    except Exception as e:
        raise RuntimeError(
            "UralicNLP is not installed or failed to import. "
            "Install with: pip install -r scripts/requirements.txt"
        ) from e


def _json_print(obj: Any) -> None:
    json.dump(obj, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def _require_model(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(f"Required model file not found: {path}")
    return str(path)


def cmd_analyze(args: argparse.Namespace) -> int:
    uralicApi = _require_uralicnlp()
    word = args.word
    analyses = uralicApi.analyze(word, LANG, filename=_require_model(ANALYZER_PATH)) or []
    # uralicApi.analyze returns list of tuples, first element is the analysis string
    _json_print([x[0] for x in analyses])
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    uralicApi = _require_uralicnlp()
    infl = args.inflection
    forms = uralicApi.generate(infl, LANG, filename=_require_model(GENERATOR_PATH)) or []
    _json_print([x[0] for x in forms])
    return 0


def cmd_lemmatize(args: argparse.Namespace) -> int:
    uralicApi = _require_uralicnlp()
    word = args.word
    lemmas = uralicApi.lemmatize(word, LANG, filename=_require_model(ANALYZER_PATH)) or []
    _json_print(lemmas)
    return 0


def cmd_translate(args: argparse.Namespace) -> int:
    uralicApi = _require_uralicnlp()
    lemma = args.lemma
    translations = uralicApi.get_translation(
        lemma,
        LANG,
        filename1=_require_model(DICT1_PATH),
        filename2=_require_model(DICT2_PATH),
    ) or []
    _json_print(translations)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="uralic_cli",
        description="Offline __LANG_NAME__ morphology with bundled UralicNLP HFST-OL models",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze", help="__LANG_NAME__ morphological analysis")
    a.add_argument("--word", required=True)
    a.set_defaults(func=cmd_analyze)

    g = sub.add_parser("generate", help="generate __LANG_NAME__ surface forms")
    g.add_argument("--inflection", required=True, help="full analysis string, e.g. kuätt+N+Sg+Gen")
    g.set_defaults(func=cmd_generate)

    l = sub.add_parser("lemmatize", help="lemmatize a __LANG_NAME__ word")
    l.add_argument("--word", required=True)
    l.set_defaults(func=cmd_lemmatize)

    t = sub.add_parser("translate", help="translate a __LANG_NAME__ lemma")
    t.add_argument("--lemma", required=True)
    t.set_defaults(func=cmd_translate)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except Exception as e:
        # Emit a structured error for easier handling
        _json_print({"error": str(e), "cmd": getattr(args, "cmd", None)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
