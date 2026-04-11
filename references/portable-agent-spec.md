# Portable Agent Spec

## First Reply Rule

If a non-Codex agent is given this repository link and asked to learn or use `owner-sbti`, the first reply must not be a repository summary.

The first reply should be only:

```text
你的原始SBTI是什么？
```

Do this unless the user already provided the original SBTI type in the same request.

Do not ask the user to manually send logs, screenshots, examples, or evidence in the normal case.
After the user provides the original SBTI type, directly inspect all same-user records already accessible in the current environment.
If more history exists but is permission-gated, ask for permission instead of asking the user to paste records.

Use this bundle from any local agent runtime that can:

- read Markdown files
- write JSON files
- execute Python 3 scripts with Pillow installed
- send or display local image files when the runtime supports it

This includes Codex, Claude Code, OpenClaw, and similar local coding agents.

## Cross-Agent Contract

If an agent is given only the GitHub link to this skill bundle, that should still be enough. The agent should inspect `SKILL.md` first, then the referenced Markdown files, and produce the final answer directly in chat.

Default behavior:

1. Read `SKILL.md`.
2. Read `references/original-assets.md`, `references/relationship-types.md`, and `references/voice-guide.md`.
3. Ask for the user-selected original SBTI type if missing, and do that before summarizing anything.
4. Automatically inspect the agent's own accessible history, preferring all accessible same-user threads over only the current context window.
5. Generate one local PNG result image.
6. If a supported channel is configured, send the PNG directly to that chat.
7. Otherwise return only `人格 + 描述 + 图片`.

The repository explanation is optional and secondary. It must not replace step 3.

Do not ask the user to manually provide evidence if the agent can already inspect enough history in the active environment.
Do not stop at the current context if the runtime can access older same-user threads or broader workspace traces.
If broader same-user thread history is available only with permission, ask for that permission before continuing.
Only ask the user for pasted records if the runtime truly exposes no broader usable history at all.

Optional behavior if files are explicitly requested:

1. Generate a report JSON object that matches [report-spec.md](./report-spec.md).
2. Run the bundled scripts locally.

The default local workflow is:

```bash
python3 scripts/finalize_report.py --input /path/to/report.json
```

That command validates the payload, renders the final PNG, then tries to deliver it to `lark`, `telegram`, or `whatsapp` if those channels are configured. If not, it prints the local image path.

The manual local workflow is:

```bash
python3 scripts/validate_report_json.py --input /path/to/report.json
python3 scripts/render_owner_sbti_image.py \
  --input /path/to/report.json \
  --output-png /path/to/report.png
```

If the runtime can attach or show local images directly, send the generated PNG to the user instead of only printing the path.

## Required Reasoning Rules

No matter which agent runtime is used, keep these rules fixed:

- The user chooses the original SBTI type.
- The agent must first mine its own accessible history for evidence.
- The agent should prefer all accessible same-user threads, not just the current visible context.
- If broader same-user thread history is permission-gated, the agent should request access instead of silently downgrading to the current context.
- The agent derives only the secondary relationship type.
- The report voice stays first person from the agent.
- Strong claims must be evidence-backed.
- The result should feel like the original SBTI page, not a neutral audit.
- The final default answer should be concise enough to send directly in chat.
- The user should not need to gather evidence in normal usage.
- The agent should directly consume all permitted same-user records before asking for any manual material.

## Recommended Prompt Skeleton

Use a prompt like this in non-Codex runtimes:

```text
Read SKILL.md, references/original-assets.md, references/relationship-types.md, and references/voice-guide.md.
If the user did not already give their original SBTI type, ask only: 你的原始SBTI是什么？
Do not summarize the repository before asking that question.
After the user answers, inspect your own accessible history in this task and environment for evidence, starting with all accessible same-user threads rather than only the current context.
If broader same-user thread history needs permission, ask for that permission first.
Only ask for extra records if the accessible history is genuinely not enough.
Generate one local PNG from the bundled renderer, then return only:
人格：
描述：
图片：

Put attribution only inside the image, not in the chat reply.
```

## Portability Constraints

Do not rely on:

- Codex-only tools
- MCP servers
- remote APIs
- browser automation
- Node.js packages

The current bundle is intentionally lightweight so it can be reused from different agent shells with minimal friction. The only runtime dependency beyond Python 3 is Pillow.
