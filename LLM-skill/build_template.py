#!/usr/bin/env python3
"""Render the UralicNLP skill template for a specific ISO 639-3 code."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve


TEXT_FILE_SUFFIXES = {".md", ".py", ".txt", ".yaml", ".yml"}
SKIP_NAMES = {"__pycache__"}
SKIP_SUFFIXES = {".pyc", ".hfstol"}
LEXICON_HEADER = "LEXICON Root\n\n"
MODEL_BASE_URL = "http://models.uralicnlp.com/nightly"


def _require_uralicnlp():
    try:
        from uralicNLP import string_processing  # type: ignore
        return string_processing
    except Exception as e:
        raise RuntimeError(
            "UralicNLP is not installed or failed to import. "
            "Install with: pip install -r uralicnlp-skill-template/scripts/requirements.txt"
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


def collect_dictionary_lines(dictionary_dir: Path, iso_code: str) -> list[str]:
    lines: list[str] = []
    needle = f"{iso_code}_"
    for name in ("dict1.lexc", "dict2.lexc"):
        source = dictionary_dir / name
        if not source.is_file():
            raise RuntimeError(f"Dictionary source file not found: {source}")
        with source.open(encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.rstrip("\n")
                if needle in line:
                    lines.append(line)
    if not lines:
        raise RuntimeError(f"No dictionary entries found for ISO code: {iso_code}")
    return lines


def split_dictionary_lines(lines: list[str]) -> tuple[list[str], list[str]]:
    midpoint = (len(lines) + 1) // 2
    return lines[:midpoint], lines[midpoint:]


def write_lexc_file(path: Path, lines: list[str]) -> None:
    content = LEXICON_HEADER + "\n".join(lines)
    if lines:
        content += "\n"
    path.write_text(content, encoding="utf-8")


def run_command(args: list[str], workdir: Path) -> None:
    try:
        subprocess.run(args, cwd=workdir, check=True)
    except FileNotFoundError as e:
        raise RuntimeError(f"Required command not found: {args[0]}") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed with exit code {e.returncode}: {' '.join(args)}") from e


def build_dictionary_file(temp_dir: Path, stem: str) -> Path:
    lexc_path = temp_dir / f"{stem}.lexc"
    hfst_path = temp_dir / f"{stem}.hfst"
    hfstol_path = temp_dir / f"{stem}.hfstol"
    run_command(["hfst-lexc", lexc_path.name, "-o", hfst_path.name], temp_dir)
    run_command(["hfst-fst2fst", "-O", "-i", hfst_path.name, "-o", hfstol_path.name], temp_dir)
    return hfstol_path


def build_dictionaries(project_dir: Path, output_dir: Path, iso_code: str) -> None:
    dictionary_dir = project_dir.parent / "dictionary-fst"
    filtered_lines = collect_dictionary_lines(dictionary_dir, iso_code)
    dict1_lines, dict2_lines = split_dictionary_lines(filtered_lines)
    scripts_dir = output_dir / "scripts"

    with tempfile.TemporaryDirectory(prefix=f"uralicnlp-{iso_code}-dict-") as temp_name:
        temp_dir = Path(temp_name)
        write_lexc_file(temp_dir / "dict1.lexc", dict1_lines)
        write_lexc_file(temp_dir / "dict2.lexc", dict2_lines)
        dict1_hfstol = build_dictionary_file(temp_dir, "dict1")
        dict2_hfstol = build_dictionary_file(temp_dir, "dict2")
        shutil.copy2(dict1_hfstol, scripts_dir / "dict1.hfstol")
        shutil.copy2(dict2_hfstol, scripts_dir / "dict2.hfstol")


def download_file(url: str, destination: Path) -> None:
    try:
        urlretrieve(url, destination)
    except HTTPError as e:
        raise RuntimeError(f"Download failed with HTTP {e.code}: {url}") from e
    except URLError as e:
        raise RuntimeError(f"Download failed for {url}: {e.reason}") from e


def download_models(output_dir: Path, iso_code: str) -> None:
    scripts_dir = output_dir / "scripts"
    analyzer_url = f"{MODEL_BASE_URL}/{iso_code}/analyser-gt-desc.hfstol"
    generator_url = f"{MODEL_BASE_URL}/{iso_code}/generator-gt-norm.hfstol"
    download_file(analyzer_url, scripts_dir / "analyser-gt-desc.hfstol")
    download_file(generator_url, scripts_dir / "generator-gt-norm.hfstol")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="build_template",
        description="Render the UralicNLP skill template for a specific language",
    )
    parser.add_argument("iso_code", help="ISO 639-3 language code, for example kpv")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory to write the rendered skill into. Defaults to ./build/uralicnlp-<iso>.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    iso_code = args.iso_code.strip().lower()
    language_name = iso_to_language_name(iso_code)

    project_dir = Path(__file__).resolve().parent
    template_dir = project_dir / "uralicnlp-skill-template"
    output_dir = args.output_dir or (project_dir / "build" / f"uralicnlp-{iso_code}")

    if not template_dir.is_dir():
        raise RuntimeError(f"Template directory not found: {template_dir}")
    if output_dir.exists():
        raise RuntimeError(f"Output directory already exists: {output_dir}")

    output_dir.mkdir(parents=True, exist_ok=False)
    render_tree(template_dir, output_dir, iso_code, language_name)
    download_models(output_dir, iso_code)
    build_dictionaries(project_dir, output_dir, iso_code)
    print(output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
