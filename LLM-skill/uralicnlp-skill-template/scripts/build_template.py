#!/usr/bin/env python3
"""Render the UralicNLP skill template for a specific ISO 639-3 code."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

TEXT_FILE_SUFFIXES = {".md", ".py", ".txt", ".yaml", ".yml"}
SKIP_NAMES = {"__pycache__", "build_template.py"}
SKIP_SUFFIXES = {".pyc", ".hfstol"}


def _require_uralicnlp():
    try:
        from uralicNLP import string_processing  # type: ignore
        return string_processing
    except Exception as e:
        raise RuntimeError(
            "UralicNLP is not installed or failed to import. "
            "Install with: pip install -r scripts/requirements.txt"
        ) from e


def iso_to_language_name(iso_code: str) -> str:
    string_processing = _require_uralicnlp()
    language_name = string_processing.iso_to_name(iso_code)
    if not language_name:
        raise RuntimeError(f"Could not resolve language name for ISO code: {iso_code}")
    return str(language_name)


def should_skip(path: Path) -> bool:
    return path.name in SKIP_NAMES or path.suffix in SKIP_SUFFIXES


def replace_placeholders(text: str, iso_code: str, language_name: str) -> str:
    result = text
    replacements = {
        "__LANG_ISO__": iso_code,
        "__LANG_NAME__": language_name,
    }
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)
    return result


def render_tree(template_dir: Path, output_dir: Path, iso_code: str, language_name: str) -> None:
    for source in template_dir.rglob("*"):
        relative = source.relative_to(template_dir)
        if should_skip(source):
            continue

        destination = output_dir / relative
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix in TEXT_FILE_SUFFIXES:
            rendered = replace_placeholders(source.read_text(encoding="utf-8"), iso_code, language_name)
            destination.write_text(rendered, encoding="utf-8")
        else:
            shutil.copy2(source, destination)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="build_template",
        description="Render the UralicNLP skill template for a specific language",
    )
    parser.add_argument("iso_code", help="ISO 639-3 language code, for example kpv")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory to write the rendered skill into. Defaults to ../build/uralicnlp-<iso>.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    iso_code = args.iso_code.strip().lower()
    language_name = iso_to_language_name(iso_code)

    script_dir = Path(__file__).resolve().parent
    template_dir = script_dir.parent
    output_dir = args.output_dir or (template_dir.parent / "build" / f"uralicnlp-{iso_code}")

    if output_dir.exists():
        raise RuntimeError(f"Output directory already exists: {output_dir}")

    output_dir.mkdir(parents=True, exist_ok=False)
    render_tree(template_dir, output_dir, iso_code, language_name)
    print(output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
