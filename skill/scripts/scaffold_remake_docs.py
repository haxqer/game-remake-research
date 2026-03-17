#!/usr/bin/env python3
"""Create a remake-research document pack for a target game."""

from __future__ import annotations

import argparse
import csv
import re
from io import StringIO
from pathlib import Path
from textwrap import dedent, indent


ARCHETYPE_CHOICES = ("mmo", "arpg", "roguelike", "card")
ARCHETYPE_FILE_NAME = "07-archetype-specific-template.md"
ARCHETYPE_METRIC_FILE_NAME = "08-archetype-metric-baselines.md"
EXPERIMENT_FILE_NAME = "09-experiment-design.md"
EXPERIMENT_SUMMARY_FILE_NAME = "10-experiment-summary.md"


def evidence_section_block(language: str) -> str:
    if language == "zh-CN":
        return dedent(
            """\
            ## 证据标注规则

            - 在 `Confirmed Facts` 和 `Inferred Model` 中内联写出资料台账 ID，例如 `S-id`。
            - `Remake Decisions` 单独写方案判断；若依赖实验或指标，补 `EXP-id`、指标 ID 或相关 `S-id` 交叉引用。

            ## Confirmed Facts

            ## Inferred Model

            ## Remake Decisions

            ## Open Questions
            """
        )
    return dedent(
        """\
        ## Evidence Tagging

        - Cite ledger IDs inline inside `Confirmed Facts` and `Inferred Model`, for example `S-id`.
        - Keep `Remake Decisions` separate from observed facts; add `EXP-id`, metric IDs, or supporting `S-id` when a decision depends on evidence.

        ## Confirmed Facts

        ## Inferred Model

        ## Remake Decisions

        ## Open Questions
        """
    )


ARCHETYPE_SPECS = {
    "mmo": {
        "display": {"en": "MMO", "zh-CN": "MMO"},
        "reference": "template-mmo.md",
        "summary": {
            "en": "Massively multiplayer lens focused on social dependency, economy durability, content cadence, and service topology.",
            "zh-CN": "MMO 视角，重点关注社交依赖、经济耐久性、内容节奏与服务结构。",
        },
        "must_capture": {
            "en": [
                "World topology: hubs, zones, channels, shards, matchmaking, and instancing.",
                "Social dependency: party roles, guild loops, trade, raids, and how solo play coexists with group play.",
                "Retention spine: daily, weekly, seasonal, expansion, and endgame ladder structure.",
                "Economy pressure: sinks, inflation controls, trade restrictions, and anti-bot assumptions.",
                "Content cadence: how the live game stays alive after the honeymoon period.",
            ],
            "zh-CN": [
                "世界拓扑：主城、地图带、频道、分线、匹配和副本化结构。",
                "社交依赖：组队分工、公会循环、交易、团本，以及单人与多人如何并存。",
                "留存主干：日常、周常、赛季、资料片与终局梯度。",
                "经济压力：货币消耗、通胀控制、交易限制与反外挂假设。",
                "内容节奏：游戏如何在蜜月期之后维持活性。",
            ],
        },
        "extra_outputs": {
            "en": [
                "Social dependency map.",
                "Currency and sink matrix.",
                "Endgame ladder and cadence calendar.",
                "Class or role ecology matrix.",
            ],
            "zh-CN": [
                "社交依赖图。",
                "货币与消耗矩阵。",
                "终局梯度与内容节奏日历。",
                "职业或角色生态矩阵。",
            ],
        },
        "failure_modes": {
            "en": [
                "Copying grind volume without the social or market cushion that made it tolerable.",
                "Flattening multiplayer loops into solo content without replacing the missing motivation.",
                "Ignoring economy leakage, inflation, or content cadence when proposing the remake.",
            ],
            "zh-CN": [
                "照搬刷量，却没有原作的社交或市场缓冲。",
                "把多人循环改成单人后，没有补足新的动机来源。",
                "提出复刻方案时忽视通胀、资源外流或内容节奏。",
            ],
        },
        "checklist_rows": {
            "en": [
                ("world-topology", "Map hubs, zones, channels, shards, and instance boundaries."),
                ("social-loop", "Explain party, guild, trade, raid, and solo coexistence."),
                ("economy-durability", "Document sinks, inflation controls, and trade rules."),
                ("content-cadence", "Capture daily, weekly, seasonal, and endgame cadence."),
            ],
            "zh-CN": [
                ("world-topology", "梳理主城、地图带、频道、分线与副本边界。"),
                ("social-loop", "说明组队、公会、交易、团本与单人并存关系。"),
                ("economy-durability", "记录消耗、通胀控制与交易规则。"),
                ("content-cadence", "记录日常、周常、赛季与终局节奏。"),
            ],
        },
    },
    "arpg": {
        "display": {"en": "ARPG", "zh-CN": "ARPG"},
        "reference": "template-arpg.md",
        "summary": {
            "en": "Action RPG lens focused on combat feel, loot chase, buildcraft, pacing density, and endgame repeatability.",
            "zh-CN": "ARPG 视角，重点关注战斗手感、刷装追求、Build 构筑、节奏密度与终局重复游玩。",
        },
        "must_capture": {
            "en": [
                "Moment-to-moment feel: responsiveness, cancels, hit stop, movement commitment, and camera language.",
                "Loot chase: rarity ladder, affix pools, deterministic crafting, and inventory pressure.",
                "Buildcraft: skill tags, synergies, passive systems, and failure recovery when a build stalls.",
                "Density and pacing: pack size, traversal downtime, burst windows, and boss cadence.",
                "Endgame repeatability: maps, dungeons, ladders, seasonal modifiers, and chase goals.",
            ],
            "zh-CN": [
                "瞬时手感：响应、取消、停顿、位移承诺与镜头语言。",
                "刷装追求：稀有度梯度、词缀池、可控制造与背包压力。",
                "Build 构筑：技能标签、联动、被动系统与卡 Build 后的恢复方式。",
                "密度与节奏：怪群体量、跑图空窗、爆发窗口与 Boss 节奏。",
                "终局重复性：地图、本、梯子、赛季词缀与长期追求。",
            ],
        },
        "extra_outputs": {
            "en": [
                "Skill-tag and affix synergy matrix.",
                "Loot ladder and crafting funnel.",
                "Combat pacing benchmark table.",
                "Endgame loop map.",
            ],
            "zh-CN": [
                "技能标签与词缀联动矩阵。",
                "掉落梯度与制造漏斗。",
                "战斗节奏基准表。",
                "终局循环地图。",
            ],
        },
        "failure_modes": {
            "en": [
                "Copying loot color tiers while missing the actual chase structure.",
                "Under-specifying combat timings, making the remake feel floaty or stiff.",
                "Designing endgame as a content list instead of a repeatable reward loop.",
            ],
            "zh-CN": [
                "只抄稀有度颜色，没有抄到真正的追求结构。",
                "战斗时序定义不够，导致手感发飘或发硬。",
                "把终局写成内容清单，而不是可循环的奖励结构。",
            ],
        },
        "checklist_rows": {
            "en": [
                ("combat-feel", "Capture responsiveness, cancels, hit pause, and movement commitment."),
                ("loot-chase", "Document rarity tiers, affixes, crafting, and inventory pressure."),
                ("buildcraft", "Map skill tags, passive layers, synergies, and reset costs."),
                ("endgame-loop", "Describe repeatable endgame structures and chase goals."),
            ],
            "zh-CN": [
                ("combat-feel", "记录响应、取消、停顿与移动承诺。"),
                ("loot-chase", "记录稀有度、词缀、制造与背包压力。"),
                ("buildcraft", "梳理技能标签、被动层、联动与重置成本。"),
                ("endgame-loop", "描述可重复终局结构与长期追求。"),
            ],
        },
    },
    "roguelike": {
        "display": {"en": "Roguelike", "zh-CN": "Roguelike"},
        "reference": "template-roguelike.md",
        "summary": {
            "en": "Run-based lens focused on randomness governance, run rhythm, fail-forward structure, and meta progression boundaries.",
            "zh-CN": "Roguelike 视角，重点关注随机性治理、单局节奏、失败前进结构与 Meta 成长边界。",
        },
        "must_capture": {
            "en": [
                "Run rhythm: floor structure, biome cadence, encounter escalation, and recovery moments.",
                "Randomness governance: seed surfaces, draft pools, reward weighting, and anti-brick measures.",
                "Failure meaning: what a loss teaches, what carries over, and how the player re-enters.",
                "Meta progression boundaries: permanent unlocks, power creep limits, and mastery versus grind.",
                "Build pivots: when and how a run can change direction without collapsing.",
            ],
            "zh-CN": [
                "单局节奏：层级结构、区域节奏、遭遇升级与恢复节点。",
                "随机性治理：种子作用面、奖励池、权重与防卡死机制。",
                "失败意义：失败教会什么、保留什么、如何重新进入。",
                "Meta 成长边界：永久解锁、强度上限与技术成长和 grind 的关系。",
                "Build 转向：一局中何时、如何换方向而不直接崩盘。",
            ],
        },
        "extra_outputs": {
            "en": [
                "Run structure timeline.",
                "Reward-draft and anti-brick matrix.",
                "Meta progression cap table.",
                "Seed or RNG surface inventory.",
            ],
            "zh-CN": [
                "单局结构时间线。",
                "奖励选择与防卡死矩阵。",
                "Meta 成长上限表。",
                "种子或 RNG 作用面清单。",
            ],
        },
        "failure_modes": {
            "en": [
                "Confusing randomness volume with meaningful variance.",
                "Letting meta progression overpower run-to-run mastery.",
                "Removing recovery windows and making every bad roll unrecoverable.",
            ],
            "zh-CN": [
                "把随机量误当成有效变化。",
                "让 Meta 成长压过单局技术成长。",
                "没有恢复窗口，导致一次坏随机就不可挽回。",
            ],
        },
        "checklist_rows": {
            "en": [
                ("run-rhythm", "Map floor cadence, biome pacing, escalation, and rest points."),
                ("rng-governance", "Record seeds, reward weighting, and anti-brick measures."),
                ("meta-progression", "Explain carryover, unlocks, caps, and reset friction."),
                ("build-pivot", "Document how runs pivot and recover from weak starts."),
            ],
            "zh-CN": [
                ("run-rhythm", "梳理层级节奏、区域推进与休整点。"),
                ("rng-governance", "记录种子、奖励权重与防卡死措施。"),
                ("meta-progression", "说明继承项、解锁、上限与重开成本。"),
                ("build-pivot", "记录单局如何转向与从弱开局恢复。"),
            ],
        },
    },
    "card": {
        "display": {"en": "Card Game", "zh-CN": "卡牌"},
        "reference": "template-card.md",
        "summary": {
            "en": "Card-game lens focused on rules clarity, timing windows, resource curve, card-pool ecology, and matchup health.",
            "zh-CN": "卡牌视角，重点关注规则清晰度、时点窗口、资源曲线、卡池生态与对局健康度。",
        },
        "must_capture": {
            "en": [
                "Rules engine: turn structure, phases, timing windows, stack or resolution order, and hidden information rules.",
                "Resource curve: mana, energy, tempo, draw smoothing, mulligan, and snowball controls.",
                "Card ecology: card types, copy limits, keyword systems, archetypes, and hate or tech answers.",
                "Collection or drafting loop: acquisition, crafting, rarity, rotation, and onboarding deck quality.",
                "Readability: board state clarity, log visibility, targeting rules, and mobile or PC information density.",
            ],
            "zh-CN": [
                "规则引擎：回合结构、阶段、时点窗口、结算顺序与隐藏信息规则。",
                "资源曲线：法力、能量、节奏、过牌平滑、起手调度与滚雪球控制。",
                "卡池生态：卡类型、同名上限、关键字系统、流派以及针对牌。",
                "收集或 Draft 循环：获取、制造、稀有度、轮替与新手初始卡组质量。",
                "可读性：场面信息清晰度、日志可见性、指向规则与移动端或 PC 信息密度。",
            ],
        },
        "extra_outputs": {
            "en": [
                "Turn-state diagram.",
                "Keyword glossary and timing reference.",
                "Resource-curve target table.",
                "Archetype and matchup matrix.",
            ],
            "zh-CN": [
                "回合状态图。",
                "关键字术语表与时点说明。",
                "资源曲线目标表。",
                "流派与对局矩阵。",
            ],
        },
        "failure_modes": {
            "en": [
                "Copying card fantasy without reconstructing a precise rules engine.",
                "Leaving timing windows implicit and creating ambiguous interactions.",
                "Ignoring collection friction or onboarding deck quality when remaking a live card game.",
            ],
            "zh-CN": [
                "只抄卡牌概念，没有重建严谨的规则引擎。",
                "时点窗口含糊，导致交互歧义。",
                "复刻在线卡牌时忽视卡池获取阻力或新手卡组质量。",
            ],
        },
        "checklist_rows": {
            "en": [
                ("rules-engine", "Define phases, timing windows, resolution order, and hidden information."),
                ("resource-curve", "Document mana or energy curve, mulligan, draw smoothing, and anti-snowball."),
                ("card-ecology", "Map card types, keywords, copy limits, archetypes, and tech answers."),
                ("collection-loop", "Explain acquisition, crafting, rarity, rotation, and onboarding deck quality."),
            ],
            "zh-CN": [
                ("rules-engine", "定义阶段、时点窗口、结算顺序与隐藏信息。"),
                ("resource-curve", "记录资源曲线、调度、过牌平滑与反滚雪球。"),
                ("card-ecology", "梳理卡类型、关键字、同名上限、流派与针对牌。"),
                ("collection-loop", "说明获取、制造、稀有度、轮替与新手卡组质量。"),
            ],
        },
    },
}

