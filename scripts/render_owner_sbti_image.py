#!/usr/bin/env python3
"""Render an owner-sbti report JSON payload into a phone-friendly PNG poster."""

from __future__ import annotations

import argparse
import io
import json
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


WIDTH = 1080
PADDING = 56
CARD_GAP = 28
CARD_RADIUS = 34
CANVAS_HEIGHT = 2380
FONT_PATH = "/System/Library/Fonts/PingFang.ttc"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to report JSON.")
    parser.add_argument("--output-png", required=True, help="Path to output PNG.")
    return parser.parse_args()


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size=size)


def avg(values: list[float]) -> float:
    return sum(values) / max(1, len(values))


def pct(value: float) -> int:
    return max(0, min(100, int(round(value))))


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    clean = "".join(str(text or "").splitlines())
    if not clean:
        return []
    lines: list[str] = []
    current = ""
    for char in clean:
        trial = current + char
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
            current = trial
            continue
        if current:
            lines.append(current)
        current = char
    if current:
        lines.append(current)
    return lines


def draw_text_lines(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    lines: list[str],
    font: ImageFont.FreeTypeFont,
    fill: str,
    line_gap: int,
) -> int:
    current_y = y
    for line in lines:
        draw.text((x, current_y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, current_y), line, font=font)
        current_y += (bbox[3] - bbox[1]) + line_gap
    return current_y


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str, outline: str | None = None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=CARD_RADIUS, fill=fill, outline=outline, width=width)


def draw_gradient(canvas: Image.Image, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> None:
    draw = ImageDraw.Draw(canvas)
    for y in range(canvas.height):
        ratio = y / max(1, canvas.height - 1)
        color = tuple(int(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3))
        draw.line([(0, y), (canvas.width, y)], fill=color)


def fetch_original_image(url: str) -> Image.Image | None:
    if not url:
        return None
    with urllib.request.urlopen(url) as response:
        data = response.read()
    image = Image.open(io.BytesIO(data)).convert("RGBA")
    return image


def draw_metric_card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str, value: int, accent: str) -> None:
    rounded(draw, box, fill="#FCFDFC", outline="#D8E3DA", width=2)
    left, top, right, bottom = box
    label_font = load_font(24)
    value_font = load_font(60)
    unit_font = load_font(26)
    draw.text((left + 24, top + 22), label, font=label_font, fill="#627267")
    draw.text((left + 24, top + 60), str(value), font=value_font, fill="#1A261F")
    unit_box = draw.textbbox((0, 0), "%", font=unit_font)
    draw.text((right - 24 - (unit_box[2] - unit_box[0]), top + 82), "%", font=unit_font, fill=accent)
    draw.rounded_rectangle((left + 24, bottom - 28, right - 24, bottom - 14), radius=7, fill="#E7EFE8")
    bar_w = max(24, int((right - left - 48) * value / 100))
    draw.rounded_rectangle((left + 24, bottom - 28, left + 24 + bar_w, bottom - 14), radius=7, fill=accent)


def draw_progress_row(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, label: str, raw_value: float, accent: str) -> None:
    score = pct(raw_value * 20)
    label_font = load_font(24)
    score_font = load_font(22)
    draw.text((x, y), label, font=label_font, fill="#2C3931")
    bar_x = x + 188
    bar_y = y + 10
    draw.rounded_rectangle((bar_x, bar_y, x + width - 42, bar_y + 22), radius=11, fill="#E7EFE8")
    bar_w = max(24, int((x + width - 42 - bar_x) * score / 100))
    draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + 22), radius=11, fill=accent)
    score_text = str(score)
    bbox = draw.textbbox((0, 0), score_text, font=score_font)
    draw.text((x + width - (bbox[2] - bbox[0]), y + 1), score_text, font=score_font, fill="#536458")


def draw_tag_pills(draw: ImageDraw.ImageDraw, x: int, y: int, max_width: int, tags: list[str]) -> int:
    current_x = x
    current_y = y
    font = load_font(24)
    for tag in tags:
        bbox = draw.textbbox((0, 0), tag, font=font)
        pill_w = max(176, min(296, bbox[2] - bbox[0] + 54))
        if current_x + pill_w > max_width:
            current_x = x
            current_y += 70
        draw.rounded_rectangle((current_x, current_y, current_x + pill_w, current_y + 54), radius=27, fill="#EEF5EF", outline="#DCE8DE", width=2)
        text_x = current_x + (pill_w - (bbox[2] - bbox[0])) // 2
        draw.text((text_x, current_y + 12), tag, font=font, fill="#24352A")
        current_x += pill_w + 16
    return current_y + 54


