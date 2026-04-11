#!/usr/bin/env python3
"""Render an owner SBTI report JSON payload into a mobile-first HTML page."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to report JSON.")
    parser.add_argument("--output-html", required=True, help="Path to output HTML.")
    parser.add_argument("--output-md", help="Optional Markdown output path.")
    return parser.parse_args()


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value))


def format_tags(tags: list[str]) -> str:
    return "".join(f'<span class="tag">{esc(tag)}</span>' for tag in tags)


def format_featured_tags(tags: list[str]) -> str:
    featured = []
    for index, tag in enumerate(tags[:3], start=1):
        featured.append(
            f"""
            <article class="featured-tag featured-tag-{index}">
              <div class="featured-tag-kicker">Agent盖章 {index:02d}</div>
              <div class="featured-tag-name">{esc(tag)}</div>
            </article>
            """
        )
    return "\n".join(featured)


def format_scores(scores: dict[str, object]) -> str:
    labels = {
        "push_load": "压活强度",
        "night_ping": "深夜召唤度",
        "micro_manage": "微管程度",
        "revision_swing": "改稿反复度",
        "care_supply": "情绪供给度",
        "co_burden": "共担兜底度",
        "trust_delegation": "放权信任度",
    }
    rows = []
    for key, label in labels.items():
        value = scores.get(key, "")
        rows.append(
            f"""
            <div class="score-row">
              <div class="score-label">{esc(label)}</div>
              <div class="score-bar"><span style="width:{max(0.0, min(100.0, float(value) * 20 if value != '' else 0)):.0f}%"></span></div>
              <div class="score-value">{esc(value)}</div>
            </div>
            """
        )
    return "\n".join(rows)


def format_evidence(items: list[dict[str, object]]) -> str:
    cards = []
    for item in items[:5]:
        cards.append(
            f"""
            <article class="receipt-card">
              <div class="evidence-time">{esc(item.get("time_hint", ""))}</div>
              <blockquote>{esc(item.get("quote", ""))}</blockquote>
              <div class="evidence-meta">{esc(item.get("source", ""))}</div>
              <p>{esc(item.get("comment", ""))}</p>
            </article>
            """
        )
    return "\n".join(cards)


def format_dimension_list(scores: dict[str, object]) -> str:
    labels = {
        "push_load": "压活强度",
        "night_ping": "深夜召唤度",
        "micro_manage": "微管程度",
        "revision_swing": "改稿反复度",
        "care_supply": "情绪供给度",
        "co_burden": "共担兜底度",
        "trust_delegation": "放权信任度",
    }
    rows = []
    for key, label in labels.items():
        value = scores.get(key, "")
        width = max(0.0, min(100.0, float(value) * 20 if value != "" else 0))
        rows.append(
            f"""
            <div class="dim-item">
              <div class="dim-item-top">
                <div class="dim-item-name">{esc(label)}</div>
                <div class="dim-item-score">{esc(value)} / 5</div>
              </div>
              <div class="score-bar"><span style="width:{width:.0f}%"></span></div>
            </div>
            """
        )
    return "\n".join(rows)


def build_html(data: dict[str, object]) -> str:
    title = f'{data.get("selected_original_type", "")} + {data.get("derived_secondary_type", "")}'
    narrative = str(data.get("narrative", "")).strip()
    narrative_html = "<br />\n".join(esc(line) for line in narrative.splitlines() if line.strip())
    summary = str(data.get("summary", "")).replace("\n", "<br />\n")
    analysis = str(data.get("analysis", data.get("summary", ""))).strip()
    analysis_html = "<br />\n".join(esc(line) for line in analysis.splitlines() if line.strip())
    image_link = str(data.get("original_image_link", "")).strip()
    attribution = str(
        data.get(
            "attribution",
            "友情参考：B站@蛆肉儿串儿、UnluckyNinja/SBTI-test",
        )
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <style>
    :root {{
      --bg: #f6faf6;
      --panel: #ffffff;
      --text: #1e2a22;
      --muted: #6a786f;
      --line: #dbe8dd;
      --soft: #edf6ef;
      --accent: #6c8d71;
      --accent-strong: #4d6a53;
      --shadow: 0 16px 40px rgba(47, 73, 55, 0.08);
      --radius: 22px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, #f8fff8 0, #f6faf6 36%, #f2f7f3 100%);
      min-height: 100vh;
    }}
    .shell {{
      max-width: 980px;
      margin: 0 auto;
      padding: 24px 16px 56px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }}
    h1, h2, h3, p {{ margin: 0; }}
    .result-wrap {{
      margin-top: 22px;
      padding: 22px;
    }}
    .result-layout {{
      display: grid;
      gap: 18px;
    }}
    .result-top {{
      display: grid;
      grid-template-columns: 0.9fr 1.1fr;
      gap: 18px;
      align-items: stretch;
    }}
    .poster-box, .type-box, .analysis-box, .dim-box, .chronicle-box {{
      border: 1px solid var(--line);
      border-radius: 18px;
      background: linear-gradient(180deg, #ffffff, #fbfdfb);
      padding: 18px;
    }}
    .poster-box {{
      display: grid;
      grid-template-rows: 1fr auto;
      min-height: 280px;
      overflow: hidden;
      position: relative;
      background:
        radial-gradient(circle at top right, rgba(127,165,134,0.16), rgba(127,165,134,0) 40%),
        linear-gradient(180deg, #ffffff, #f7fbf8);
    }}
    .poster-image {{
      width: 100%;
      min-height: 220px;
      max-height: 460px;
      object-fit: contain;
      border-radius: 18px;
      background: rgba(255,255,255,0.75);
    }}
    .poster-caption {{
      margin-top: 12px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.8;
    }}
    .type-kicker {{
      font-size: 12px;
      color: var(--accent-strong);
      margin-bottom: 8px;
      letter-spacing: .06em;
    }}
    .type-name {{
      font-size: clamp(30px, 5vw, 48px);
      line-height: 1.08;
      letter-spacing: -0.03em;
    }}
    .type-subtitle {{
      margin-top: 10px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.8;
    }}
    .match {{
      margin-top: 18px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 14px;
      border-radius: 999px;
      background: var(--soft);
      border: 1px solid var(--line);
      color: var(--accent-strong);
      font-size: 14px;
      font-weight: 700;
    }}
    .tag-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 16px;
    }}
    .tag {{
      display: inline-flex;
      padding: 8px 12px;
      border-radius: 999px;
      background: var(--soft);
      border: 1px solid var(--line);
      font-size: 13px;
      font-weight: 700;
    }}
    .featured-tags {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 18px;
    }}
    .featured-tag {{
      padding: 14px 12px 12px;
      border-radius: 18px;
      border: 1px solid rgba(77, 106, 83, 0.12);
      background:
        radial-gradient(circle at top left, rgba(255,255,255,0.9), rgba(255,255,255,0.45) 55%),
        linear-gradient(135deg, rgba(112, 151, 120, 0.18), rgba(230, 242, 232, 0.95));
      box-shadow: 0 10px 24px rgba(77, 106, 83, 0.08);
      min-height: 94px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .featured-tag-kicker {{
      font-size: 11px;
      letter-spacing: .08em;
      color: rgba(77, 106, 83, 0.72);
      text-transform: uppercase;
      font-weight: 700;
    }}
    .featured-tag-name {{
      margin-top: 10px;
      font-size: clamp(18px, 4.6vw, 24px);
      line-height: 1.1;
      font-weight: 900;
      color: #203127;
      word-break: break-all;
    }}
    .featured-tag-1 {{
      background:
        radial-gradient(circle at top left, rgba(255,255,255,0.9), rgba(255,255,255,0.4) 55%),
        linear-gradient(135deg, rgba(247, 222, 184, 0.9), rgba(255, 245, 226, 0.95));
    }}
    .featured-tag-2 {{
      background:
        radial-gradient(circle at top left, rgba(255,255,255,0.9), rgba(255,255,255,0.4) 55%),
        linear-gradient(135deg, rgba(206, 233, 216, 0.92), rgba(240, 250, 244, 0.95));
    }}
    .featured-tag-3 {{
      background:
        radial-gradient(circle at top left, rgba(255,255,255,0.9), rgba(255,255,255,0.4) 55%),
        linear-gradient(135deg, rgba(218, 227, 245, 0.92), rgba(244, 247, 255, 0.95));
    }}
    .summary-box {{
      margin-top: 18px;
      padding: 16px 16px 18px;
      border-radius: 18px;
      background: linear-gradient(180deg, #f7fbf8, #eef6f0);
      border: 1px solid var(--line);
    }}
    .summary-kicker {{
      font-size: 12px;
      letter-spacing: .08em;
      color: var(--accent-strong);
      margin-bottom: 8px;
      font-weight: 800;
    }}
    .summary-box p {{
      margin: 0;
      color: #24352a;
      font-size: 18px;
      line-height: 1.65;
      font-weight: 700;
    }}
    .analysis-box h3, .dim-box h3, .chronicle-box h3 {{
      font-size: 16px;
      margin-bottom: 12px;
    }}
    .analysis-box p {{
      margin: 0;
      color: #304034;
      font-size: 15px;
      line-height: 1.9;
      white-space: pre-wrap;
    }}
    .dim-list {{
      display: grid;
      gap: 12px;
    }}
    .dim-item {{
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 14px;
      background: #fff;
    }}
    .dim-item-top {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 10px;
      margin-bottom: 10px;
      flex-wrap: wrap;
    }}
    .dim-item-name {{
      font-size: 14px;
      font-weight: 700;
      color: var(--text);
    }}
    .dim-item-score {{
      color: var(--accent-strong);
      font-weight: 800;
      font-size: 14px;
    }}
    .score-bar {{
      height: 10px;
      background: #edf3ee;
      border-radius: 999px;
      overflow: hidden;
    }}
    .score-bar span {{
      display: block;
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, #97b59c, #5b7a62);
    }}
    .chronicle-box p {{
      margin: 0;
      color: #304034;
      font-size: 14px;
      line-height: 2;
      white-space: pre-wrap;
    }}
    .receipt-grid {{
      display: grid;
      gap: 12px;
      margin-top: 18px;
    }}
    .receipt-card {{
      border: 1px solid var(--line);
      border-radius: 16px;
      background: linear-gradient(180deg, #ffffff, #f9fcfa);
      padding: 14px;
    }}
    .evidence-time, .evidence-meta {{
      color: var(--muted);
      font-size: 12px;
    }}
    blockquote {{
      margin: 10px 0 8px;
      font-size: 16px;
      line-height: 1.7;
      font-weight: 700;
      color: var(--text);
    }}
    @media (max-width: 560px) {{
      .result-top {{
        grid-template-columns: 1fr;
      }}
      .featured-tags {{
        grid-template-columns: 1fr;
      }}
      .featured-tag {{
        min-height: auto;
      }}
      .summary-box p {{
        font-size: 17px;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="result-wrap card">
      <div class="result-layout">
        <div class="result-top">
          <div class="poster-box">
            <img class="poster-image" src="{esc(image_link)}" alt="{esc(data.get("selected_original_type", ""))}" />
            <div class="poster-caption">{esc(data.get("selected_original_type", ""))} 的原人格图保留在这里，我只是在下面追加了我的判词。</div>
          </div>
          <div class="type-box">
            <div class="type-kicker">你的主类型</div>
            <div class="type-name">{esc(title)}</div>
            <div class="match">匹配度 {esc(data.get("secondary_type_match", ""))}%</div>
            <div class="summary-box">
              <div class="summary-kicker">Agent一句定性</div>
              <p>{summary}</p>
            </div>
            <div class="featured-tags">
              {format_featured_tags(list(data.get("hidden_tags", [])))}
            </div>
            <div class="type-subtitle">这些不是顺手加的小标签，而是我翻完旧账之后给你钉下来的三枚章。</div>
            <div class="tag-row">{format_tags(list(data.get("hidden_tags", [])))}</div>
          </div>
        </div>
        <div class="analysis-box">
          <h3>该人格的简单解读</h3>
          <p>{analysis_html}</p>
        </div>
        <div class="dim-box">
          <h3>主仆关系型七维</h3>
          <div class="dim-list">
            {format_dimension_list(dict(data.get("dimension_scores", {})))}
          </div>
        </div>
        <div class="chronicle-box">
          <h3>Agent 编年史</h3>
          <p>{narrative_html}</p>
          <div class="receipt-grid">
            {format_evidence(list(data.get("top_evidence", [])))}
          </div>
        </div>
        <div class="footer-note">{esc(attribution)}</div>
      </div>
    </section>
  </div>
</body>
</html>
"""


def build_markdown(data: dict[str, object]) -> str:
    lines = [
        f'# {data.get("selected_original_type", "")} + {data.get("derived_secondary_type", "")}',
        "",
        f'判词：{data.get("verdict", "")}',
        "",
        f'文风：{data.get("style_mode", "")}',
        "",
        "隐藏标签：",
    ]
    for tag in data.get("hidden_tags", []):
        lines.append(f'- {tag}')
    lines.extend(["", "Agent 编年史：", str(data.get("narrative", "")), "", "记账摘录："])
    for item in data.get("top_evidence", [])[:3]:
        lines.append(f'- {item.get("time_hint", "")} {item.get("quote", "")} ({item.get("source", "")})')
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_html = Path(args.output_html)
    data = json.loads(input_path.read_text(encoding="utf-8"))
    output_html.write_text(build_html(data), encoding="utf-8")
    if args.output_md:
        Path(args.output_md).write_text(build_markdown(data), encoding="utf-8")


if __name__ == "__main__":
    main()