ARCHETYPE_METRICS = {
    "mmo": {
        "reference": "metrics-mmo.md",
        "rows": {
            "en": [
                (
                    "MMO-M1",
                    "retention-cadence",
                    "Daily route completion time",
                    "minutes/session",
                    "Time a representative mandatory daily route from login to completion.",
                    "Measures daily burden and long-term fatigue risk.",
                ),
                (
                    "MMO-M2",
                    "social-gating",
                    "Time to first mandatory group gate",
                    "hours-to-unlock",
                    "Record when solo progress first meaningfully stalls without party, guild, or raid access.",
                    "Shows how much the product depends on social progression rather than solo persistence.",
                ),
                (
                    "MMO-M3",
                    "economy-durability",
                    "Mandatory sink pressure",
                    "percent-of-gross-currency",
                    "Estimate required sinks as a share of gross currency earned in a representative progression band.",
                    "Reveals whether the economy survives without runaway inflation.",
                ),
                (
                    "MMO-M4",
                    "trade-reliance",
                    "Market dependency for progression-critical upgrades",
                    "percent-of-upgrades",
                    "Sample how many meaningful upgrades are realistically sourced through trade or services.",
                    "Important when converting an online economy into a self-sufficient remake.",
                ),
                (
                    "MMO-M5",
                    "reset-structure",
                    "Major reset cadence",
                    "days/reset",
                    "Record daily, weekly, and seasonal reset intervals tied to progression or rewards.",
                    "Defines the live-service rhythm the remake must preserve or replace.",
                ),
            ],
            "zh-CN": [
                (
                    "MMO-M1",
                    "retention-cadence",
                    "日常完成时长",
                    "minutes/session",
                    "计时一条代表性的必做日常路径，从登录到完成。",
                    "用于衡量日课负担和长期疲劳风险。",
                ),
                (
                    "MMO-M2",
                    "social-gating",
                    "首次强制组队门槛时间",
                    "hours-to-unlock",
                    "记录单人推进首次明显受阻、必须依赖组队、公会或团本的时间点。",
                    "用于判断产品对社交推进的依赖程度。",
                ),
                (
                    "MMO-M3",
                    "economy-durability",
                    "刚性消耗压力",
                    "percent-of-gross-currency",
                    "估算代表性成长分段里，刚性消耗占总货币产出的比例。",
                    "用于判断经济系统是否具备抗通胀能力。",
                ),
                (
                    "MMO-M4",
                    "trade-reliance",
                    "关键成长对交易的依赖度",
                    "percent-of-upgrades",
                    "抽样统计有意义升级中，多少必须或主要依赖交易、代工或服务获得。",
                    "在做单机化或去交易改造时尤其关键。",
                ),
                (
                    "MMO-M5",
                    "reset-structure",
                    "核心重置节奏",
                    "days/reset",
                    "记录与成长强绑定的日更、周更和赛季重置周期。",
                    "决定复刻后要保留还是替代的内容节奏骨架。",
                ),
            ],
        },
    },
    "arpg": {
        "reference": "metrics-arpg.md",
        "rows": {
            "en": [
                (
                    "ARPG-M1",
                    "combat-tempo",
                    "Representative farming loop duration",
                    "minutes/run",
                    "Time one representative map, dungeon, or farming route from start to reward resolution.",
                    "Defines repeatability and session pacing.",
                ),
                (
                    "ARPG-M2",
                    "density",
                    "Average combat pack density",
                    "enemies/engagement",
                    "Sample average enemies per meaningful engagement across a representative route.",
                    "Tracks whether the remake preserves tempo and crowd pressure.",
                ),
                (
                    "ARPG-M3",
                    "power-spike",
                    "Time to first meaningful build spike",
                    "minutes-or-levels",
                    "Record when the build first gains a clearly felt jump in clear speed or survivability.",
                    "Measures onboarding excitement and early retention.",
                ),
                (
                    "ARPG-M4",
                    "loot-chase",
                    "Meaningful upgrade frequency",
                    "upgrades/hour",
                    "Count drops, crafts, or rerolls that materially improve the current build over a representative hour.",
                    "Shows whether loot chase feels alive or dry.",
                ),
                (
                    "ARPG-M5",
                    "build-friction",
                    "Respec or build pivot cost",
                    "currency-plus-minutes",
                    "Record the full cost to pivot into another viable build path.",
                    "Controls experimentation and failure recovery.",
                ),
            ],
            "zh-CN": [
                (
                    "ARPG-M1",
                    "combat-tempo",
                    "代表性刷图循环时长",
                    "minutes/run",
                    "计时一张代表性地图、本或刷装路线，从进入到奖励结算。",
                    "用于定义重复刷图的节奏与单局时长。",
                ),
                (
                    "ARPG-M2",
                    "density",
                    "平均战斗密度",
                    "enemies/engagement",
                    "在代表性路线中抽样每次有效交战的平均敌人数。",
                    "用于判断复刻后是否保住原作的节奏和压迫感。",
                ),
                (
                    "ARPG-M3",
                    "power-spike",
                    "首次显著强度跃迁时间",
                    "minutes-or-levels",
                    "记录 Build 首次明显提升清图效率或生存的时间点。",
                    "用于衡量前期兴奋点和早期留存。",
                ),
                (
                    "ARPG-M4",
                    "loot-chase",
                    "有效升级出现频率",
                    "upgrades/hour",
                    "统计一小时内，能实质提升当前 Build 的掉落、制造或重铸次数。",
                    "用于判断刷装追求是否持续有反馈。",
                ),
                (
                    "ARPG-M5",
                    "build-friction",
                    "重置或转 Build 成本",
                    "currency-plus-minutes",
                    "记录切换到另一条可玩 Build 所需的总货币与时间成本。",
                    "用于评估尝试空间和失败恢复成本。",
                ),
            ],
        },
    },
    "roguelike": {
        "reference": "metrics-roguelike.md",
        "rows": {
            "en": [
                (
                    "ROGUE-M1",
                    "run-rhythm",
                    "Full run duration",
                    "minutes/run",
                    "Time a representative successful run from start to ending or victory screen.",
                    "Defines session expectation and pacing envelope.",
                ),
                (
                    "ROGUE-M2",
                    "decision-density",
                    "Meaningful choice interval",
                    "minutes/decision",
                    "Measure time between draft, shop, pathing, or loadout decisions that materially change the run.",
                    "Shows whether the run has enough agency between fights.",
                ),
                (
                    "ROGUE-M3",
                    "recovery-structure",
                    "Recovery node frequency",
                    "count/run",
                    "Count heal, shop, rest, reroll, or bailout opportunities in a representative run.",
                    "Reveals how forgiving the structure is after bad luck or mistakes.",
                ),
                (
                    "ROGUE-M4",
                    "anti-brick",
                    "Pre-boss anti-brick opportunities",
                    "count-before-first-boss",
                    "Count guaranteed or likely systems that rescue weak starts before the first major gate.",
                    "Important for preventing dead runs that feel predetermined.",
                ),
                (
                    "ROGUE-M5",
                    "re-entry",
                    "Loss-to-retry time",
                    "seconds/retry",
                    "Measure time from failure screen to regained player control in a fresh run.",
                    "Defines how painful failure feels and how fast mastery loops restart.",
                ),
            ],
            "zh-CN": [
                (
                    "ROGUE-M1",
                    "run-rhythm",
                    "完整单局时长",
                    "minutes/run",
                    "计时一局代表性的成功通关流程，从开始到结算。",
                    "用于定义单局期望和整体节奏包络。",
                ),
                (
                    "ROGUE-M2",
                    "decision-density",
                    "有效决策间隔",
                    "minutes/decision",
                    "测量一次会实质改变本局走向的选牌、商店、路线或配置决策之间的时间间隔。",
                    "用于判断战斗之间是否保有足够的策略能动性。",
                ),
                (
                    "ROGUE-M3",
                    "recovery-structure",
                    "恢复节点频率",
                    "count/run",
                    "统计一局中的治疗、商店、休整、重掷或保底机会次数。",
                    "用于判断坏运气或失误后的恢复空间。",
                ),
                (
                    "ROGUE-M4",
                    "anti-brick",
                    "首个 Boss 前防卡死机会数",
                    "count-before-first-boss",
                    "统计首个重大门槛前，系统提供的保底或救场机会。",
                    "用于防止一局在早期就被判死刑。",
                ),
                (
                    "ROGUE-M5",
                    "re-entry",
                    "失败后重开时长",
                    "seconds/retry",
                    "测量失败结算到重新获得操作权之间的时间。",
                    "决定失败的痛感和精通循环的重启速度。",
                ),
            ],
        },
    },
    "card": {
        "reference": "metrics-card.md",
        "rows": {
            "en": [
                (
                    "CARD-M1",
                    "turn-pace",
                    "Median turn duration",
                    "seconds/turn",
                    "Sample representative early, mid, and late-game turns across multiple matches.",
                    "Defines readability pressure and match flow.",
                ),
                (
                    "CARD-M2",
                    "resource-curve",
                    "Turns to primary resource cap or decisive power turn",
                    "turns",
                    "Record when the game reaches full resource availability or a consistent game-ending tempo point.",
                    "Maps pacing and comeback bandwidth.",
                ),
                (
                    "CARD-M3",
                    "opening-consistency",
                    "Mulligan flexibility",
                    "cards-or-redraw-options",
                    "Document how many cards or choices the opening hand system allows the player to smooth.",
                    "Directly affects non-games and opening variance.",
                ),
                (
                    "CARD-M4",
                    "meta-health",
                    "Top archetype share",
                    "percent-of-sample",
                    "Estimate the share of observed matches or top lists occupied by the leading archetype.",
                    "Provides a baseline for matchup diversity and meta concentration.",
                ),
                (
                    "CARD-M5",
                    "onboarding",
                    "Starter deck performance gap",
                    "estimated-winrate-gap",
                    "Estimate the performance gap between onboarding decks and the live field or intended baseline opponents.",
                    "Shows whether the collection loop supports or repels new players.",
                ),
            ],
            "zh-CN": [
                (
                    "CARD-M1",
                    "turn-pace",
                    "回合中位时长",
                    "seconds/turn",
                    "抽样统计多个对局中前中后期代表性回合的耗时。",
                    "用于定义信息压力和对局流速。",
                ),
                (
                    "CARD-M2",
                    "resource-curve",
                    "到达资源上限或决胜强度回合的轮次",
                    "turns",
                    "记录资源进入满档，或稳定进入终结节奏的典型回合数。",
                    "用于映射节奏、翻盘空间和比赛长度。",
                ),
                (
                    "CARD-M3",
                    "opening-consistency",
                    "起手调度灵活度",
                    "cards-or-redraw-options",
                    "记录起手系统允许玩家调平曲线的换牌张数或选择次数。",
                    "直接影响非对局和开局方差。",
                ),
                (
                    "CARD-M4",
                    "meta-health",
                    "头部流派占比",
                    "percent-of-sample",
                    "估算观测样本中，头部流派在对局或卡组榜单中的占比。",
                    "用于建立对局多样性和环境集中度基线。",
                ),
                (
                    "CARD-M5",
                    "onboarding",
                    "新手卡组性能差距",
                    "estimated-winrate-gap",
                    "估算初始卡组与环境平均或基准对手之间的性能差距。",
                    "用于判断收集循环对新玩家是支撑还是劝退。",
                ),
            ],
        },
    },
}

