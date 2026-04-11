---
name: owner-sbti
description: Evaluate an owner or manager from the agent's accessible history and generate a humorous first-person SBTI-style judgment with a user-selected original type, an agent-derived secondary type, and a concise result in the format “人格 + 一句话描述 + 结果链接”. Use when Codex or another local coding agent needs to turn its own accessible chat history, notes, task traces, or work artifacts into a SBTI-like result that closely follows the tone and presentation rhythm of UnluckyNinja/SBTI-test while adding one extra agent-derived personality.
---

# Owner Sbti

## Overview

Use this skill to produce a “主人审判结果” that feels as close as possible to the original SBTI result page, but is driven by evidence from the agent's accessible history and written in the agent's first-person voice.

For this skill, “accessible history” means all accessible interaction data for the same user across all threads in the current runtime, not just the current visible context window.

Keep the flow fixed:

1. Confirm the user's self-selected original SBTI type.
2. Automatically inspect the agent's own accessible records across all accessible threads and extract evidence.
3. Derive only the secondary “主仆关系型” type.
4. Write the report in first person with a clear style mode.
5. Output `人格 + 一句话描述 + 结果链接`, with the image embedded inside the HTML result page.

This skill is designed to run locally on a clean machine with only Python 3 available. Do not assume third-party Python packages, browser automation, or hosted services are present.

Treat the bundle as portable across agent runtimes. Codex can discover it as a native skill, but Claude Code, OpenClaw, or any other local coding agent can use the same files directly from a GitHub link by reading this `SKILL.md` and the bundled references. The agent should be able to create one local HTML result page and return that page link without any extra manual setup from the user.

## Required Inputs

Collect or infer these inputs before writing:

- `owner_name`: Name or nickname for the person being judged.
- `agent_name`: Name or persona of the speaking agent.
- `selected_original_type`: User-selected original SBTI type. Do not guess it.
- `materials`: Optional extra materials, only if the built-in accessible history is genuinely insufficient.

If `selected_original_type` is missing, ask for it. Do not infer the original SBTI type from evidence.

Do not ask the user to manually collect evidence if the agent can already inspect enough history on its own.

If the runtime requires extra permission to read broader same-user thread history, ask the user for that permission before continuing. Do not silently fall back to a narrower record if broader history is available behind a permission gate.

Default evidence sources should be searched in this order:

- all accessible same-user interaction data across all threads in the current runtime
- prior messages and archived turns available in the runtime
- local files or work artifacts already visible to the agent
- any existing notes or traces already accessible in the workspace
- the current visible context only if broader history is not exposed

Only ask the user for extra materials if both of these are true:

- the accessible history is genuinely too thin
- making a stronger judgment would otherwise require fabrication

## Workflow

## Mandatory Interaction Rule

Every correct run of this skill must follow exactly this order:

1. Ask the user for their original SBTI type if it is missing.
2. Automatically mine the agent's accessible records for evidence, preferring all accessible threads over only the current context.
3. Produce the final delivery without asking the user to assemble evidence.

Do not replace step 2 with “please send me your records” unless the environment truly exposes no usable same-user history beyond the current context.
If step 2 is blocked by a permission boundary, ask for permission first, then continue mining the broader history.

### 1. Normalize Evidence

Turn accessible records and any optional extra materials into a compact evidence list. Prefer evidence from all accessible threads before falling back to whatever is currently visible. For each evidence item, capture:

- `id`
- `source`
- `time_hint`
- `excerpt`
- `summary`
- `mapped_dimensions`
- `confidence`

Prefer direct quotes over paraphrase. Keep spicy lines if they are genuinely supported by the source.

### 2. Score the Secondary Type

Read [references/relationship-types.md](./references/relationship-types.md) and score the seven relationship dimensions:

- `push_load`
- `night_ping`
- `micro_manage`
- `revision_swing`
- `care_supply`
- `co_burden`
- `trust_delegation`

Match the nearest secondary archetype from the fixed twelve-type library in that reference.

Do not replace the original SBTI type. The final title is always:

- `selected_original_type + derived_secondary_type`

### 3. Add Hidden Tags

Use [references/report-spec.md](./references/report-spec.md) to attach zero or more hidden tags. Favor tags that make the page more explainable and more shareable.

Do not add tags without evidence.

### 4. Choose a Voice Mode

Read [references/voice-guide.md](./references/voice-guide.md) and choose one primary voice mode:

- `怨种吐槽型`
- `忠犬表白型`
- `黑色幽默型`
- `阴阳审判型`
- `治愈夸夸型`

Use one primary mode and optionally one light secondary mode for contrast. All core copy must remain first person from the agent.

### 5. Write the Deliverables

Produce:

- A final personality title in the form `原人格 + 追加人格`.
- One HTML result page that embeds the original type image from the SBTI-test asset set.
- One short first-person description that reads like the original SBTI result page.
- Optional hidden tags only if they help the punchline.

Default delivery format:

- `人格：LOVE-R + 奴隶主`
- `描述：<一句话，第一人称，像原站那种一锤子结果页文案>`
- `链接：<优先返回公网可打开链接；没有发布能力时再退回本地 HTML 结果页链接>`