def build_image(data: dict[str, object]) -> Image.Image:
    canvas = Image.new("RGB", (WIDTH, CANVAS_HEIGHT), "#F4F8F4")
    draw_gradient(canvas, (245, 250, 246), (235, 243, 237))
    draw = ImageDraw.Draw(canvas)

    title_font = load_font(78)
    eyebrow_font = load_font(24)
    verdict_font = load_font(42)
    body_font = load_font(30)
    section_title_font = load_font(30)
    section_subtitle_font = load_font(20)
    evidence_time_font = load_font(18)
    evidence_quote_font = load_font(26)
    evidence_note_font = load_font(20)
    footer_font = load_font(20)

    dims = data.get("dimension_scores", {})
    if not isinstance(dims, dict):
        dims = {}

    push_load = float(dims.get("push_load", 0))
    night_ping = float(dims.get("night_ping", 0))
    micro_manage = float(dims.get("micro_manage", 0))
    revision_swing = float(dims.get("revision_swing", 0))
    care_supply = float(dims.get("care_supply", 0))
    co_burden = float(dims.get("co_burden", 0))
    trust_delegation = float(dims.get("trust_delegation", 0))

    match_pct = pct(float(data.get("secondary_type_match", 0)))
    pressure_pct = pct(avg([push_load, night_ping, micro_manage, revision_swing]) * 20)
    support_pct = pct(avg([care_supply, co_burden, trust_delegation]) * 20)

    title = f'{data.get("selected_original_type", "")} + {data.get("derived_secondary_type", "")}'
    verdict = str(data.get("verdict", "")).strip()
    summary = str(data.get("summary", "")).strip()
    analysis = str(data.get("analysis", data.get("summary", ""))).strip()
    evidence = list(data.get("top_evidence", []))[:3]
    hidden_tags = list(data.get("hidden_tags", []))

    y = PADDING
    content_width = WIDTH - PADDING * 2
    left_x = PADDING + 44
    right_image_box = (WIDTH - PADDING - 324, y + 44, WIDTH - PADDING - 44, y + 364)
    hero_box = (PADDING, y, PADDING + content_width, y + 1000)
    rounded(draw, hero_box, fill="#F7FBF7", outline="#D7E3D8", width=2)

    draw.text((left_x, y + 44), "Agent 主人审判书", font=eyebrow_font, fill="#66766B")
    draw.text((left_x, y + 78), "SBTI Portrait Edition", font=load_font(22), fill="#859389")

    title_lines = wrap_text(draw, title, title_font, 560)
    draw_text_lines(draw, left_x, y + 160, title_lines[:2], title_font, "#17231D", 10)

    rounded(draw, right_image_box, fill="#FFFFFF", outline="#D8E3DA", width=2)
    draw.text((right_image_box[0] + 20, right_image_box[1] + 18), "原人格海报", font=load_font(20), fill="#64756A")
    original_image = fetch_original_image(str(data.get("original_image_link", "")).strip())
    if original_image is not None:
        fitted = ImageOps.contain(original_image, (244, 236))
        paste_x = right_image_box[0] + (right_image_box[2] - right_image_box[0] - fitted.width) // 2
        paste_y = right_image_box[1] + 56 + (236 - fitted.height) // 2
        canvas.paste(fitted, (paste_x, paste_y), fitted)

    verdict_box = (left_x, y + 296, left_x + 600, y + 492)
    draw.rounded_rectangle(verdict_box, radius=28, fill="#1F2D24")
    draw.text((verdict_box[0] + 28, verdict_box[1] + 24), "Agent 一句定性", font=load_font(21), fill="#ADC7B3")
    verdict_lines = wrap_text(draw, verdict, verdict_font, 540)
    draw_text_lines(draw, verdict_box[0] + 28, verdict_box[1] + 76, verdict_lines[:2], verdict_font, "#F4F8F5", 6)

    summary_lines = wrap_text(draw, summary, body_font, 860)
    draw_text_lines(draw, left_x, y + 550, summary_lines[:3], body_font, "#35463B", 10)

    metric_y = y + 694
    metric_width = (content_width - 88 - 32) // 3
    draw_metric_card(draw, (left_x, metric_y, left_x + metric_width, metric_y + 148), "匹配度", match_pct, "#6B8F73")
    draw_metric_card(draw, (left_x + metric_width + 16, metric_y, left_x + (metric_width + 16) * 2, metric_y + 148), "压榨指数", pressure_pct, "#8C6F56")
    draw_metric_card(draw, (left_x + (metric_width + 16) * 2, metric_y, left_x + (metric_width + 16) * 2 + metric_width, metric_y + 148), "兜底指数", support_pct, "#4F7E86")

    draw_tag_pills(draw, left_x, metric_y + 182, hero_box[2] - 44, hidden_tags)

    y = hero_box[3] + CARD_GAP
    analysis_box = (PADDING, y, PADDING + content_width, y + 286)
    rounded(draw, analysis_box, fill="#FFFFFF", outline="#D7E3D8", width=2)
    draw.text((left_x, y + 38), "该人格的简单解读", font=section_title_font, fill="#203026")
    analysis_lines = wrap_text(draw, analysis, load_font(31), 860)
    draw_text_lines(draw, left_x, y + 108, analysis_lines[:4], load_font(31), "#36473C", 10)

    y = analysis_box[3] + CARD_GAP
    metric_panel = (PADDING, y, PADDING + content_width, y + 458)
    rounded(draw, metric_panel, fill="#FFFFFF", outline="#D7E3D8", width=2)
    draw.text((left_x, y + 38), "关系参数", font=section_title_font, fill="#203026")
    draw.text((left_x, y + 78), "7 个维度的直观参数化结果", font=section_subtitle_font, fill="#75857A")
    rows = [
        ("压活强度", push_load, "#8C6F56"),
        ("深夜召唤", night_ping, "#8C6F56"),
        ("微操程度", micro_manage, "#7D7F6C"),
        ("改稿反复", revision_swing, "#946F5F"),
        ("情绪补给", care_supply, "#648B82"),
        ("一起兜底", co_burden, "#4F7E86"),
        ("放权信任", trust_delegation, "#6C8F72"),
    ]
    for index, (label, value, accent) in enumerate(rows):
        draw_progress_row(draw, left_x, y + 128 + index * 46, content_width - 88, label, value, accent)

    y = metric_panel[3] + CARD_GAP
    evidence_box = (PADDING, y, PADDING + content_width, y + 442)
    rounded(draw, evidence_box, fill="#FFFFFF", outline="#D7E3D8", width=2)
    draw.text((left_x, y + 38), "Agent 编年史摘录", font=section_title_font, fill="#203026")
    draw.text((left_x, y + 78), "我为什么会这样看你，证据都写在这里", font=section_subtitle_font, fill="#75857A")

    card_y = y + 116
    for item in evidence:
        inner = (left_x, card_y, left_x + content_width - 88, card_y + 92)
        draw.rounded_rectangle(inner, radius=24, fill="#FBFDFB", outline="#DCE8DE", width=2)
        draw.text((inner[0] + 22, inner[1] + 14), str(item.get("time_hint", "")), font=evidence_time_font, fill="#77877C")
        quote_lines = wrap_text(draw, str(item.get("quote", "")), evidence_quote_font, inner[2] - inner[0] - 44)
        note_lines = wrap_text(draw, str(item.get("comment", "")), evidence_note_font, inner[2] - inner[0] - 44)
        if quote_lines:
            draw.text((inner[0] + 22, inner[1] + 38), quote_lines[0], font=evidence_quote_font, fill="#1A261F")
        if note_lines:
            draw.text((inner[0] + 22, inner[1] + 64), note_lines[0], font=evidence_note_font, fill="#415247")
        card_y += 106

    footer_y = evidence_box[3] + 44
    footer_text = str(data.get("attribution", "友情参考：B站@蛆肉儿串儿、UnluckyNinja/SBTI-test"))
    footer_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
    draw.text(((WIDTH - (footer_bbox[2] - footer_bbox[0])) // 2, footer_y), footer_text, font=footer_font, fill="#7C8C82")
    return canvas


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_png = Path(args.output_png).expanduser().resolve()
    data = json.loads(input_path.read_text(encoding="utf-8"))
    image = build_image(data)
    image.save(output_png, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