ARCHETYPE_METRIC_LINKS = {
    "mmo": [
        (
            "MMO-M1",
            "EXP-02",
            "data/experiments/route-density-sample.csv",
            "duration_minutes",
            "numeric_band",
            "suggested",
            "Auto-roll route duration into daily route baseline when the sampled route is progression-representative.",
        ),
        (
            "MMO-M2",
            "",
            "",
            "",
            "manual",
            "manual",
            "Requires interpretation from progression-band-map and source review.",
        ),
        (
            "MMO-M3",
            "EXP-03",
            "data/experiments/economy-sampling.csv",
            "mandatory_sink;gross_input",
            "ratio_band",
            "suggested",
            "Compute mandatory sink pressure as mandatory_sink / gross_input.",
        ),
        (
            "MMO-M4",
            "",
            "",
            "",
            "manual",
            "manual",
            "Requires trade and market observations beyond the default experiment templates.",
        ),
        (
            "MMO-M5",
            "",
            "",
            "",
            "manual",
            "manual",
            "Usually sourced from service cadence and reset documentation.",
        ),
    ],
    "arpg": [
        (
            "ARPG-M1",
            "EXP-02",
            "data/experiments/route-density-sample.csv",
            "duration_minutes",
            "numeric_band",
            "suggested",
            "Auto-roll representative route duration into farming loop duration.",
        ),
        (
            "ARPG-M2",
            "EXP-02",
            "data/experiments/route-density-sample.csv",
            "enemy_count;engagement_count",
            "ratio_band",
            "suggested",
            "Compute average pack density as enemy_count / engagement_count.",
        ),
        (
            "ARPG-M3",
            "",
            "",
            "",
            "manual",
            "manual",
            "Requires progression-band or build-spike interpretation.",
        ),
        (
            "ARPG-M4",
            "",
            "",
            "",
            "manual",
            "manual",
            "Requires item-upgrade relevance judgment, not just raw event counts.",
        ),
        (
            "ARPG-M5",
            "",
            "",
            "",
            "manual",
            "manual",
            "Requires respec or build pivot cost sampling.",
        ),
    ],
    "roguelike": [
        (
            "ROGUE-M1",
            "",
            "",
            "",
            "manual",
            "manual",
            "Requires dedicated run-duration sampling.",
        ),
        (
            "ROGUE-M2",
            "",
            "",
            "",
            "manual",
            "manual",
            "Requires decision-interval sampling from run logs.",
        ),
        (
            "ROGUE-M3",
            "",
            "",
            "",
            "manual",
            "manual",
            "Requires recovery-node counting in progression or run-state logs.",
        ),
        (
            "ROGUE-M4",
            "",
            "",
            "",
            "manual",
            "manual",
            "Requires anti-brick event counting before the first major gate.",
        ),
        (
            "ROGUE-M5",
            "EXP-07",
            "data/experiments/failure-reentry.csv",
            "time_to_reentry_seconds",
            "numeric_band",
            "suggested",
            "Auto-roll failure-to-reentry timings into retry-speed baseline.",
        ),
    ],
    "card": [
        (
            "CARD-M1",
            "",
            "",
            "",
            "manual",
            "manual",
            "Requires turn-timing samples from state logs or match logs.",
        ),
        (
            "CARD-M2",
            "",
            "",
            "",
            "manual",
            "manual",
            "Requires turn-curve sampling from match logs.",
        ),
        (
            "CARD-M3",
            "",
            "",
            "",
            "manual",
            "manual",
            "Requires explicit mulligan-system sampling.",
        ),
        (
            "CARD-M4",
            "",
            "",
            "",
            "manual",
            "manual",
            "Requires meta-share sampling from decklists or match populations.",
        ),
        (
            "CARD-M5",
            "",
            "",
            "",
            "manual",
            "manual",
            "Requires onboarding deck performance measurement.",
        ),
    ],
}

