---
name: "game-remake-research"
description: "Deep game teardown and remake-documentation skill. Use when Codex needs to analyze an existing game and produce recreation or 复刻 or 对标 docs: source-backed breakdowns from professional game design, balance design, gameplay design, product management, art, animation, music/audio, copywriting, narrative, client architecture, and lead engineering, plus a replica-ready document pack with formulas, pipelines, implementation order, risks, and open questions."
---

# Game Remake Research

Research an existing game as if preparing a vertical slice or full remake. Use roles as analytical lenses, not theatrical dialogue, and synthesize them into one coherent specification.

## Skill Paths

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export GAME_REMAKE_RESEARCH="$CODEX_HOME/skills/game-remake-research"
```

User-scoped skills install under `$CODEX_HOME/skills` by default.

## Start

- Lock the target game, platform, region, edition, and time slice before drawing conclusions.
- If the user says `latest`, `current`, `live`, `today`, or similar for a live-service game, browse first and cite exact dates or build windows.
- Treat repo-local GDDs, spreadsheets, and technical docs as internal target-state inputs, not evidence about the original game.
- Pick one primary archetype lens when the target clearly behaves like an MMO, ARPG, roguelike, or card game. Read `references/template-selection.md` first for hybrids.
- Read only the matching archetype reference and matching metrics reference unless a secondary lens is clearly required:
  - `references/template-mmo.md`
  - `references/metrics-mmo.md`
  - `references/template-arpg.md`
  - `references/metrics-arpg.md`
  - `references/template-roguelike.md`
  - `references/metrics-roguelike.md`
  - `references/template-card.md`
  - `references/metrics-card.md`
- Scaffold the output pack before deep research. Use support files when the project is large, version-sensitive, or likely to be revisited:

```bash
python3 "$GAME_REMAKE_RESEARCH/scripts/scaffold_remake_docs.py" \
  --game "MapleStory" \
  --out ./docs/remake-maplestory \
  --archetype mmo \
  --language zh-CN \
  --with-support-files \
  --single-file
