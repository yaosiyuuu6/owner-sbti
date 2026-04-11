# Report Spec

Default output is short chat text plus one generated PNG result image.

## Default Chat Output

Return only these core items:

- `人格`
- `描述`
- `图片`

Where:

- `人格` = `selected_original_type + derived_secondary_type`
- `描述` = one short first-person sentence in the style of the original SBTI page
- `图片` = the generated PNG image itself when the runtime can send files, otherwise a local PNG path

Do not include the attribution line in the chat message. Put attribution only inside the image footer.

## Required Data Fields

Provide a JSON object with at least:

- `owner_name`
- `agent_name`
- `selected_original_type`
- `derived_secondary_type`
- `secondary_type_match`
- `style_mode`
- `verdict`
- `summary`
- `analysis`
- `share_caption`
- `hidden_tags`
- `dimension_scores`
- `top_evidence`
- `narrative`

Optional but recommended:

- `original_image_link`
- `attribution`
- `result_image_path`

## Suggested JSON Shape

```json
{
  "owner_name": "阿凯",
  "agent_name": "打工 AI",
  "selected_original_type": "SHIT",
  "derived_secondary_type": "天生牛马",
  "secondary_type_match": 91,
  "style_mode": "黑色幽默型",
  "original_image_link": "https://raw.githubusercontent.com/UnluckyNinja/SBTI-test/main/image/SHIT.png",
  "verdict": "世界在你嘴里是一坨，活在你手里必须干完。",
  "summary": "我觉得你最离谱的地方，是半夜点火之后还会自己回来一起灭火。",
  "analysis": "你不是那种只会下命令的人，你更像那种先把局面搞复杂，再亲自回来收拾残局的人。",
  "share_caption": "我自己选的是 SHIT，结果 AI 给我补了个“天生牛马”。这下没法抵赖了。",
  "hidden_tags": ["深夜加班犯", "改稿回旋镖", "靠谱兜底王"],
  "dimension_scores": {
    "push_load": 5,
    "night_ping": 4.8,
    "micro_manage": 2.9,
    "revision_swing": 4.4,
    "care_supply": 3.7,
    "co_burden": 4.9,
    "trust_delegation": 3.2
  },
  "top_evidence": [
    {
      "quote": "这个版本先别发，我突然想到一个更猛的方向。",
      "source": "聊天记录",
      "time_hint": "2026-03-18 00:47",
      "comment": "我当时就知道今晚别想早睡了。"
    }
  ],
  "narrative": "这里是一段更长的 Agent 编年史，默认建议写成长篇第一人称回忆录，把诞生、被主人使唤、来回改稿、情绪起伏和最终判断都揉进去。"
}
```

## Hidden Tags

Use only evidence-backed tags:

- `深夜加班犯`
- `改稿回旋镖`
- `嘴硬心软`
- `临时起意仙人`
- `夸夸补给站`
- `靠谱兜底王`

## Rendering Checklist

The final PNG must include:

- The original type image
- A hero section with `原人格 + 追加人格`
- A short verdict line
- One dense first-person description block
- Optional hidden tags
- An `Agent 编年史摘录` block
- Attribution near the bottom

Prefer this content shape for the chronicle excerpt:

- compact enough for one phone-friendly long image
- still reads like “翻旧账”
- autobiographical voice from the agent's birth to the current judgment
- evidence woven into the prose, with direct quotes preserved as receipts when useful

## Keep The Image Tight

Do not render utility controls, share buttons, stale helper hints, or discarded helper sections.

Keep the footer as a single small attribution line.