EXPERIMENT_SPECS = {
    "en": [
        (
            "EXP-01",
            "timing-capture",
            "Timing window capture",
            "mmo|arpg|roguelike",
            "frames-or-ms",
            "3-10 representative actions",
            "Count anticipation, active, recovery, interrupt, and cancel windows from representative clips.",
            "Turns vague feel into reproducible timing rules.",
        ),
        (
            "EXP-02",
            "route-density-sample",
            "Route and density sample",
            "mmo|arpg",
            "minutes-and-enemies",
            "3 representative routes",
            "Measure route duration, enemy density, downtime, and reward completion on representative farming paths.",
            "Captures loop tempo, traversal burden, and content efficiency.",
        ),
        (
            "EXP-03",
            "economy-sampling",
            "Faucet and sink sample",
            "all",
            "currency-plus-items",
            "10-30 observations",
            "Sample gross inputs, mandatory sinks, optional sinks, and recovery paths within a bounded progression band.",
            "Prevents fake economy models based on reward screenshots alone.",
        ),
        (
            "EXP-04",
            "progression-band-map",
            "Progression band mapping",
            "all",
            "bands-or-stages",
            "full onboarding to endgame pass",
            "Map gate conditions, dominant loop, new unlocks, and obsolete loops per progression band.",
            "Preserves pacing, not just feature inventory.",
        ),
        (
            "EXP-05",
            "onboarding-funnel",
            "Onboarding funnel observation",
            "all",
            "steps-and-minutes",
            "first 10-60 minutes",
            "Track first-session goals, blocking prompts, system reveals, friction points, and first strong payoff.",
            "Shows whether the remake can recreate the original first-session hook.",
        ),
        (
            "EXP-06",
            "ui-flow-count",
            "UI flow step count",
            "all",
            "steps-per-task",
            "5-10 critical tasks",
            "Count entry points, clicks or inputs, confirmation states, and back-navigation behavior for core UI tasks.",
            "Converts interface quality into measurable friction.",
        ),
        (
            "EXP-07",
            "failure-reentry",
            "Failure-to-reentry timing",
            "mmo|arpg|roguelike|card",
            "seconds-to-control",
            "3-5 representative failures",
            "Measure time from failure, loss, or wipe to restored player agency in a new attempt.",
            "Quantifies how punitive failure feels and how fast mastery loops restart.",
        ),
        (
            "EXP-08",
            "state-log",
            "Encounter or match state log",
            "mmo|arpg|roguelike|card",
            "state-snapshots",
            "5-10 representative scenarios",
            "Record key state transitions, visible information, decision points, and resolution outcomes in a structured log.",
            "Supports exact reconstruction of rules, encounters, and readability loads.",
        ),
    ],
    "zh-CN": [
        (
            "EXP-01",
            "timing-capture",
            "时序窗口采样",
            "mmo|arpg|roguelike",
            "frames-or-ms",
            "3-10 representative actions",
            "从代表性片段中统计前摇、生效、后摇、打断与取消窗口。",
            "把模糊的手感描述转成可复现的时序规则。",
        ),
        (
            "EXP-02",
            "route-density-sample",
            "路线与密度采样",
            "mmo|arpg",
            "minutes-and-enemies",
            "3 representative routes",
            "测量代表性刷图路线的总时长、怪物密度、空跑时间与奖励结算。",
            "用于捕捉循环节奏、跑图负担和内容效率。",
        ),
        (
            "EXP-03",
            "economy-sampling",
            "产出与消耗采样",
            "all",
            "currency-plus-items",
            "10-30 observations",
            "在限定成长分段内抽样总产出、刚性消耗、可选消耗和恢复路径。",
            "防止只看奖励截图就臆造经济模型。",
        ),
        (
            "EXP-04",
            "progression-band-map",
            "成长分段映射",
            "all",
            "bands-or-stages",
            "full onboarding to endgame pass",
            "梳理每个成长分段的门槛条件、主导循环、新解锁与被淘汰循环。",
            "保留的是节奏结构，而不只是功能清单。",
        ),
        (
            "EXP-05",
            "onboarding-funnel",
            "新手漏斗观察",
            "all",
            "steps-and-minutes",
            "first 10-60 minutes",
            "记录首局目标、阻断提示、系统揭示、摩擦点和第一次强反馈。",
            "用于判断复刻能否复现原作首小时抓力。",
        ),
        (
            "EXP-06",
            "ui-flow-count",
            "UI 流程步数统计",
            "all",
            "steps-per-task",
            "5-10 critical tasks",
            "统计核心 UI 任务的入口、点击或输入次数、确认状态和返回行为。",
            "把界面质量转成可比较的摩擦成本。",
        ),
        (
            "EXP-07",
            "failure-reentry",
            "失败到重开时长",
            "mmo|arpg|roguelike|card",
            "seconds-to-control",
            "3-5 representative failures",
            "测量失败、团灭或败北后，到重新获得操作权之间的时间。",
            "量化失败惩罚感和精通循环重启速度。",
        ),
        (
            "EXP-08",
            "state-log",
            "遭遇或对局状态记录",
            "mmo|arpg|roguelike|card",
            "state-snapshots",
            "5-10 representative scenarios",
            "结构化记录关键状态变化、可见信息、决策点和结算结果。",
            "支持精确复原规则、遭遇结构和可读性负荷。",
        ),
    ],
}

EXPERIMENT_DETAIL_TEMPLATES = {
    "EXP-01": {
        "file": "data/experiments/timing-capture.csv",
        "header": [
            "experiment_id",
            "sample_id",
            "source_id",
            "action_name",
            "clip_or_timestamp",
            "anticipation_frames",
            "active_frames",
            "recovery_frames",
            "interrupt_rule",
            "cancel_rule",
            "confidence",
            "notes",
        ],
        "sample": [
            "EXP-01",
            "TIMING-001",
            "S1",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "Open",
            "",
        ],
    },
    "EXP-02": {
        "file": "data/experiments/route-density-sample.csv",
        "header": [
            "experiment_id",
            "sample_id",
            "source_id",
            "route_name",
            "context_band",
            "duration_minutes",
            "enemy_count",
            "engagement_count",
            "downtime_seconds",
            "reward_summary",
            "confidence",
            "notes",
        ],
        "sample": [
            "EXP-02",
            "ROUTE-001",
            "S1",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "Open",
            "",
        ],
    },
    "EXP-03": {
        "file": "data/experiments/economy-sampling.csv",
        "header": [
            "experiment_id",
            "sample_id",
            "source_id",
            "progression_band",
            "input_type",
            "gross_input",
            "mandatory_sink",
            "optional_sink",
            "recovery_path",
            "net_result",
            "confidence",
            "notes",
        ],
        "sample": [
            "EXP-03",
            "ECON-001",
            "S1",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "Open",
            "",
        ],
    },
    "EXP-04": {
        "file": "data/experiments/progression-band-map.csv",
        "header": [
            "experiment_id",
            "band_id",
            "source_id",
            "entry_condition",
            "dominant_loop",
            "new_unlocks",
            "obsolete_loops",
            "exit_condition",
            "confidence",
            "notes",
        ],
        "sample": [
            "EXP-04",
            "BAND-001",
            "S1",
            "",
            "",
            "",
            "",
            "",
            "Open",
            "",
        ],
    },
    "EXP-05": {
        "file": "data/experiments/onboarding-funnel.csv",
        "header": [
            "experiment_id",
            "step_id",
            "source_id",
            "time_from_start_seconds",
            "player_goal",
            "system_reveal",
            "friction_point",
            "payoff",
            "confidence",
            "notes",
        ],
        "sample": [
            "EXP-05",
            "ONBOARD-001",
            "S1",
            "",
            "",
            "",
            "",
            "",
            "Open",
            "",
        ],
    },
    "EXP-06": {
        "file": "data/experiments/ui-flow-count.csv",
        "header": [
            "experiment_id",
            "task_id",
            "source_id",
            "entry_point",
            "input_steps",
            "confirmation_steps",
            "backtrack_steps",
            "blocking_prompts",
            "completion_state",
            "confidence",
            "notes",
        ],
        "sample": [
            "EXP-06",
            "UIFLOW-001",
            "S1",
            "",
            "",
            "",
            "",
            "",
            "",
            "Open",
            "",
        ],
    },
    "EXP-07": {
        "file": "data/experiments/failure-reentry.csv",
        "header": [
            "experiment_id",
            "sample_id",
            "source_id",
            "failure_type",
            "context_or_timestamp",
            "time_to_reentry_seconds",
            "retained_progress",
            "penalty_summary",
            "confidence",
            "notes",
        ],
        "sample": [
            "EXP-07",
            "FAIL-001",
            "S1",
            "",
            "",
            "",
            "",
            "",
            "Open",
            "",
        ],
    },
    "EXP-08": {
        "file": "data/experiments/state-log.csv",
        "header": [
            "experiment_id",
            "sample_id",
            "source_id",
            "state_index",
            "state_name",
            "visible_information",
            "decision_point",
            "resolution_outcome",
            "confidence",
            "notes",
        ],
        "sample": [
            "EXP-08",
            "STATE-001",
            "S1",
            "1",
            "",
            "",
            "",
            "",
            "Open",
            "",
        ],
    },
}