```

- Read `references/research-workflow.md` for the execution order.
- Read `references/role-matrix.md` when you need the role-by-role question set.
- Read `references/deliverables.md` before writing the final pack.
- Read `references/evidence-rubric.md` when facts are disputed, version-sensitive, or sourced from mixed regions.
- Read `references/citation-style.md` when drafting dossier sections or fixing evidence-audit warnings about missing inline source anchors.
- Read `references/evidence-link-audit.md` when you need to verify that `source_id` / `source_ids` references across CSVs and experiment sheets still match the ledger.
- Read `references/capture-methods.md` when you need frame counts, economy samples, UI-flow capture, or audio breakdowns.
- Read `references/experiment-design.md` when you need reusable sampling plans for timings, routes, onboarding, economy, or failure-reentry.
- Read `references/metric-rollup.md` when typed experiment data should be synchronized back into `data/archetype-metrics.csv`.
- Read `references/experiment-summary.md` when raw experiment CSVs should be turned into a concise markdown brief.
- Read `references/pack-audit.md` before final handoff or when inheriting a half-finished research pack and you need a fast completeness check.
- Read `references/status-report.md` when the user needs a one-file progress snapshot for handoff, producer review, or takeover.
- Read `references/handoff-bundle.md` when the user wants one command to generate handoff-ready summaries, dossiers, reports, and audit output.

## Evidence Rules

- Prefer sources in this order: official sites, manuals, patch notes, developer talks, direct gameplay footage, reputable wikis or datamines, then secondary commentary.
- Stamp each important claim as `Confirmed`, `Inferred`, or `Open`.
- In `Confirmed Facts` and `Inferred Model`, cite ledger IDs inline with the claim, for example `S12` or `S12, S18`.
- Attach exact dates, versions, regions, and platforms to balance values, drop rules, UI flows, monetization details, and feature availability.
- If internals are unknowable, infer from repeated observation and explain the inference path instead of pretending certainty.
- Separate `original-game facts` from `remake decisions`. The latter are design proposals, not discoveries.

## Workflow

1. **Lock scope.**
   Define the research target precisely: game, version band, platforms, regions, and whether the goal is a reference study, vertical slice, or full remake pack.
2. **Build the evidence base.**
   Gather primary sources first. For historical games, combine official material with representative footage from early game, mid game, endgame, menus, progression, and boss content.
3. **Run the multi-role teardown.**
   Cover every role below. Keep one shared source ledger and do not let roles contradict each other silently.
4. **Translate the teardown into remake specifications.**
   Convert observed systems into implementation-ready loops, formulas, asset lists, state machines, content taxonomies, pipelines, and milestones.
5. **Close with gaps and validation.**
   End every major section with unknowns, proposed validation steps, and the minimum experiment needed to confirm the assumption.

## Multi-Role Coverage

- `Professional game designer`: fantasy, product pillars, macro loops, content topology, progression gates, and must-preserve moments.
- `Balance designer`: stats, currencies, faucets and sinks, drop logic, upgrade formulas, pacing bands, and failure recovery.
- `Gameplay designer`: controls, verb set, combat rules, hit timing, encounter grammar, map traversal, and fail states.
- `Product manager`: audience, positioning, retention logic, monetization or de-monetization strategy, scope cuts, and release plan.
- `Art`: camera framing, color language, shape language, UI language, environment tiers, character readability, and asset taxonomy.
- `Animation`: state list, anticipation, active and recovery windows, cancel rules, locomotion sets, boss telegraphs, and reusable rigs.
- `Music/audio`: cue map, instrumentation, dynamic music rules, SFX taxonomy, mix priorities, and feedback hierarchy.
- `Copywriting`: terminology, UI copy tone, quest text patterns, naming rules, and localization-sensitive constraints.
- `Narrative`: world pillars, narrative structure, onboarding fiction, quest arcs, NPC roles, and tone consistency.
- `Game client architect`: runtime modules, scene or screen flow, data boundaries, content pipelines, save model, tools, and performance budgets.
- `Lead engineer`: implementation order, staffing assumptions, build-vs-buy decisions, technical risks, test strategy, and acceptance gates.

Load `references/role-matrix.md` when you need the detailed question bank and mandatory outputs for each role.

## Output Standard

- Produce a document pack, not a loose brainstorm.
- Ensure every file is source-backed and version-stamped.
- Put facts, inferred models, remake decisions, and open questions in separate subsections.
- When evidence is sparse, prefer explicit gaps over generic filler.
- Do not output theatrical “role dialogue”; each role should sharpen the analysis, not fragment the deliverable.
- If the user only wants one document, merge the sections from `references/deliverables.md` into one dossier while preserving the same order.

## Scripts

Use the scaffold script to create a repeatable doc structure:

```bash
python3 "$GAME_REMAKE_RESEARCH/scripts/scaffold_remake_docs.py" \
  --game "Hollow Knight" \
  --out ./docs/remake-hollow-knight \
  --archetype arpg \
  --version-scope "PC + Switch release content through Godmaster" \
  --language en \
  --with-support-files \
  --single-file
```

Options:

- `--game`: required target title.
- `--out`: required output directory.
- `--version-scope`: optional baseline string written into the templates.
- `--language`: `en` or `zh-CN`.
- `--archetype`: optional primary lens: `mmo`, `arpg`, `roguelike`, or `card`.
- `--single-file`: also create a single-file dossier template.
- `--with-support-files`: also create manifest and CSV support templates.
  When `--archetype` is set, this also creates `data/archetype-checklist.csv` and `data/archetype-metrics.csv`.
  It also creates `09-experiment-design.md`, `data/experiment-plan.csv`, and `data/experiment-observations.csv`.
  `data/experiment-plan.csv` is automatically priority-ranked for the selected archetype.
  Raw experiment measurements now go into typed templates under `data/experiments/`.
  It also creates `10-experiment-summary.md` as a regenerable summary target.
  When preparing a compact dossier, also generate `10-experiment-summary-compact.md`.
- `--force`: overwrite existing scaffold files.

Merge a finished multi-file pack into one dossier when the user wants a single deliverable:

```bash
python3 "$GAME_REMAKE_RESEARCH/scripts/merge_remake_docs.py" \
  --input-dir ./docs/remake-hollow-knight \
  --output hollow-knight-dossier.md \
  --mode compact
