---
name: uralicnlp-__LANG_ISO__
description: morphologically analyze, lemmatize, translate, and generate __LANG_NAME__ words offline with bundled UralicNLP. Use when the user asks about __LANG_NAME__ (`__LANG_ISO__`) lemma forms, morphological tags, translations, or inflection/generation from an analysis string.
---

# __LANG_NAME__ morphology

## Quick start

### 1) Ensure dependencies are installed
If imports fail or this is the first run in the session, install UralicNLP:

```bash
python -m pip install -r scripts/requirements.txt
```

### 2) Use the CLI helper for deterministic results
All commands output JSON.

- Morphological analysis:
```bash
python scripts/uralic_cli.py analyze --word mieʹcc
```

- Lemmatize:
```bash
python scripts/uralic_cli.py lemmatize --word mieʹcen
```

- Generate/inflect from a full analysis string:
```bash
python scripts/uralic_cli.py generate --inflection mieʹcc+N+Sg+Gen
```

- Translate a lemma:
```bash
python scripts/uralic_cli.py translate --lemma mieʹcc
```

## How to respond to users

### Inputs to request (only when missing)
- **word** or **inflection string**
- **lemma** for translations
- The language is fixed to **__LANG_NAME__** (`__LANG_ISO__`); do not ask the user to choose another language.

### Output conventions
- Prefer returning:
  - **analysis** as a list of strings like `mieʹcc+N+Sg+Nom`
  - **lemmatization** as a list of lemmas
  - **translation** as the JSON value returned by the translation lookup
  - **generation** as a list of surface forms
- If the CLI returns `{ "error": ... }`, explain what went wrong and suggest the next action, usually installing deps or checking that the bundled HFST-OL files are present.
- This skill works offline by using the bundled HFST-OL files in `scripts/`. Do not rely on UralicNLP downloading models.

## Script reference
- `scripts/uralic_cli.py`: main entrypoint. Use it instead of rewriting code in-chat.
- `scripts/analyser-gt-desc.hfstol`: bundled __LANG_NAME__ analyzer model.
- `scripts/dict1.hfstol`: first bundled __LANG_NAME__ translation dictionary.
- `scripts/dict2.hfstol`: second bundled __LANG_NAME__ translation dictionary.
- `scripts/generator-gt-norm.hfstol`: bundled __LANG_NAME__ generator model.
- `scripts/requirements.txt`: dependency list.