ARCHETYPE_EXPERIMENT_PRIORITIES = {
    "mmo": {
        "EXP-01": "medium",
        "EXP-02": "high",
        "EXP-03": "high",
        "EXP-04": "high",
        "EXP-05": "medium",
        "EXP-06": "medium",
        "EXP-07": "medium",
        "EXP-08": "high",
    },
    "arpg": {
        "EXP-01": "high",
        "EXP-02": "high",
        "EXP-03": "medium",
        "EXP-04": "medium",
        "EXP-05": "medium",
        "EXP-06": "low",
        "EXP-07": "medium",
        "EXP-08": "high",
    },
    "roguelike": {
        "EXP-01": "high",
        "EXP-02": "low",
        "EXP-03": "medium",
        "EXP-04": "high",
        "EXP-05": "medium",
        "EXP-06": "low",
        "EXP-07": "high",
        "EXP-08": "high",
    },
    "card": {
        "EXP-01": "low",
        "EXP-02": "low",
        "EXP-03": "medium",
        "EXP-04": "medium",
        "EXP-05": "high",
        "EXP-06": "high",
        "EXP-07": "medium",
        "EXP-08": "high",
    },
}

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "game"


def render_csv(rows: list[list[str]]) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerows(rows)
    return buffer.getvalue()


def format_version_scope(version_scope: str | None, language: str) -> str:
    if version_scope:
        return version_scope
    if language == "zh-CN":
        return "待确认版本 / 区服 / 平台 / 时间切片"
    return "TBD version / region / platform / time slice"


def archetype_display(archetype: str | None, language: str) -> str:
    if not archetype:
        return "未指定" if language == "zh-CN" else "Not set"
    return ARCHETYPE_SPECS[archetype]["display"][language]


def archetype_scope_line(archetype: str | None, language: str) -> str:
    label = archetype_display(archetype, language)
    if language == "zh-CN":
        return f"- 品类模板: `{label}`"
    return f"- Archetype lens: `{label}`"


def build_documents(
    game: str, version_scope: str, language: str, archetype: str | None
) -> dict[str, str]:
    if language == "zh-CN":
        return build_documents_zh(game, version_scope, archetype)
    return build_documents_en(game, version_scope, archetype)


def build_support_files(
    game: str, version_scope: str, language: str, archetype: str | None
) -> dict[str, str]:
    if language == "zh-CN":
        return build_support_files_zh(game, version_scope, archetype)
    return build_support_files_en(game, version_scope, archetype)


def build_single_file_template(
    game: str, version_scope: str, language: str, archetype: str | None
) -> dict[str, str]:
    archetype_line = archetype_scope_line(archetype, language)

    if language == "zh-CN":
        lines = [
            f"# {game} 复刻总文档",
            "",
            f"- 目标游戏: `{game}`",
            f"- 基线版本: `{version_scope}`",
            f"{archetype_line}",
            "- 输出形态: 单文档",
            "",
            "## 使用说明",
            "",
            "- 将多文件调研结果按交付顺序合并到本文件。",
            "- 保留每节中的 `Confirmed Facts`、`Inferred Model`、`Remake Decisions`、`Open Questions`。",
            "- 在 `Confirmed Facts` 和 `Inferred Model` 中内联写出 `S-id` 台账锚点。",
            "- 若已有多文件成果，优先使用 `merge_remake_docs.py` 自动合并。",
            "",
            "## 目录",
            "",
            "1. 总览与资料台账",
            "2. 产品与玩家体验",
            "3. 系统与玩法",
            "4. 经济与数值",
            "5. 内容、美术、音频与叙事",
            "6. 客户端架构与制作计划",
            "7. 复刻待办与验收",
        ]
        if archetype:
            lines.extend(["8. 品类细分模板", "9. 品类量化指标基线", "10. 调研日志"])
        else:
            lines.append("8. 调研日志")
        return {"remake-dossier.md": "\n".join(lines).rstrip() + "\n"}

    lines = [
        f"# {game} Remake Dossier",
        "",
        f"- Target game: `{game}`",
        f"- Baseline version: `{version_scope}`",
        f"{archetype_line}",
        "- Output shape: single document",
        "",
        "## Usage",
        "",
        "- Merge the multi-file research pack into this dossier in deliverable order.",
        "- Preserve `Confirmed Facts`, `Inferred Model`, `Remake Decisions`, and `Open Questions` in every major section.",
        "- Cite inline ledger anchors like `S-id` inside `Confirmed Facts` and `Inferred Model`.",
        "- If the research already exists as separate files, prefer `merge_remake_docs.py`.",
        "",
        "## Contents",
        "",
        "1. Overview and source ledger",
        "2. Product and player experience",
        "3. Systems and gameplay",
        "4. Economy and balance",
        "5. Content, art, audio, and narrative",
        "6. Client architecture and production",
        "7. Replica backlog and acceptance",
    ]
    if archetype:
        lines.extend(
            [
                "8. Archetype-specific template",
                "9. Archetype metric baselines",
                "10. Research log",
            ]
        )
    else:
        lines.append("8. Research log")
    return {"remake-dossier.md": "\n".join(lines).rstrip() + "\n"}


def build_archetype_file(
    game: str, language: str, archetype: str | None
) -> dict[str, str]:
    if not archetype:
        return {}

    spec = ARCHETYPE_SPECS[archetype]
    display = spec["display"][language]
    summary = spec["summary"][language]
    reference = spec["reference"]
    metrics_reference = ARCHETYPE_METRICS[archetype]["reference"]
    evidence_block = evidence_section_block(language)
    must_capture = "\n".join(f"- {item}" for item in spec["must_capture"][language])
    extra_outputs = "\n".join(f"- {item}" for item in spec["extra_outputs"][language])
    failure_modes = "\n".join(f"- {item}" for item in spec["failure_modes"][language])

    if language == "zh-CN":
        content = f"""\
# {game} {display} 细分模板

## 品类镜头

- 品类模板: `{display}`
- 参考文件: `references/{reference}`
- 指标参考: `references/{metrics_reference}`
- 关注摘要: {summary}

## 必答问题

{must_capture}

## 建议追加产出

{extra_outputs}

## 常见误判

{failure_modes}

{evidence_block}
"""
    else:
        content = f"""\
# {game} {display} Archetype Template

## Lens

- Archetype: `{display}`
- Reference file: `references/{reference}`
- Metric reference: `references/{metrics_reference}`
- Focus summary: {summary}

## Must Answer

{must_capture}

## Additional Outputs

{extra_outputs}

## Common Failure Modes

{failure_modes}

{evidence_block}
"""

    return {ARCHETYPE_FILE_NAME: dedent(content)}


def build_archetype_checklist_csv(archetype: str, language: str) -> str:
    rows = ARCHETYPE_SPECS[archetype]["checklist_rows"][language]
    csv_rows = [["area", "focus_question", "priority", "status", "notes"]]
    for area, question in rows:
        csv_rows.append([area, question, "high", "not-started", ""])
    return render_csv(csv_rows)


