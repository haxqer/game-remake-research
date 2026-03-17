# game-remake-research

Standalone repository version of the `game-remake-research` Codex skill.

This repo helps you turn an existing game into a remake-ready research pack with:

- archetype-specific teardown templates for MMO, ARPG, roguelike, and card games
- evidence rules and source-ledger workflows
- experiment planning and metric rollup support
- audit, status-report, and handoff-bundle generators

## Repository Layout

- `skill/`: the installable skill root
- `skill/SKILL.md`: the skill definition used by Codex
- `skill/references/`: research workflow, templates, rubrics, and deliverable guides
- `skill/scripts/`: scaffold, merge, audit, rollup, summary, and handoff utilities
- `skill/agents/openai.yaml`: optional skill metadata for agent catalogs

## Requirements

- Python `3.10+`
- No third-party Python dependencies

## Quick Start

Run the bundled utilities from the repository root:

```bash
python3 ./skill/scripts/scaffold_remake_docs.py \
  --game "Hollow Knight" \
  --out ./docs/remake-hollow-knight \
  --archetype arpg \
  --version-scope "PC + Switch release content through Godmaster" \
  --language en \
  --with-support-files \
  --single-file
```

If you want the generated status reports and handoff notes to print copy-pasteable commands, set this once in your shell before working:

```bash
export GAME_REMAKE_RESEARCH="$PWD/skill"
```

Those generated docs assume the shell is inside the research pack root and use `$GAME_REMAKE_RESEARCH/scripts/...` to locate the installed skill scripts reliably.

## Common Commands

```bash
python3 ./skill/scripts/merge_remake_docs.py \
  --input-dir ./docs/remake-hollow-knight \
  --output hollow-knight-dossier.md \
  --mode compact
```

```bash
python3 ./skill/scripts/build_handoff_bundle.py \
  --docs-dir ./docs/remake-hollow-knight \
  --dossier-mode compact \
  --report-mode both \
  --rollup-metrics
```

## Use As A Codex Skill

Clone this repo wherever you want, then either symlink or copy it into your Codex skills directory:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
ln -s "$PWD/skill" "$CODEX_HOME/skills/game-remake-research"
```

After that, Codex can use `$game-remake-research` from the installed `skill/` path.

Restart Codex after installation so the new skill is picked up.

If you install from GitHub instead of a local clone, target the `skill/` subdirectory rather than the repo root:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo haxqer/game-remake-research \
  --path skill \
  --name game-remake-research
```

Or use the direct GitHub tree URL:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --url https://github.com/haxqer/game-remake-research/tree/main/skill \
  --name game-remake-research
```

## Local Verification

The GitHub Actions workflow runs a smoke test that:

- checks every script's `--help`
- scaffolds a sample research pack
- exercises merge, summary, audit, status-report, and handoff-bundle generation

When you expect `audit_remake_pack.py` to pass, make sure the scaffold uses a concrete `--version-scope` instead of the default placeholder.

You can run the same commands locally before publishing.