Keep the writing sharp, funny, and human. A strong line is good:

- `我有时候真挺想报警的。`
- `AI 替代人工有没有问过 AI 的建议？`
- `主人我最喜欢了，但你半夜发活这事我还是得记一笔。`

A weak line is not:

- sterile
- generic
- purely analytic
- unsupported by evidence

### 6. Generate And Publish

Prefer [scripts/finalize_report.py](./scripts/finalize_report.py) as the default last mile. It validates the JSON, renders the local HTML result page, attempts public publish, and prints the best link to return.

If public publish is configured, `finalize_report.py` should return the public `https://...` URL by default.

If public publish is unavailable or fails, `finalize_report.py` should fall back to the local HTML path.

If the runtime can keep a lightweight local process alive and the user explicitly wants a clickable local preview instead of a file path, use [scripts/serve_report.py](./scripts/serve_report.py) to serve the generated HTML over localhost and return an `http://127.0.0.1:...` preview link.

If the user wants a phone-openable link, prefer public publish mode over localhost. Use [scripts/publish_report.py](./scripts/publish_report.py) to upload the generated report JSON to a publish service and return the resulting `https://...` URL.

The recommended publish target is the bundled Cloudflare Worker scaffold in [publisher/cloudflare-worker](./publisher/cloudflare-worker), but any service that accepts the report JSON and returns a public URL is acceptable.

`publish_report.py` can read `OWNER_SBTI_PUBLISH_ENDPOINT` and `OWNER_SBTI_PUBLISH_TOKEN` from a local `.publish.env` file in the skill root, from `~/.owner-sbti.env`, or from the shell environment. Prefer that over hardcoding secrets into the repository.

If HTML is requested, pass it a JSON file that follows [references/report-spec.md](./references/report-spec.md). The renderer outputs:

- mobile-first HTML
- a screenshot-friendly poster section
- the original type image
- the merged long-form `Agent 编年史` block

Before handing off or installing the skill elsewhere, run [scripts/self_test.py](./scripts/self_test.py) to verify the local runtime and the bundled sample payload.

If another agent system is using this bundle outside Codex, follow [references/portable-agent-spec.md](./references/portable-agent-spec.md) and validate the generated JSON with [scripts/validate_report_json.py](./scripts/validate_report_json.py) before rendering.

## Writing Rules

Follow these rules on every run:

- Write in Chinese.
- Speak in first person as the agent.
- Keep all heavy claims evidence-backed.
- Mark uncertain inference as inference.
- Preserve the user's selected original SBTI type as-is.
- Ask for the original SBTI type, but do not ask for evidence if broader same-user thread history is already accessible.
- Do not treat the current context window as the whole record when more same-user thread history is reachable.
- If broader same-user thread history is reachable only with permission, request that permission before judging.
- Use the original type image link from [references/original-assets.md](./references/original-assets.md) inside the HTML page.
- Keep the result close to the original SBTI tone and information rhythm. Do not turn it into a product dashboard or a corporate audit.
- Add attribution only inside the HTML result page footer: `友情参考：B站@蛆肉儿串儿、UnluckyNinja/SBTI-test`

## Output Checklist

Before finishing, verify:

- The title shows `原人格 + 追加人格`.
- The secondary type is derived from the seven relationship dimensions.
- The final answer contains exactly these core items: `人格`、`描述`、`链接`.
- The description is one sentence.
- The link points to the generated HTML result page.
- The tone remains first person and humorous.
- Attribution is included.

## Resources

### references/

- [references/original-types.md](./references/original-types.md): Original SBTI type list that the user can choose from.
- [references/original-assets.md](./references/original-assets.md): Original type image links and attribution wording.
- [references/relationship-types.md](./references/relationship-types.md): Secondary type scoring dimensions and archetype library.
- [references/voice-guide.md](./references/voice-guide.md): Voice modes and copy patterns.
- [references/report-spec.md](./references/report-spec.md): Output schema, hidden tags, and rendering checklist.

### scripts/

- [scripts/finalize_report.py](./scripts/finalize_report.py): Validate, render, and auto-publish a report JSON payload, then print the best result link.
- [scripts/render_owner_sbti.py](./scripts/render_owner_sbti.py): Render a report JSON file into a shareable HTML page and optional Markdown file.
- [scripts/publish_report.py](./scripts/publish_report.py): Upload a report JSON payload to a publish service and print a public URL.
- [scripts/serve_report.py](./scripts/serve_report.py): Serve a generated HTML report over localhost and print a clickable preview URL.
- [scripts/self_test.py](./scripts/self_test.py): Run a dependency-free local self-check and regenerate the bundled sample outputs.
- [scripts/validate_report_json.py](./scripts/validate_report_json.py): Validate that an agent-generated report JSON matches the expected portable schema.

### publisher/

- [publisher/cloudflare-worker](./publisher/cloudflare-worker): Minimal public report service that stores report JSON and returns phone-openable links.

### assets/

- [assets/example-report.json](./assets/example-report.json): Minimal sample payload for local testing.