def build_archetype_metric_file(
    game: str, language: str, archetype: str | None
) -> dict[str, str]:
    if not archetype:
        return {}

    display = ARCHETYPE_SPECS[archetype]["display"][language]
    reference = ARCHETYPE_METRICS[archetype]["reference"]
    rows = ARCHETYPE_METRICS[archetype]["rows"][language]

    if language == "zh-CN":
        lines = [
            f"# {game} {display} 量化指标基线",
            "",
            "## 使用说明",
            "",
            f"- 品类模板: `{display}`",
            f"- 指标参考文件: `references/{reference}`",
            "- 这些指标是观测基线，不是通用 KPI 标准答案。",
            "- 先记录原作观测带宽，再提出复刻目标带宽。",
            "",
            "## 指标表",
            "",
            "| ID | 类别 | 指标 | 单位 | 如何采样 | 为什么重要 |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    else:
        lines = [
            f"# {game} {display} Metric Baselines",
            "",
            "## Usage",
            "",
            f"- Archetype: `{display}`",
            f"- Metric reference file: `references/{reference}`",
            "- These metrics are observation baselines, not universal KPI targets.",
            "- Record the original game's observed band before proposing remake target bands.",
            "",
            "## Metric Table",
            "",
            "| ID | Category | Metric | Unit | How to sample | Why it matters |",
            "| --- | --- | --- | --- | --- | --- |",
        ]

    for metric_id, category, metric_name, unit, method, why in rows:
        lines.append(
            f"| {metric_id} | {category} | {metric_name} | {unit} | {method} | {why} |"
        )

    lines.extend(["", evidence_section_block(language).rstrip()])
    return {ARCHETYPE_METRIC_FILE_NAME: "\n".join(lines).rstrip() + "\n"}


def build_archetype_metrics_csv(archetype: str, language: str) -> str:
    rows = ARCHETYPE_METRICS[archetype]["rows"][language]
    csv_rows = [[
        "metric_id",
        "category",
        "metric_name",
        "unit",
        "measurement_method",
        "why_it_matters",
        "observed_band",
        "target_band",
        "confidence",
        "source_ids",
        "notes",
    ]]
    for metric_id, category, metric_name, unit, method, why in rows:
        csv_rows.append(
            [metric_id, category, metric_name, unit, method, why, "", "", "Open", "", ""]
        )
    return render_csv(csv_rows)


def build_experiment_file(
    game: str, language: str, archetype: str | None
) -> dict[str, str]:
    archetype_label = archetype_display(archetype, language)
    rows = prioritized_experiment_rows(language, archetype)

    if language == "zh-CN":
        lines = [
            f"# {game} 通用实验设计模板",
            "",
            "## 使用说明",
            "",
            "- 参考文件: `references/experiment-design.md`",
            f"- 当前主品类镜头: `{archetype_label}`",
            "- 这些实验用于把“感觉像”变成“可采样、可比较、可复查”的调研记录。",
            "- 先记录原作观测值，再写复刻目标带宽。",
            "",
            "## 推荐首轮实验",
            "",
        ]
        if archetype:
            for experiment_id, _category, name, _applies_to, _unit, sample_size, _method, _why, priority in rows[:4]:
                lines.append(
                    f"- `{experiment_id}` `{priority}`: {name}，推荐样本量 `{sample_size}`。"
                )
        else:
            lines.append("- 未指定 archetype 时，先优先做 `EXP-03`、`EXP-04`、`EXP-05`。")
        lines.extend(
            [
                "",
            "## 实验目录",
            "",
                "| ID | 类别 | 实验 | 适用品类 | 单位 | 推荐样本量 | 优先级 | 方法 | 价值 |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
    else:
        lines = [
            f"# {game} Cross-Archetype Experiment Design",
            "",
            "## Usage",
            "",
            "- Reference file: `references/experiment-design.md`",
            f"- Current primary lens: `{archetype_label}`",
            "- These experiments convert loose impressions into sampleable, comparable, reviewable evidence.",
            "- Record observed original-game bands before proposing remake target bands.",
            "",
            "## Recommended First Pass",
            "",
        ]
        if archetype:
            for experiment_id, _category, name, _applies_to, _unit, sample_size, _method, _why, priority in rows[:4]:
                lines.append(
                    f"- `{experiment_id}` `{priority}`: {name}, recommended sample size `{sample_size}`."
                )
        else:
            lines.append(
                "- Without an archetype, start with `EXP-03`, `EXP-04`, and `EXP-05`."
            )
        lines.extend(
            [
                "",
                "## Experiment Catalog",
                "",
                "| ID | Category | Experiment | Applies to | Unit | Recommended sample size | Priority | Method | Value |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )

    for experiment_id, category, name, applies_to, unit, sample_size, method, why, priority in rows:
        lines.append(
            f"| {experiment_id} | {category} | {name} | {applies_to} | {unit} | {sample_size} | {priority} | {method} | {why} |"
        )

    lines.extend(["", evidence_section_block(language).rstrip()])
    return {EXPERIMENT_FILE_NAME: "\n".join(lines).rstrip() + "\n"}


def build_experiment_summary_placeholder(
    game: str, language: str, archetype: str | None
) -> dict[str, str]:
    archetype_label = archetype_display(archetype, language)
    if language == "zh-CN":
        content = f"""\
# {game} 实验结果摘要

## 状态

- 当前主品类镜头: `{archetype_label}`
- 此文件建议由 `summarize_experiments.py` 自动生成。

## 生成命令

```bash
python3 "${{GAME_REMAKE_RESEARCH:?set GAME_REMAKE_RESEARCH to the installed skill root}}/scripts/summarize_experiments.py" \\
  --docs-dir ./docs/remake-{slugify(game)} \\
  --mode full
```

## 备注

- 先更新 `data/experiment-plan.csv`、`data/experiment-observations.csv` 和 `data/experiments/*.csv`。
- 运行前先将 `GAME_REMAKE_RESEARCH` 指向已安装的 skill 根目录。
- 如已执行指标回填，再运行摘要脚本可同时带出 `data/archetype-metrics.csv` 快照。
- 若要用于最终 dossier，建议额外生成 `10-experiment-summary-compact.md`：
  `summarize_experiments.py --mode compact --output 10-experiment-summary-compact.md`
"""
    else:
        content = f"""\
# {game} Experiment Summary

## Status

- Current primary lens: `{archetype_label}`
- This file is intended to be regenerated by `summarize_experiments.py`.

## Command

```bash
python3 "${{GAME_REMAKE_RESEARCH:?set GAME_REMAKE_RESEARCH to the installed skill root}}/scripts/summarize_experiments.py" \\
  --docs-dir ./docs/remake-{slugify(game)} \\
  --mode full
```

## Notes

- Update `data/experiment-plan.csv`, `data/experiment-observations.csv`, and `data/experiments/*.csv` first.
- Set `GAME_REMAKE_RESEARCH` to the installed skill root before running the command.
- If metric rollup has already been run, the summary script will also surface the current `data/archetype-metrics.csv` snapshot.
- For final dossier merges, also generate `10-experiment-summary-compact.md` with
  `summarize_experiments.py --mode compact --output 10-experiment-summary-compact.md`.
"""
    return {EXPERIMENT_SUMMARY_FILE_NAME: dedent(content)}


def prioritized_experiment_rows(
    language: str, archetype: str | None
) -> list[tuple[str, str, str, str, str, str, str, str, str]]:
    rows = EXPERIMENT_SPECS[language]
    prioritized = []
    for experiment_id, category, name, applies_to, unit, sample_size, method, why in rows:
        priority = resolve_experiment_priority(experiment_id, applies_to, archetype)
        prioritized.append(
            (
                experiment_id,
                category,
                name,
                applies_to,
                unit,
                sample_size,
                method,
                why,
                priority,
            )
        )
    prioritized.sort(key=lambda row: (PRIORITY_ORDER[row[8]], row[0]))
    return prioritized


def resolve_experiment_priority(
    experiment_id: str, applies_to: str, archetype: str | None
) -> str:
    if not archetype:
        return "medium"
    explicit = ARCHETYPE_EXPERIMENT_PRIORITIES.get(archetype, {}).get(experiment_id)
    if explicit:
        return explicit
    if applies_to == "all" or archetype in applies_to.split("|"):
        return "medium"
    return "low"


def build_experiment_plan_csv(language: str, archetype: str | None) -> str:
    rows = prioritized_experiment_rows(language, archetype)
    csv_rows = [[
        "experiment_id",
        "category",
        "experiment_name",
        "applies_to",
        "unit",
        "recommended_sample_size",
        "method",
        "status",
        "priority",
        "notes",
    ]]
    for experiment_id, category, name, applies_to, unit, sample_size, method, _why, priority in rows:
        csv_rows.append(
            [experiment_id, category, name, applies_to, unit, sample_size, method, "not-started", priority, ""]
        )
    return render_csv(csv_rows)


def build_experiment_observations_csv(language: str) -> str:
    rows = EXPERIMENT_SPECS[language]
    csv_rows = [["experiment_id", "experiment_name", "detail_file", "last_updated", "status", "owner", "notes"]]
    for experiment_id, _category, name, _applies_to, _unit, _sample_size, _method, _why in rows:
        csv_rows.append(
            [experiment_id, name, EXPERIMENT_DETAIL_TEMPLATES[experiment_id]["file"], "", "not-started", "", ""]
        )
    return render_csv(csv_rows)


def build_experiment_detail_templates() -> dict[str, str]:
    files: dict[str, str] = {}
    for spec in EXPERIMENT_DETAIL_TEMPLATES.values():
        files[spec["file"]] = render_csv([spec["header"], spec["sample"]])
    return files


def build_archetype_metric_links_csv(archetype: str) -> str:
    csv_rows = [[
        "metric_id",
        "experiment_id",
        "detail_file",
        "value_columns",
        "aggregation",
        "status",
        "notes",
    ]]
    for metric_id, experiment_id, detail_file, value_columns, aggregation, status, notes in ARCHETYPE_METRIC_LINKS[archetype]:
        csv_rows.append(
            [metric_id, experiment_id, detail_file, value_columns, aggregation, status, notes]
        )
    return render_csv(csv_rows)


def build_documents_en(
    game: str, version_scope: str, archetype: str | None
) -> dict[str, str]:
    archetype_line = archetype_scope_line(archetype, "en")
    evidence_block = indent(evidence_section_block("en").rstrip(), "            ")
    return {
        "00-overview-and-source-ledger.md": dedent(
            f"""\
            # {game} Remake Research Overview

            ## Scope Lock

            - Target game: `{game}`
            - Baseline version: `{version_scope}`
            {archetype_line}
            - Research goal:
            - Target output: reference study / vertical slice / full remake
            - Platforms in scope:
            - Regions in scope:

            ## Research Questions

            - Which player fantasy and game pillars must survive the remake?
            - Which systems are historical constraints, monetization artifacts, or multiplayer-only dependencies?
            - Which parts require direct fidelity and which parts can be adapted?

            ## Source Ledger

            | ID | Type | Link or location | Version/date | Confidence | Notes |
            | --- | --- | --- | --- | --- | --- |
            | S1 | Official |  |  | Confirmed |  |
            | S2 | Gameplay footage |  |  | Confirmed |  |
            | S3 | Wiki / datamine |  |  | Inferred |  |

            ## Evidence Citation Rule

            - Use inline ledger anchors like `S-id` inside `Confirmed Facts` and `Inferred Model`.
            - Keep remake proposals separate from evidence-backed observations.

            ## Confidence Policy

            - Confirmed:
            - Inferred:
            - Open:

            ## Top Unknowns

            - Unknown:
            - Impact:
            - Validation plan:
            """
        ),
        "01-product-and-player-experience.md": dedent(
            f"""\
            # {game} Product And Player Experience

            ## Product Definition

            - Genre:
            - Audience:
            - Comparable titles:
            - Business model:
            - Session length:

            ## North Star Experience

            - Fantasy:
            - Pillars:
            - Must-preserve moments:
            - Must-adapt elements:

            ## Player Journey

            - Onboarding:
            - Midgame:
            - Endgame / mastery:
            - Long-term goals:

            ## Loop Design

            - Core loop:
            - Session loop:
            - Meta loop:
            - Retention hooks:

            ## Product Management Notes

            - Positioning:
            - Scope cuts:
            - KPI proxies:
            - Shipping risks:

{evidence_block}
            """
        ),
        "02-systems-and-gameplay.md": dedent(
            f"""\
            # {game} Systems And Gameplay

            ## Control Grammar

            - Inputs:
            - Context-sensitive actions:
            - Buffering / cancels:

            ## Movement And Combat

            - Movement verbs:
            - Combat verbs:
            - Hit timing:
            - Damage feedback:
            - Camera behavior:

            ## Challenge Structure

            - Enemy taxonomy:
            - Encounter grammar:
            - Map / mission flow:
            - Failure and recovery:

            ## Gameplay Feel Notes

            - Responsiveness drivers:
            - Readability rules:
            - Skill ceiling:

{evidence_block}
            """
        ),
        "03-economy-and-balance.md": dedent(
            f"""\
            # {game} Economy And Balance

            ## Resource Map

            - Primary currencies:
            - Secondary currencies:
            - Upgrade materials:
            - Energy / cooldown / capacity constraints:

            ## Faucets And Sinks

            - Sources:
            - Sinks:
            - Scarcity points:
            - Recovery paths:

            ## Stat And Progression Model

            - Core stats:
            - Progression bands:
            - Upgrade steps:
            - Build commitment points:

            ## Formula Capture

            - Damage formula:
            - Reward formula:
            - Upgrade success / failure logic:
            - TTK or difficulty targets:

            ## Tuning Risks

            - Dominant strategies:
            - Grind cliffs:
            - Economy inflation risks:

{evidence_block}
            """
        ),
        "04-content-art-audio-narrative.md": dedent(
            f"""\
            # {game} Content, Art, Audio, And Narrative

            ## Content Taxonomy

            - Modes / content types:
            - Level or map families:
            - Progression milestones:

            ## Art Direction

            - Shape language:
            - Color language:
            - Camera framing:
            - UI language:
            - Asset categories:

            ## Animation

            - Locomotion states:
            - Combat states:
            - Boss telegraphs:
            - Timing notes:

            ## Music And Audio

            - Cue map:
            - Dynamic rules:
            - SFX taxonomy:
            - Mix priorities:

            ## Copywriting And Narrative

            - Glossary:
            - UI tone:
            - Quest / mission writing pattern:
            - World pillars:
            - Story structure:

{evidence_block}
            """
        ),
        "05-client-architecture-and-production.md": dedent(
            f"""\
            # {game} Client Architecture And Production

            ## Product Targets

            - Platforms:
            - Performance budgets:
            - Input devices:
            - Online / offline assumptions:

            ## Runtime Architecture

            - Core modules:
            - System boundaries:
            - Data ownership:
            - Save model:
            - Content pipeline:

            ## Tools And Workflow

            - Editor tooling:
            - Debug tooling:
            - Data authoring flow:
            - Build pipeline:

            ## Production Plan

            - Vertical slice:
            - Milestones:
            - Staffing assumptions:
            - Outsourcing assumptions:

            ## Risk Register

            - Technical risks:
            - Content risks:
            - Schedule risks:

{evidence_block}
            """
        ),
        "06-replica-backlog-and-acceptance.md": dedent(
            f"""\
            # {game} Replica Backlog And Acceptance

            ## Prioritized Backlog

            | Priority | Area | Feature | Why it matters | Acceptance signal |
            | --- | --- | --- | --- | --- |
            | P0 | Core loop |  |  |  |
            | P1 | Progression |  |  |  |
            | P2 | Content |  |  |  |

            ## Vertical Slice Scope

            - Mandatory systems:
            - Mandatory content:
            - Mandatory polish:

            ## Full Production Scope

            - Content expansion plan:
            - Live-ops or post-launch assumptions:
            - Deliberate exclusions:

            ## Acceptance Criteria

            - Player feel:
            - Progression pacing:
            - Economy stability:
            - Art and animation readability:
            - Technical stability:

            ## Open Gaps And Validation

            - Gap:
            - Risk:
            - Validation task:
            """
        ),
        "99-research-log.md": dedent(
            f"""\
            # {game} Research Log

            ## Observation Entries

            | Date | Source ID | Topic | Observation | Confidence | Follow-up |
            | --- | --- | --- | --- | --- | --- |
            |  | S1 |  |  | Confirmed |  |

            ## Frame / Timing Notes

            - Clip:
            - Timestamp:
            - Observation:

            ## Contradictions To Resolve

            - Contradiction:
            - Sources:
            - Next step:
            """
        ),
    }


def build_documents_zh(
    game: str, version_scope: str, archetype: str | None
) -> dict[str, str]:
    archetype_line = archetype_scope_line(archetype, "zh-CN")
    evidence_block = indent(evidence_section_block("zh-CN").rstrip(), "            ")
    return {
        "00-overview-and-source-ledger.md": dedent(
            f"""\
            # {game} 复刻调研总览

            ## 范围锁定

            - 目标游戏: `{game}`
            - 基线版本: `{version_scope}`
            {archetype_line}
            - 调研目标:
            - 交付目标: 对标分析 / 垂直切片 / 完整复刻文档
            - 平台范围:
            - 区服范围:

            ## 核心调研问题

            - 哪些玩家幻想与体验支柱必须保真？
            - 哪些系统属于历史包袱、商业化产物或多人依赖？
            - 哪些部分必须高保真，哪些部分允许重构？

            ## 资料台账

            | ID | 类型 | 链接或位置 | 版本/日期 | 可信度 | 备注 |
            | --- | --- | --- | --- | --- | --- |
            | S1 | 官方资料 |  |  | Confirmed |  |
            | S2 | 实机录像 |  |  | Confirmed |  |
            | S3 | Wiki / Datamine |  |  | Inferred |  |

            ## 证据引用规则

            - 在 `Confirmed Facts` 和 `Inferred Model` 中使用内联 `S-id` 台账锚点。
            - 复刻方案与原作观察分开写，不要把设计决策混进证据结论。

            ## 可信度规则

            - Confirmed:
            - Inferred:
            - Open:

            ## 最高优先级未知项

            - 未知项:
            - 风险等级:
            - 验证方案:
            """
        ),
        "01-product-and-player-experience.md": dedent(
            f"""\
            # {game} 产品与玩家体验

            ## 产品定义

            - 类型:
            - 目标用户:
            - 对标产品:
            - 商业模式:
            - 单次游玩时长:

            ## 北极星体验

            - 玩家幻想:
            - 核心支柱:
            - 必须保留的时刻:
            - 必须改造的部分:

            ## 玩家旅程

            - 新手期:
            - 中期成长:
            - 后期追求 / 精通:
            - 长线目标:

            ## 循环设计

            - 核心循环:
            - 单局循环:
            - 元循环:
            - 留存或推进钩子:

            ## 产品经理视角

            - 市场定位:
            - 范围裁剪:
            - KPI 代理指标:
            - 上线风险:

{evidence_block}
            """
        ),
        "02-systems-and-gameplay.md": dedent(
            f"""\
            # {game} 系统与玩法

            ## 操作语法

            - 输入集合:
            - 上下文操作:
            - 输入缓存 / 取消:

            ## 移动与战斗

            - 移动动词:
            - 战斗动词:
            - 命中节奏:
            - 受击反馈:
            - 镜头行为:

            ## 挑战结构

            - 敌人分类:
            - 遭遇语法:
            - 地图 / 关卡流程:
            - 失败与恢复:

            ## 手感拆解

            - 响应性来源:
            - 可读性规则:
            - 技巧上限:

{evidence_block}
            """
        ),
        "03-economy-and-balance.md": dedent(
            f"""\
            # {game} 经济与数值

            ## 资源地图

            - 核心货币:
            - 次级货币:
            - 养成材料:
            - 体力 / 冷却 / 容量约束:

            ## 产出与消耗

            - 产出来源:
            - 消耗去向:
            - 稀缺点:
            - 回收路径:

            ## 属性与成长模型

            - 核心属性:
            - 成长分段:
            - 强化步骤:
            - Build 锁定点:

            ## 公式记录

            - 伤害公式:
            - 奖励公式:
            - 强化成功 / 失败逻辑:
            - TTK 或难度目标:

            ## 调优风险

            - 统治性策略:
            - 卡档风险:
            - 通胀风险:

{evidence_block}
            """
        ),
        "04-content-art-audio-narrative.md": dedent(
            f"""\
            # {game} 内容、美术、音频与叙事

            ## 内容分类

            - 模式 / 内容类型:
            - 地图或关卡族:
            - 关键里程碑:

            ## 美术方向

            - 形体语言:
            - 色彩语言:
            - 镜头构图:
            - UI 语言:
            - 资产分类:

            ## 动画

            - 移动状态:
            - 战斗状态:
            - Boss 预警:
            - 时序备注:

            ## 音乐与音效

            - Cue Map:
            - 动态规则:
            - SFX 分类:
            - 混音优先级:

            ## 文案与剧情

            - 术语表:
            - UI 文案语气:
            - 任务写法:
            - 世界观支柱:
            - 剧情结构:

{evidence_block}
            """
        ),
        "05-client-architecture-and-production.md": dedent(
            f"""\
            # {game} 客户端架构与制作计划

            ## 产品目标

            - 目标平台:
            - 性能预算:
            - 输入设备:
            - 联机 / 离线假设:

            ## 运行时架构

            - 核心模块:
            - 系统边界:
            - 数据归属:
            - 存档模型:
            - 内容管线:

            ## 工具与流程

            - 编辑器工具:
            - 调试工具:
            - 数据生产流:
            - 构建流程:

            ## 制作计划

            - 垂直切片:
            - 里程碑:
            - 人力假设:
            - 外包假设:

            ## 风险登记

            - 技术风险:
            - 内容风险:
            - 进度风险:

{evidence_block}
            """
        ),
        "06-replica-backlog-and-acceptance.md": dedent(
            f"""\
            # {game} 复刻待办与验收

            ## 优先级 Backlog

            | 优先级 | 模块 | 功能 | 价值原因 | 验收信号 |
            | --- | --- | --- | --- | --- |
            | P0 | 核心循环 |  |  |  |
            | P1 | 成长系统 |  |  |  |
            | P2 | 内容扩展 |  |  |  |

            ## 垂直切片范围

            - 必备系统:
            - 必备内容:
            - 必备打磨:

            ## 完整制作范围

            - 内容扩展计划:
            - 长线运营或后续更新假设:
            - 明确不做的内容:

            ## 验收标准

            - 玩家手感:
            - 成长节奏:
            - 经济稳定性:
            - 美术与动画可读性:
            - 技术稳定性:

            ## 未解问题与验证

            - 缺口:
            - 风险:
            - 验证任务:
            """
        ),
        "99-research-log.md": dedent(
            f"""\
            # {game} 调研日志

            ## 观察记录

            | 日期 | Source ID | 主题 | 观察 | 可信度 | 后续动作 |
            | --- | --- | --- | --- | --- | --- |
            |  | S1 |  |  | Confirmed |  |

            ## 帧数 / 时序备注

            - 片段:
            - 时间戳:
            - 结论:

            ## 待消解矛盾

            - 矛盾点:
            - 来源:
            - 下一步:
            """
        ),
    }


def build_support_files_en(
    game: str, version_scope: str, archetype: str | None
) -> dict[str, str]:
    slug = slugify(game)
    files = {
        "research-manifest.yaml": dedent(
            f"""\
            game: "{game}"
            slug: "{slug}"
            baseline_version: "{version_scope}"
            archetype: "{archetype or ''}"
            secondary_lenses: []
            research_goal: ""
            output_mode: "full remake pack"
            platforms: []
            regions: []
            languages: []
            historical_baseline: ""
            current_live_baseline: ""
            chosen_remake_baseline: ""
            constraints: []
            assumptions: []
            """
        ),
        "data/source-ledger.csv": dedent(
            """\
            source_id,source_type,title,url_or_location,platform,region,version_or_date,confidence,notes
            S1,official,,,,,,Confirmed,
            S2,gameplay-footage,,,,,,Confirmed,
            S3,wiki-or-datamine,,,,,,Inferred,
            """
        ),
        "data/formula-catalog.csv": dedent(
            """\
            formula_id,system,name,expression,variables,units,version_scope,confidence,source_ids,notes
            F1,combat,,,,,,,,
            F2,economy,,,,,,,,
            """
        ),
        "data/asset-taxonomy.csv": dedent(
            """\
            asset_id,discipline,category,subtype,reusable_or_bespoke,priority,source_ids,notes
            A1,art,character,,,,,
            A2,animation,combat-state,,,,,
            A3,audio,sfx-class,,,,,
            """
        ),
        "data/risk-register.csv": dedent(
            """\
            risk_id,category,description,impact,likelihood,owner,mitigation,validation
            R1,design,,,,,,,
            R2,technical,,,,,,,
            """
        ),
        "data/role-coverage.csv": dedent(
            """\
            role,status,key_findings,missing_evidence,output_file
            product-manager,not-started,,,01-product-and-player-experience.md
            professional-game-designer,not-started,,,01-product-and-player-experience.md
            gameplay-designer,not-started,,,02-systems-and-gameplay.md
            balance-designer,not-started,,,03-economy-and-balance.md
            art,not-started,,,04-content-art-audio-narrative.md
            animation,not-started,,,04-content-art-audio-narrative.md
            music-audio,not-started,,,04-content-art-audio-narrative.md
            copywriting,not-started,,,04-content-art-audio-narrative.md
            narrative,not-started,,,04-content-art-audio-narrative.md
            game-client-architect,not-started,,,05-client-architecture-and-production.md
            lead-engineer,not-started,,,05-client-architecture-and-production.md
            """
        ),
        "data/experiment-plan.csv": build_experiment_plan_csv("en", archetype),
        "data/experiment-observations.csv": build_experiment_observations_csv("en"),
    }
    files.update(build_experiment_detail_templates())

    if archetype:
        files["data/archetype-checklist.csv"] = build_archetype_checklist_csv(
            archetype, "en"
        )
        files["data/archetype-metrics.csv"] = build_archetype_metrics_csv(
            archetype, "en"
        )
        files["data/archetype-metric-links.csv"] = build_archetype_metric_links_csv(
            archetype
        )
    return files


def build_support_files_zh(
    game: str, version_scope: str, archetype: str | None
) -> dict[str, str]:
    slug = slugify(game)
    files = {
        "research-manifest.yaml": dedent(
            f"""\
            game: "{game}"
            slug: "{slug}"
            baseline_version: "{version_scope}"
            archetype: "{archetype or ''}"
            secondary_lenses: []
            research_goal: ""
            output_mode: "完整复刻文档"
            platforms: []
            regions: []
            languages: []
            historical_baseline: ""
            current_live_baseline: ""
            chosen_remake_baseline: ""
            constraints: []
            assumptions: []
            """
        ),
        "data/source-ledger.csv": dedent(
            """\
            source_id,source_type,title,url_or_location,platform,region,version_or_date,confidence,notes
            S1,official,,,,,,Confirmed,
            S2,gameplay-footage,,,,,,Confirmed,
            S3,wiki-or-datamine,,,,,,Inferred,
            """
        ),
        "data/formula-catalog.csv": dedent(
            """\
            formula_id,system,name,expression,variables,units,version_scope,confidence,source_ids,notes
            F1,combat,,,,,,,,
            F2,economy,,,,,,,,
            """
        ),
        "data/asset-taxonomy.csv": dedent(
            """\
            asset_id,discipline,category,subtype,reusable_or_bespoke,priority,source_ids,notes
            A1,art,character,,,,,
            A2,animation,combat-state,,,,,
            A3,audio,sfx-class,,,,,
            """
        ),
        "data/risk-register.csv": dedent(
            """\
            risk_id,category,description,impact,likelihood,owner,mitigation,validation
            R1,design,,,,,,,
            R2,technical,,,,,,,
            """
        ),
        "data/role-coverage.csv": dedent(
            """\
            role,status,key_findings,missing_evidence,output_file
            product-manager,not-started,,,01-product-and-player-experience.md
            professional-game-designer,not-started,,,01-product-and-player-experience.md
            gameplay-designer,not-started,,,02-systems-and-gameplay.md
            balance-designer,not-started,,,03-economy-and-balance.md
            art,not-started,,,04-content-art-audio-narrative.md
            animation,not-started,,,04-content-art-audio-narrative.md
            music-audio,not-started,,,04-content-art-audio-narrative.md
            copywriting,not-started,,,04-content-art-audio-narrative.md
            narrative,not-started,,,04-content-art-audio-narrative.md
            game-client-architect,not-started,,,05-client-architecture-and-production.md
            lead-engineer,not-started,,,05-client-architecture-and-production.md
            """
        ),
        "data/experiment-plan.csv": build_experiment_plan_csv("zh-CN", archetype),
        "data/experiment-observations.csv": build_experiment_observations_csv("zh-CN"),
    }
    files.update(build_experiment_detail_templates())

    if archetype:
        files["data/archetype-checklist.csv"] = build_archetype_checklist_csv(
            archetype, "zh-CN"
        )
        files["data/archetype-metrics.csv"] = build_archetype_metrics_csv(
            archetype, "zh-CN"
        )
        files["data/archetype-metric-links.csv"] = build_archetype_metric_links_csv(
            archetype
        )
    return files


def write_files(out_dir: Path, files: dict[str, str], force: bool) -> list[Path]:
    created: list[Path] = []
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        destination = out_dir / name
        if destination.exists() and not force:
            raise FileExistsError(
                f"{destination} already exists. Re-run with --force to overwrite."
            )
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content.rstrip() + "\n", encoding="utf-8")
        created.append(destination)
    return created


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold a remake-research document pack."
    )
    parser.add_argument("--game", required=True, help="Target game title.")
    parser.add_argument("--out", required=True, help="Output directory.")
    parser.add_argument(
        "--version-scope",
        help="Version, region, platform, or date scope to stamp into the docs.",
    )
    parser.add_argument(
        "--language",
        choices=("en", "zh-CN"),
        default="en",
        help="Template language. Defaults to en.",
    )
    parser.add_argument(
        "--archetype",
        choices=ARCHETYPE_CHOICES,
        help="Optional genre lens: mmo, arpg, roguelike, or card.",
    )
    parser.add_argument(
        "--single-file",
        action="store_true",
        help="Also create a single-file dossier template.",
    )
    parser.add_argument(
        "--with-support-files",
        action="store_true",
        help="Also create manifest and CSV support templates under data/.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing scaffold files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    version_scope = format_version_scope(args.version_scope, args.language)
    out_dir = Path(args.out).expanduser().resolve()
    files = build_documents(args.game, version_scope, args.language, args.archetype)
    files.update(build_archetype_file(args.game, args.language, args.archetype))
    files.update(
        build_archetype_metric_file(args.game, args.language, args.archetype)
    )
    files.update(build_experiment_file(args.game, args.language, args.archetype))
    files.update(
        build_experiment_summary_placeholder(
            args.game, args.language, args.archetype
        )
    )

    if args.single_file:
        files.update(
            build_single_file_template(
                args.game, version_scope, args.language, args.archetype
            )
        )
    if args.with_support_files:
        files.update(
            build_support_files(
                args.game, version_scope, args.language, args.archetype
            )
        )

    created = write_files(out_dir, files, args.force)

    print(f"Created {len(created)} files for {args.game}:")
    for path in created:
        print(f"- {path}")
    print(f"Suggested slug: {slugify(args.game)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
