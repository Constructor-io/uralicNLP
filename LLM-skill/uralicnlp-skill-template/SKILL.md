---
name: uralicnlp-sms
description: morphologically analyze, lemmatize, and generate Skolt Sami words offline with bundled UralicNLP. Use when the user asks about Skolt Sami (`sms`) lemma forms, morphological tags, or inflection/generation from an analysis string.
---

# Skolt Sami morphology

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

## How to respond to users

### Inputs to request (only when missing)
- **word** or **inflection string**
- The language is fixed to **Skolt Sami** (`sms`); do not ask the user to choose another language.

### Output conventions
- Prefer returning:
  - **analysis** as a list of strings like `mieʹcc+N+Sg+Nom`
  - **lemmatization** as a list of lemmas
  - **generation** as a list of surface forms
- If the CLI returns `{ "error": ... }`, explain what went wrong and suggest the next action, usually installing deps or checking that the bundled HFST-OL files are present.
- This skill works offline by using the bundled HFST-OL files in `scripts/`. Do not rely on UralicNLP downloading models.

## Script reference
- `scripts/uralic_cli.py`: main entrypoint. Use it instead of rewriting code in-chat.
- `scripts/analyser-gt-desc.hfstol`: bundled Skolt Sami analyzer model.
- `scripts/generator-gt-norm.hfstol`: bundled Skolt Sami generator model.
- `scripts/requirements.txt`: dependency list.
