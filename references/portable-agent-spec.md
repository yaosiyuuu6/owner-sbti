# Portable Agent Spec

Use this bundle from any local agent runtime that can:

- read Markdown files
- write JSON files
- execute Python 3 scripts

This includes Codex, Claude Code, OpenClaw, and similar local coding agents.

## Cross-Agent Contract

If an agent is given only the GitHub link to this skill bundle, that should still be enough. The agent should inspect `SKILL.md` first, then the referenced Markdown files, and produce the final answer directly in chat.

Default behavior:

1. Read `SKILL.md`.
2. Read `references/original-assets.md`, `references/relationship-types.md`, and `references/voice-guide.md`.
3. Ask for the user-selected original SBTI type if missing.
4. Automatically inspect the agent's own accessible history, preferring all accessible same-user threads over only the current context window.
5. Generate one local HTML result page.
6. Return only `人格 + 描述 + 链接`.

Do not ask the user to manually provide evidence if the agent can already inspect enough history in the active environment.
Do not stop at the current context if the runtime can access older same-user threads or broader workspace traces.

Optional behavior if files are explicitly requested:

1. Generate a report JSON object that matches [report-spec.md](./report-spec.md).
2. Run the bundled scripts locally.

The optional local workflow is:

```bash
python3 scripts/validate_report_json.py --input /path/to/report.json
python3 scripts/render_owner_sbti.py \
  --input /path/to/report.json \
  --output-html /path/to/report.html \
  --output-md /path/to/report.md
```

## Required Reasoning Rules

No matter which agent runtime is used, keep these rules fixed:

- The user chooses the original SBTI type.
- The agent must first mine its own accessible history for evidence.
- The agent should prefer all accessible same-user threads, not just the current visible context.
- The agent derives only the secondary relationship type.
- The report voice stays first person from the agent.
- Strong claims must be evidence-backed.
- The result should feel like the original SBTI page, not a neutral audit.
- The final default answer should be concise enough to send directly in chat.
- The user should not need to gather evidence in normal usage.

## Recommended Prompt Skeleton

Use a prompt like this in non-Codex runtimes:

```text
Read SKILL.md, references/original-assets.md, references/relationship-types.md, and references/voice-guide.md.
The user-selected original SBTI type is: <TYPE>.
First inspect your own accessible history in this task and environment for evidence, starting with all accessible same-user threads rather than only the current context.
Only ask for extra records if the accessible history is genuinely not enough.
Generate one local HTML page from the bundled renderer, then return only:
人格：
描述：
链接：

Put attribution only inside the HTML page, not in the chat reply.
```

## Portability Constraints

Do not rely on:

- Codex-only tools
- MCP servers
- remote APIs
- browser automation
- Node.js packages

The current bundle is intentionally Python-stdlib-only so it can be reused from different agent shells with minimal friction.
