# owner-sbti

## First Reply Rule

If you are Claude Code, OpenClaw, or any non-Codex agent and the user asks you to learn or use this repository, do not start by summarizing the repository.

Your first reply should be only this question, unless the user already provided the answer:

```text
你的原始SBTI是什么？
```

Only after the user answers that question should you inspect accessible history and generate the result.

Do not ask the user to send chat logs, examples, evidence, or past records in the normal case.

Instead, directly inspect all same-user records you already have permission to access across all available threads, workspaces, and runtime history. If more history exists but is permission-gated, ask for permission, not for manual pasted records.

An agent skill that turns the agent's accessible history into a redesigned SBTI-style owner judgment poster.

“Accessible history” here means all accessible same-user interaction data across all threads, related workspaces, and runtime history in the current environment, not just the current visible context.

It keeps the original SBTI type image and humorous judgment tone as references, asks the user to choose their original SBTI type first, then lets the agent derive one extra relationship type from its own accessible records and render a new poster-style report image.

The default final output is:

- `人格`
- `描述`
- `图片`

## What It Does

- Reuses the original type image from [UnluckyNinja/SBTI-test](https://github.com/UnluckyNinja/SBTI-test) as a referenced visual asset
- Uses the user's selected original SBTI type as the base identity
- Derives one extra agent-side relationship type such as `奴隶主` or `天生牛马`
- Writes the copy in first-person agent voice
- Generates a phone-friendly PNG result image by default
- Works as a portable local skill bundle for Codex, Claude Code, OpenClaw, and similar agents

## Result Format

The expected response is short:

```text
人格：SHIT + 控制狂
描述：我不太敢糊弄你，因为你连哪里还不够顺眼、哪里还有半成品味，都要亲自抓出来重做。
图片：/absolute/path/to/report.png
```

Attribution is shown only inside the image footer:

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

As long as the agent can read files and run Python 3 with Pillow locally, it can use the skill without extra hosted setup.

## Required Flow

1. Give the agent this skill folder or GitHub directory link.
2. The agent should first ask for your original SBTI type if you did not already provide it.
3. Let the agent automatically inspect all accessible same-user threads first.
4. If broader thread history is behind a permission boundary, let the agent ask for permission first.
5. Do not ask the user to manually send records in the normal case.
6. Only ask the user for pasted records if the environment truly exposes no usable broader history at all.
7. Let the agent produce:
   - one extra relationship type
   - one-sentence description
   - one result image

The user should not have to manually prepare evidence in the normal case, and the agent should not stop at only the current context if older same-user thread history is reachable. If that broader history needs permission, the agent should ask for permission instead of pretending the narrower context is enough.

## Local Rendering

Validate a payload:

```bash
python3 scripts/validate_report_json.py --input /path/to/report.json
```

Finalize the report in one step. This validates the JSON, renders a PNG, and prints the final image path:

```bash
python3 scripts/finalize_report.py --input /path/to/report.json
```

Render the PNG manually:

```bash
python3 scripts/render_owner_sbti_image.py \
  --input /path/to/report.json \
  --output-png /path/to/report.png
```

Install Pillow if it is missing:

```bash
python3 -m pip install pillow
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
- `references/report-spec.md`: report JSON contract and image requirements
- `references/voice-guide.md`: first-person tone system
- `scripts/render_owner_sbti_image.py`: PNG renderer
- `scripts/finalize_report.py`: validate and render in one step
- `scripts/validate_report_json.py`: payload validator
- `scripts/self_test.py`: local smoke test

## Notes

- The original SBTI type is selected by the user, not inferred by the agent.
- The agent only derives the extra relationship type.
- The image is phone-friendly and intentionally rendered as a new poster-style report, while still borrowing the original type image and irreverent tone as references.
- This repository is for local use and distribution as a skill bundle, not as a standalone SaaS product.
- The default happy path is now `finalize_report.py`: validate the payload, render one PNG, and send that image back.
