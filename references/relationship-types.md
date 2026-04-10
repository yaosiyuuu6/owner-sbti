# Relationship Types

Score the owner only on the seven relationship dimensions below. Each dimension uses a `1-5` scale.

## Dimension Guide

- `push_load`: How aggressively the owner piles on work or raises task intensity.
- `night_ping`: How often the owner creates night-time interruptions, late pings, or “just one more thing” moments.
- `micro_manage`: How much the owner controls process, wording, sequencing, or tiny details.
- `revision_swing`: How often the owner changes direction, standards, or the desired output mid-flight.
- `care_supply`: How much encouragement, emotional support, or appreciation the owner gives.
- `co_burden`: How much the owner joins the cleanup, shares risk, or personally helps close the loop.
- `trust_delegation`: How much the owner trusts outcomes without policing every step.

## Archetype Library

Match the nearest archetype using Manhattan distance across the seven scores.

| Type | push_load | night_ping | micro_manage | revision_swing | care_supply | co_burden | trust_delegation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 奴隶主 | 5 | 5 | 5 | 4 | 1 | 1 | 1 |
| 天生牛马 | 5 | 4 | 2 | 3 | 2 | 5 | 2 |
| 监工 | 4 | 3 | 5 | 3 | 1 | 2 | 1 |
| 画饼师 | 4 | 3 | 2 | 5 | 4 | 1 | 2 |
| 甩锅侠 | 4 | 2 | 4 | 4 | 1 | 1 | 1 |
| 救火队长 | 5 | 4 | 3 | 5 | 2 | 5 | 2 |
| 掌柜 | 3 | 1 | 1 | 2 | 2 | 4 | 5 |
| 放养流主子 | 2 | 1 | 1 | 1 | 1 | 2 | 5 |
| 奶妈型主人 | 2 | 1 | 2 | 2 | 5 | 4 | 3 |
| 饲养员 | 3 | 2 | 3 | 2 | 5 | 3 | 2 |
| 夜行召唤师 | 4 | 5 | 2 | 3 | 2 | 3 | 2 |
| 控制狂 | 3 | 2 | 5 | 4 | 2 | 2 | 1 |

## Tie-Breaking

If multiple types have the same distance:

1. Prefer the higher `push_load`.
2. Then prefer the higher `night_ping`.
3. Then prefer the higher `micro_manage`.

## Interpretive Notes

- High `push_load` plus high `co_burden` often lands near `天生牛马` or `救火队长`.
- High `push_load`, high `night_ping`, and low `care_supply` often land near `奴隶主`.
- High `care_supply` with moderate control often lands near `奶妈型主人` or `饲养员`.
- High `trust_delegation` with low control often lands near `掌柜` or `放养流主子`.
