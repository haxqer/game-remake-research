---
name: "game-remake-research"
description: "Use when Codex must turn an existing game into a source-backed remake / 复刻 / 对标 / vertical-slice research pack."
---

# Game Remake Research

Turn an existing game into source-backed remake documentation. Use this skill for remake, `复刻`, `对标`, benchmark, or vertical-slice research packs, not for generic brainstorming or casual comparisons.

## Use This Skill When

- The user wants to analyze an existing game as reference material for a remake or competitor study.
- The deliverable should be a source-backed pack, dossier, spec, formula set, experiment plan, or handoff bundle.
- The work must separate original-game facts from remake decisions and unknowns.

## Do Not Use This Skill When

- The user only wants a short opinion, recommendation, or surface-level comparison.
- The task is implementation-only and does not need research deliverables.
- The user only wants one narrow mechanic explained without a broader research pack.

## Start

- Lock the target game, edition or era, platform set, region, and time slice before writing conclusions.
- If the target is live-service and the user says `latest`, `current`, `live`, `today`, or similar, browse first and cite exact dates or build windows.
- Treat repo-local GDDs, spreadsheets, and technical docs as target-state inputs, not evidence about the original game.
- Pick one primary archetype lens. Read `references/template-selection.md` first, then load only the chosen `template-*.md` and `metrics-*.md` pair unless a secondary lens is clearly required.
- Scaffold the output pack before deep research. For packs that will be audited or handed off, pass a concrete `--version-scope`.

```bash
python3 "$GAME_REMAKE_RESEARCH/scripts/scaffold_remake_docs.py" \
  --game "MapleStory" \
  --out ./docs/remake-maplestory \
  --archetype mmo \
  --version-scope "KMS baseline as observed on 2026-03-01" \
  --language zh-CN \
  --with-support-files \
  --single-file
```

Example assumes `$GAME_REMAKE_RESEARCH` points at the skill root. If that variable is unset, run the same script from this skill's local `scripts/` directory.

## Workflow

1. Read `references/research-workflow.md` and lock scope before collecting sources.
2. Use `references/role-matrix.md` to cover every analysis lens in one coherent pack.
3. Use `references/deliverables.md` to keep the pack structure and section outputs aligned.
4. End every major section with open questions and the minimum validation step needed to close them.

## Load These References As Needed

- Planning and structure: `references/template-selection.md`, `references/research-workflow.md`, `references/role-matrix.md`, `references/deliverables.md`
- Evidence and capture: `references/evidence-rubric.md`, `references/citation-style.md`, `references/capture-methods.md`
- Experiments and metrics: `references/experiment-design.md`, `references/metric-rollup.md`, `references/experiment-summary.md`, `references/evidence-link-audit.md`
- Finish and handoff: `references/pack-audit.md`, `references/status-report.md`, `references/handoff-bundle.md`

## Evidence Rules

- Prefer sources in this order: official sites, manuals, patch notes, developer talks, direct gameplay footage, reputable wikis or datamines, then secondary commentary.
- Stamp important claims as `Confirmed`, `Inferred`, or `Open`.
- In `Confirmed Facts` and `Inferred Model`, cite ledger IDs inline with the claim, for example `S12` or `S12, S18`.
- Attach exact dates, versions, regions, and platforms to balance values, drop rules, UI flows, monetization details, and feature availability.
- If internals are unknowable, infer from repeated observation and explain the inference path instead of pretending certainty.
- Keep original-game facts separate from remake decisions.

## Scripts

- Core pack flow: `scaffold_remake_docs.py`, `merge_remake_docs.py`
- Experiment flow: `rollup_experiment_metrics.py`, `summarize_experiments.py`
- Audit flow: `audit_evidence_links.py`, `audit_remake_pack.py`
- Review and handoff: `build_pack_status_report.py`, `build_handoff_bundle.py`

If the user wants one final document, merge the pack in the order defined by `references/deliverables.md`.

## Common Failure Modes

- Mixing regions, eras, or platforms without labeling them.
- Loading all four archetype templates when one primary lens would do.
- Writing strong conclusions without an experiment plan for the highest-risk unknowns.
- Confusing inferred formulas with confirmed formulas.
- Writing opinions without backlog, risk, or acceptance criteria.
- Describing art direction without asset categories and reuse strategy.
- Describing feel without timing, state, cancel, or camera rules.
- Producing architecture prose without boundaries, hot paths, or tool implications.

## Check Before You Finish

- Confirm the user can see which version or build the research refers to.
- Confirm each role's output is reflected in the final pack rather than left as raw notes.
- Confirm formulas include units, variables, and assumptions.
- Confirm asset and animation sections describe production-ready categories, not just adjectives.
- Confirm architecture and engineering sections define boundaries, sequencing, and risks.
- Confirm unresolved gaps include a validation plan.
