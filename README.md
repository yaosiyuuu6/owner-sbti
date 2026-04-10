# owner-sbti

An agent skill that turns the agent's accessible history into a SBTI-style owner judgment page.

“Accessible history” here means all accessible same-user interaction data across all threads in the current runtime, not just the current visible context.

It keeps the original SBTI presentation rhythm, asks the user to choose their original SBTI type first, then lets the agent derive one extra relationship type from its own accessible records.

The default final output is:

- `人格`
- `描述`
- `链接`

## What It Does

- Keeps the result page close to [UnluckyNinja/SBTI-test](https://github.com/UnluckyNinja/SBTI-test)
- Uses the user's selected original SBTI type as the base identity
- Derives one extra agent-side relationship type such as `奴隶主` or `天生牛马`
- Writes the copy in first-person agent voice
- Generates a local HTML result page that is easy to open and share
- Works as a portable local skill bundle for Codex, Claude Code, OpenClaw, and similar agents

## Result Format

The expected response is short:

```text
人格：SHIT + 控制狂
描述：我不太敢糊弄你，因为你连哪里还有 AI 味、哪里不像原版、哪里差一口气都要亲自抓出来重做。
链接：/absolute/path/to/result.html
```

Attribution is shown inside the HTML page footer:

```text
友情参考：B站@蛆肉儿串儿、UnluckyNinja/SBTI-test
```

## Install

### Codex

Install the skill folder into:

```text
~/.codex/skills/owner-sbti
```

Then restart Codex so it can discover the skill.

### Claude Code / OpenClaw / Other Local Agents

No special installer is required.

An agent can use this repository directly by opening:

- `SKILL.md`
- `references/`
- `scripts/`

As long as the agent can read files and run Python 3 locally, it can use the skill without extra setup.

## Required Flow

1. Give the agent this skill folder or GitHub directory link.
2. Tell it your original SBTI type.
3. Let the agent automatically inspect all accessible threads first.
4. Only provide extra records if the environment truly does not expose enough history.
5. Let the agent produce:
   - one extra relationship type
   - one-sentence description
   - one local result page link

The user should not have to manually prepare evidence in the normal case, and the agent should not stop at only the current context if older same-user thread history is reachable.

## Local Rendering

Validate a payload:

```bash
python3 scripts/validate_report_json.py --input /path/to/report.json
```

Render HTML and Markdown:

```bash
python3 scripts/render_owner_sbti.py \
  --input /path/to/report.json \
  --output-html /path/to/report.html \
  --output-md /path/to/report.md
```

Run the bundled self-test:

```bash
python3 scripts/self_test.py
```

## Repository Layout

```text
owner-sbti/
├── SKILL.md
├── README.md
├── agents/
├── assets/
├── references/
└── scripts/
```

## Key Files

- `SKILL.md`: primary instructions for the agent
- `references/original-assets.md`: original SBTI image links and attribution wording
- `references/relationship-types.md`: extra relationship-type scoring model
- `references/report-spec.md`: report JSON contract and page requirements
- `references/voice-guide.md`: first-person tone system
- `scripts/render_owner_sbti.py`: HTML renderer
- `scripts/validate_report_json.py`: payload validator
- `scripts/self_test.py`: local smoke test

## Notes

- The original SBTI type is selected by the user, not inferred by the agent.
- The agent only derives the extra relationship type.
- The page is mobile-first and intentionally styled to stay close to the original SBTI result-page feel.
- This repository is for local use and distribution as a skill bundle, not as a standalone SaaS product.