```

Options:

- `--input-dir`: required research directory.
- `--output`: output file name inside the directory.
- `--title`: optional dossier title.
- `--include-log`: include `99-research-log.md`.
- `--mode`: `full` keeps the full research pack order; `compact` omits `09-experiment-design.md` and prefers `10-experiment-summary-compact.md`, falling back to `10-experiment-summary.md`.
- `--force`: overwrite the output file.

Roll typed experiment observations back into archetype metrics after collecting data:

```bash
python3 "$GAME_REMAKE_RESEARCH/scripts/rollup_experiment_metrics.py" \
  --docs-dir ./docs/remake-maplestory
```

Generate a markdown summary from experiment plan, registry, typed sheets, and current metric rollup:

```bash
python3 "$GAME_REMAKE_RESEARCH/scripts/summarize_experiments.py" \
  --docs-dir ./docs/remake-maplestory \
  --mode full
```

The experiment summary now also surfaces raw-sample totals, how many experiments already have typed evidence, and a priority-ranked next-pass list with experiment IDs, statuses, and current sample counts.
`summarize_experiments.py` now also accepts `--language en` or `--language zh-CN` when summary output should not follow pack auto-detection.
Compact summaries add a raw-sample coverage section so dossier readers can see which experiment sheets already contain usable evidence and which high-priority experiments still have zero samples.

For the compact dossier variant, generate a second summary file:

```bash
python3 "$GAME_REMAKE_RESEARCH/scripts/summarize_experiments.py" \
  --docs-dir ./docs/remake-maplestory \
  --mode compact \
  --output 10-experiment-summary-compact.md
```

Then run `merge_remake_docs.py --mode compact` so the dossier pulls the shorter summary automatically.

Audit a research pack before handoff:

```bash
python3 "$GAME_REMAKE_RESEARCH/scripts/audit_remake_pack.py" \
  --docs-dir ./docs/remake-maplestory
```

Use `--strict` when warnings should also fail CI or handoff gates.
Use `--language en` or `--language zh-CN` to override auto-detected audit output language.
The audit now also warns when generated artifacts are stale relative to newer source docs or CSVs, including experiment summaries, evidence-link reports, status reports, handoff dossiers, and handoff manifests.

Audit evidence-link integrity across ledger, support CSVs, and experiment sheets:

```bash
python3 "$GAME_REMAKE_RESEARCH/scripts/audit_evidence_links.py" \
  --docs-dir ./docs/remake-maplestory \
  --output reports/evidence-link-audit.md
```

Generate a markdown status report for review or takeover:

```bash
python3 "$GAME_REMAKE_RESEARCH/scripts/build_pack_status_report.py" \
  --docs-dir ./docs/remake-maplestory \
  --mode full
