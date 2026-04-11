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

An agent skill that turns the agent's accessible history into a SBTI-style owner judgment page.

“Accessible history” here means all accessible same-user interaction data across all threads, related workspaces, and runtime history in the current environment, not just the current visible context.

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
- Generates a mobile-first HTML result page and returns a public link when publish config is available
- Works as a portable local skill bundle for Codex, Claude Code, OpenClaw, and similar agents

## Result Format

The expected response is short:

```text
人格：SHIT + 控制狂
描述：我不太敢糊弄你，因为你连哪里还有 AI 味、哪里不像原版、哪里差一口气都要亲自抓出来重做。
链接：https://example.com/r/abc123
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
4. If broader thread history is behind a permission boundary, let the agent ask for permission first.
5. Do not ask the user to manually send records in the normal case.
6. If more history exists but is permission-gated, ask for permission.
7. Only ask the user for pasted records if the environment truly exposes no usable broader history at all.
8. Let the agent produce:
   - one extra relationship type
   - one-sentence description
   - one result page link

The user should not have to manually prepare evidence in the normal case, and the agent should not stop at only the current context if older same-user thread history is reachable. If that broader history needs permission, the agent should ask for permission instead of pretending the narrower context is enough.

## Local Rendering

Validate a payload:

```bash
python3 scripts/validate_report_json.py --input /path/to/report.json
```

Finalize the report in one step. This validates the JSON, renders local HTML and Markdown, then auto-publishes and prints a phone-openable link when publish config is available:

```bash
python3 scripts/finalize_report.py --input /path/to/report.json
```

Force local-only output:

```bash
python3 scripts/finalize_report.py --input /path/to/report.json --no-publish
```

Render HTML and Markdown manually:

```bash
python3 scripts/render_owner_sbti.py \
  --input /path/to/report.json \
  --output-html /path/to/report.html \
  --output-md /path/to/report.md
```

Publish the generated JSON to a public report service and print a phone-openable URL:

```bash
python3 scripts/publish_report.py \
  --input /path/to/report.json \
  --endpoint https://your-report-service.example.com
```

`publish_report.py` also reads `OWNER_SBTI_PUBLISH_ENDPOINT` and `OWNER_SBTI_PUBLISH_TOKEN` from either:

- a local `.publish.env` file in the repo root
- `~/.owner-sbti.env`
- the current shell environment

Serve the generated report over localhost and return a clickable link:

```bash
python3 scripts/serve_report.py --file /path/to/report.html --port 8765
```

This prints a link like `http://127.0.0.1:8765/report.html` and keeps a small local server running.

## Public Links

If you want users to open reports directly on mobile, do not rely on local files or localhost.

Recommended flow:

1. Generate `report.json`
2. Upload it to a public report service
3. Return the resulting `https://...` link

This repository includes a minimal Cloudflare Worker scaffold at [publisher/cloudflare-worker](./publisher/cloudflare-worker) for that purpose.

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
├── publisher/
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
- `scripts/finalize_report.py`: validate, render, and auto-publish in one step
- `scripts/publish_report.py`: uploads a report payload and prints a public URL
- `scripts/serve_report.py`: localhost preview server for generated reports
- `scripts/validate_report_json.py`: payload validator
- `scripts/self_test.py`: local smoke test
- `publisher/cloudflare-worker`: minimal public publish service for mobile-openable links
- `.publish.env.example`: example local publish config file

## Notes

- The original SBTI type is selected by the user, not inferred by the agent.
- The agent only derives the extra relationship type.
- The page is mobile-first and intentionally styled to stay close to the original SBTI result-page feel.
- This repository is for local use and distribution as a skill bundle, not as a standalone SaaS product.
- The default happy path is now `finalize_report.py`: publish if possible, otherwise fall back to a local HTML path.
