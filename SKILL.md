---
name: "game-remake-research"
description: "Use when Codex needs a source-backed teardown of an existing game and a remake-ready research pack, vertical-slice spec, or benchmark dossier."
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
- If the user says `latest`, `current`, `live`, `today`, or similar for a live-service game, browse first and cite exact dates or build windows.
- Treat repo-local GDDs, spreadsheets, and technical docs as target-state inputs, not evidence about the original game.
- Pick one primary archetype lens when the target clearly behaves like an MMO, ARPG, roguelike, or card game. Read `references/template-selection.md` first for hybrids.
- Read only the matching archetype template and metrics reference unless a secondary lens is clearly required:
  - `references/template-mmo.md` + `references/metrics-mmo.md`
  - `references/template-arpg.md` + `references/metrics-arpg.md`
  - `references/template-roguelike.md` + `references/metrics-roguelike.md`
  - `references/template-card.md` + `references/metrics-card.md`
- Scaffold the output pack before deep research. For packs that will be audited or handed off, pass a concrete `--version-scope`.
- When running bundled scripts, resolve them from this skill's `scripts/` directory. Repository installs often expose that root as `$GAME_REMAKE_RESEARCH`.

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

## Workflow

1. Read `references/research-workflow.md` and lock scope before collecting sources.
2. Build the evidence base from primary sources first, then representative gameplay observation.
3. Run one coherent multi-role teardown using shared source IDs and shared assumptions.
4. Translate observations into remake-ready loops, formulas, pipelines, content structures, and risks.
5. End every major section with open questions and the minimum validation step needed to close them.

## Load These References As Needed

- `references/role-matrix.md`: role-by-role questions and expected outputs.
- `references/deliverables.md`: pack structure and required document contents.
- `references/evidence-rubric.md`: how to grade claims as `Confirmed`, `Inferred`, or `Open`.
- `references/citation-style.md`: how to place inline `S-id` anchors in the docs.
- `references/capture-methods.md`: frame counts, economy samples, UI-flow capture, and audio breakdowns.
- `references/experiment-design.md`: reusable experiment plans and sampling patterns.
- `references/metric-rollup.md`: syncing typed experiment observations into archetype metrics.
- `references/experiment-summary.md`: regenerating full or compact experiment summaries.
- `references/evidence-link-audit.md`: checking `source_id` and `source_ids` integrity.
- `references/pack-audit.md`: final pack audit workflow.
- `references/status-report.md`: generating reviewer or takeover status snapshots.
- `references/handoff-bundle.md`: generating the full handoff bundle in one command.

## Evidence Rules

- Prefer sources in this order: official sites, manuals, patch notes, developer talks, direct gameplay footage, reputable wikis or datamines, then secondary commentary.
- Stamp important claims as `Confirmed`, `Inferred`, or `Open`.
- In `Confirmed Facts` and `Inferred Model`, cite ledger IDs inline with the claim, for example `S12` or `S12, S18`.
- Attach exact dates, versions, regions, and platforms to balance values, drop rules, UI flows, monetization details, and feature availability.
- If internals are unknowable, infer from repeated observation and explain the inference path instead of pretending certainty.
- Keep original-game facts separate from remake decisions.

## Coverage

Cover these analytical lenses in one coherent pack, not as theatrical role dialogue:

- professional game design
- balance design
- gameplay design
- product management
- art
- animation
- music and audio
- copywriting
- narrative
- game client architecture
- lead engineering

Use `references/role-matrix.md` when you need the detailed question set.

## Scripts

- `scaffold_remake_docs.py`: create the research pack scaffold. Treat `--version-scope` as required when the pack will go through audit, status reporting, or handoff.
- `merge_remake_docs.py`: merge a finished multi-file pack into one dossier. Use compact mode for shorter external-facing deliverables.
- `rollup_experiment_metrics.py`: sync typed experiment observations back into `data/archetype-metrics.csv`.
- `summarize_experiments.py`: generate full or compact experiment summaries from plan, registry, typed sheets, and metric rollup.
- `audit_evidence_links.py`: verify that ledger IDs and support-file source references still match.
- `audit_remake_pack.py`: catch placeholders, incomplete support files, and stale generated artifacts before handoff.
- `build_pack_status_report.py`: generate a progress snapshot for review, producer check-ins, or takeover.
- `build_handoff_bundle.py`: regenerate summaries, audits, status reports, and dossiers in one pass.

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