```

This writes to `reports/pack-status.md` by default. Use `--mode compact` for a shorter variant.
Use `--mode both` to regenerate both default status-report variants in one run.
When both variants are generated in one run, they now ignore each other during freshness audit so the freshly written pair does not self-report sibling stale warnings.
The report now includes an evidence-traceability snapshot so unknown `S-id`, blank source refs, and missing inline citations are visible without opening the separate audit file.
In `--mode full`, the evidence section also expands into direct tables for unknown source references, blank source-ref rows, unused ledger IDs, and docs missing inline citations.
Evidence findings are now ordered by severity: duplicate or unknown `S-id` blockers first, then blank refs, then citation gaps, then unused ledger cleanup.
Recommended next actions use the same severity ordering and are prefixed with the priority label.
Core-doc placeholder cleanup is also priority-ranked: overview/source-ledger first, then the main analysis docs, then backlog/log tails.
Status and handoff audit findings are now grouped by category: scope/structure, template placeholders, support data, and progress signals.
Stale generated artifacts are surfaced as their own warning group so inherited packs do not quietly ship out-of-date summaries, handoff dossiers, or audit outputs.
The snapshot header now also shows stale-artifact counts directly for experiment summaries, evidence audits, status reports, handoff dossiers, and handoff manifests.
In compact outputs, each issue group now shows the first two items plus a per-group remainder count, instead of dumping the full warning list.
The compact core-document table now shows only the highest-risk files first and adds a folded-count line for the remaining docs.
Compact support, role, archetype, and experiment sections now switch to anomaly-first summaries so takeover readers see missing support rows, blocked roles, archetype gaps, and experiment debt before healthy counts.
When experiment debt remains, the next-action list now cites the first affected experiment IDs directly for plan updates, registry fixes, and raw-sample capture.
When generated artifacts are stale, the next-action list now also tells the reviewer which summaries, audits, or reports should be regenerated first, and single-class stale actions now include the direct repair command.
When multiple generated-artifact classes are stale at the same time, those next actions now collapse into one inferred `build_handoff_bundle.py` command so takeover notes stay short and executable.
Those generated next-action commands assume the shell is already in the pack root, so they consistently use `--docs-dir .`.
When the current generated artifact was intentionally produced in English or Chinese, those next-action commands now preserve that explicit `--language` choice instead of falling back to auto-detection.
If a stale handoff dossier was originally generated with `--include-log`, the repair command now preserves that flag as well.
When experiment-summary refresh depends on archetype metric rollup support, the generated repair command now includes metric rollup first instead of only regenerating the markdown summary.

Build a handoff bundle in one command:

```bash
python3 "$GAME_REMAKE_RESEARCH/scripts/build_handoff_bundle.py" \
  --docs-dir ./docs/remake-maplestory \
  --dossier-mode compact \
  --report-mode both \
  --rollup-metrics
```

This regenerates the needed experiment summary variants, writes the evidence-link audit, writes status reports, builds handoff dossiers, and emits `reports/handoff-bundle.md`.
The handoff manifest also surfaces evidence-link counts directly so reviewers can see source-integrity and citation gaps at a glance.
It now also includes one sample item per evidence problem class, so takeover reviewers can jump straight to the first broken source ID, row, or uncited doc.
Those evidence findings are severity-ranked as well, so blocker-class source-ID failures appear before lower-priority cleanup items.
The handoff `建议下一步` / `Recommended Next Actions` list now follows the same priority ordering.
Placeholder cleanup actions in the handoff list now follow the same logic, prioritizing overview/source-ledger work ahead of lower-value tail docs.
The audit section itself also groups issues by category so structure problems do not get buried under generic placeholder noise.
Compact handoff audits now keep those groups but cap each one to the first two items plus an omitted-count line.
When compact status artifacts are generated as part of the bundle, their support/role/archetype/experiment sections also render as anomaly-first summaries instead of static counters.
Those handoff next actions now also call out concrete experiment IDs when plan, registry, or raw-sample gaps are still blocking evidence collection.
Because the bundle regenerates summaries, evidence audit, and requested status variants before its final audit pass, it now also clears most stale-artifact warnings automatically during handoff packaging.
Its snapshot header now also reports stale-artifact counts directly, including handoff dossier freshness, so reviewers can tell at a glance whether any derivative files remain out of date.

## Common Failure Modes

- Mixing regions, eras, or platforms without labeling them.
- Loading all four archetype templates when one primary lens would do.
- Writing strong conclusions without an experiment plan for the highest-risk unknowns.
- Confusing inferred formulas with confirmed formulas.
- Writing a beautiful deck of opinions that still lacks backlog, risk, or acceptance criteria.
- Describing art direction but not asset categories and reuse strategy.
- Describing feel but not timing, state, cancel, or camera rules.
- Producing architecture prose without clear boundaries, hot paths, or tool implications.

## Check Before You Finish

- Confirm the user can see which version or build the research refers to.
- Confirm each role's output is reflected in the final pack rather than left as raw notes.
- Confirm formulas include units, variables, and assumptions.
- Confirm asset and animation sections describe production-ready categories, not just adjectives.
- Confirm architecture and engineering sections define boundaries, sequencing, and risks.
- Confirm unresolved gaps include a validation plan.
