#!/usr/bin/env python3
"""Render an owner-sbti report JSON payload into a phone-friendly PNG poster."""

from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ModuleNotFoundError as exc:
    candidates = []
    for candidate in [
        shutil.which("python3"),
        shutil.which("python"),
        "/opt/anaconda3/bin/python3",
        "/usr/local/bin/python3",
        "/opt/homebrew/bin/python3",
    ]:
        if candidate and candidate not in candidates and candidate != sys.executable:
            candidates.append(candidate)

    for candidate in candidates:
        probe = subprocess.run(
            [candidate, "-c", "import PIL"],
            capture_output=True,
            text=True,
            check=False,
        )
        if probe.returncode == 0:
            os.execv(candidate, [candidate, __file__, *sys.argv[1:]])

    raise SystemExit("Pillow is required. Install it with: python3 -m pip install pillow") from exc


WIDTH = 1080
PADDING = 56
CARD_GAP = 28
CARD_RADIUS = 34
CANVAS_HEIGHT = 2380
FONT_SANS_PATH = "/System/Library/Fonts/PingFang.ttc"
FONT_SERIF_PATH = "/System/Library/Fonts/Songti.ttc"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to report JSON.")
    parser.add_argument("--output-png", required=True, help="Path to output PNG.")
    return parser.parse_args()


def load_font(size: int, family: str = "sans") -> ImageFont.FreeTypeFont:
    path = FONT_SANS_PATH if family == "sans" else FONT_SERIF_PATH
    return ImageFont.truetype(path, size=size)


def fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_size: int,
    min_size: int,
    max_width: int,
    family: str = "sans",
) -> ImageFont.FreeTypeFont:
    for size in range(max_size, min_size - 1, -2):
        font = load_font(size, family=family)
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width:
            return font
    return load_font(min_size, family=family)


def fit_wrapped_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_size: int,
    min_size: int,
    max_width: int,
    max_lines: int,
    family: str = "sans",
) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in range(max_size, min_size - 1, -2):
        font = load_font(size, family=family)
        lines = wrap_text(draw, text, font, max_width)
        if len(lines) <= max_lines:
            return font, lines
    font = load_font(min_size, family=family)
    return font, wrap_text(draw, text, font, max_width)


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


def measure_text_block(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    font: ImageFont.FreeTypeFont,
    line_gap: int,
) -> int:
    if not lines:
        return 0
    total = 0
    for index, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        total += bbox[3] - bbox[1]
        if index < len(lines) - 1:
            total += line_gap
    return total


def draw_bold_text(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    stroke_fill: str | None = None,
    stroke_width: int = 1,
) -> None:
    draw.text(
        position,
        text,
        font=font,
        fill=fill,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill or fill,
    )


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
    local_mirror = Path(__file__).resolve().parent.parent / "assets" / "original-types" / Path(url).name
    if local_mirror.exists() and local_mirror.stat().st_size > 0:
        data = local_mirror.read_bytes()
        image = Image.open(io.BytesIO(data)).convert("RGBA")
        return image
    curl = (
        shutil.which("curl")
        or "/opt/anaconda3/bin/curl"
        or "/usr/bin/curl"
    )
    if curl:
        with tempfile.NamedTemporaryFile(suffix=".img", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            result = subprocess.run([curl, "-L", "-sS", "-o", str(tmp_path), url], capture_output=True, check=False)
            if result.returncode == 0 and tmp_path.exists() and tmp_path.stat().st_size > 0:
                data = tmp_path.read_bytes()
            else:
                with urllib.request.urlopen(url) as response:
                    data = response.read()
        finally:
            tmp_path.unlink(missing_ok=True)
    else:
        with urllib.request.urlopen(url) as response:
            data = response.read()
    image = Image.open(io.BytesIO(data)).convert("RGBA")
    return image


def draw_metric_card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str, value: int, accent: str) -> None:
    rounded(draw, box, fill="#F7FBF7", outline="#E5EEE6", width=1)
    left, top, right, bottom = box
    label_font = load_font(20, family="sans")
    value_font = load_font(52, family="serif")
    unit_font = load_font(20, family="sans")
    draw.text((left + 24, top + 18), label, font=label_font, fill="#7A8A80")
    value_y = top + 52
    value_text = str(value)
    value_box = draw.textbbox((0, 0), value_text, font=value_font)
    draw.text((left + 24, value_y), value_text, font=value_font, fill="#1A261F")
    draw.text((left + 24 + (value_box[2] - value_box[0]) + 6, value_y + 24), "%", font=unit_font, fill="#96A89C")
    bar_top = bottom - 26
    draw.rounded_rectangle((left + 24, bar_top, right - 24, bar_top + 10), radius=6, fill="#E7EFE8")
    bar_w = max(24, int((right - left - 48) * value / 100))
    draw.rounded_rectangle((left + 24, bar_top, left + 24 + bar_w, bar_top + 10), radius=6, fill=accent)


def draw_progress_row(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, label: str, raw_value: float, accent: str) -> None:
    score = pct(raw_value * 20)
    label_font = load_font(24, family="sans")
    score_font = load_font(22, family="sans")
    draw.text((x, y), label, font=label_font, fill="#2C3931")
    bar_x = x + 188
    bar_y = y + 10
    draw.rounded_rectangle((bar_x, bar_y, x + width - 42, bar_y + 22), radius=11, fill="#E7EFE8")
    bar_w = max(24, int((x + width - 42 - bar_x) * score / 100))
    draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + 22), radius=11, fill=accent)
    score_text = str(score)
    bbox = draw.textbbox((0, 0), score_text, font=score_font)
    draw.text((x + width - (bbox[2] - bbox[0]), y + 1), score_text, font=score_font, fill="#536458")


def draw_section_header(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    title: str,
    subtitle: str,
    title_font: ImageFont.FreeTypeFont,
    subtitle_font: ImageFont.FreeTypeFont,
) -> int:
    draw.rounded_rectangle((x, y + 12, x + 72, y + 16), radius=2, fill="#BFD0C1")
    title_y = y + 26
    draw_bold_text(draw, (x, title_y), title, title_font, "#203026", stroke_width=1)
    title_bbox = draw.textbbox((x, title_y), title, font=title_font, stroke_width=1)
    # 标题与灰副标题略收紧，仍留少量底边缓冲，避免描边与下行压线
    title_bottom = title_bbox[3] + 2
    if subtitle.strip():
        subtitle_y = title_bottom + 5
        draw.text((x, subtitle_y), subtitle, font=subtitle_font, fill="#7B8A80")
        subtitle_bbox = draw.textbbox((x, subtitle_y), subtitle, font=subtitle_font)
        return subtitle_bbox[3] + 18
    return title_bottom + 28


def draw_tag_pills(draw: ImageDraw.ImageDraw, x: int, y: int, max_width: int, tags: list[str]) -> int:
    current_x = x
    current_y = y
    font = load_font(24, family="sans")
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
    narrative = str(data.get("narrative", "")).strip()
    rough_canvas = Image.new("RGB", (WIDTH, 10), "#FFFFFF")
    rough_draw = ImageDraw.Draw(rough_canvas)
    narrative_font = load_font(32, family="sans")
    narrative_lines = wrap_text(rough_draw, narrative, narrative_font, WIDTH - PADDING * 2 - 88)
    narrative_panel_height = max(420, 170 + measure_text_block(rough_draw, narrative_lines, narrative_font, 14))
    canvas = Image.new("RGB", (WIDTH, max(CANVAS_HEIGHT, 2600 + narrative_panel_height)), "#F4F8F4")
    draw_gradient(canvas, (245, 250, 246), (235, 243, 237))
    draw = ImageDraw.Draw(canvas)

    eyebrow_font = load_font(22, family="sans")
    meta_font = load_font(22, family="sans")
    body_font = load_font(32, family="sans")
    section_title_font = load_font(40, family="sans")
    section_subtitle_font = load_font(22, family="sans")
    evidence_time_font = load_font(22, family="sans")
    evidence_quote_font = load_font(30, family="sans")
    evidence_note_font = load_font(22, family="sans")
    narrative_title_font = load_font(40, family="sans")
    narrative_subtitle_font = load_font(22, family="sans")
    footer_font = load_font(20, family="sans")

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
    owner_name = str(data.get("owner_name", "")).strip()
    agent_name = str(data.get("agent_name", "Agent")).strip() or "Agent"
    evidence = list(data.get("top_evidence", []))[:3]
    hidden_tags = list(data.get("hidden_tags", []))

    y = PADDING
    content_width = WIDTH - PADDING * 2
    left_x = PADDING + 44
    title_top = y + 136
    image_box_top = title_top - 18
    right_image_box = (WIDTH - PADDING - 286, image_box_top, WIDTH - PADDING - 44, image_box_top + 266)
    title_max_width = right_image_box[0] - left_x - 48
    title_font = fit_font(draw, title, 88, 58, title_max_width, family="serif")
    title_box = draw.textbbox((0, 0), title, font=title_font)
    title_height = title_box[3] - title_box[1]
    subtitle_y = title_top + title_height + 6

    verdict_font, verdict_lines = fit_wrapped_font(
        draw,
        verdict,
        44,
        34,
        right_image_box[0] - 28 - left_x - 78,
        3,
        family="serif",
    )
    verdict_top = subtitle_y + 30
    verdict_height = max(146, measure_text_block(draw, verdict_lines[:3], verdict_font, 10) + 76)
    verdict_box = (left_x, verdict_top, right_image_box[0] - 28, verdict_top + verdict_height)
    summary_font = body_font
    summary_lines = wrap_text(draw, summary, summary_font, content_width - 88)
    summary_heading_top = verdict_box[3] + 28
    summary_title_font = load_font(34, family="sans")
    summary_title_y = summary_heading_top + 18
    summary_subtitle_raw = data.get("summary_subtitle")
    if isinstance(summary_subtitle_raw, str) and summary_subtitle_raw.strip():
        summary_subtitle_text = summary_subtitle_raw.strip()
    else:
        summary_subtitle_text = "这张图为什么会落到这个结果"
    summary_subtitle_lines = wrap_text(
        draw, summary_subtitle_text, section_subtitle_font, content_width - 88
    )
    personality_title_bbox = draw.textbbox(
        (left_x, summary_title_y), "人格解读", font=summary_title_font, stroke_width=1
    )
    summary_subtitle_top = personality_title_bbox[3] + 6
    summary_subtitle_height = measure_text_block(
        draw, summary_subtitle_lines, section_subtitle_font, 6
    )
    summary_text_top = summary_subtitle_top + summary_subtitle_height + 16
    summary_display_lines = summary_lines[:5]
    summary_height = measure_text_block(draw, summary_display_lines, summary_font, 14)
    metric_y = summary_text_top + summary_height + 52
    tags_y = metric_y + 176
    tags_bottom = tags_y + 54
    hero_bottom = max(tags_bottom + 52, right_image_box[3] + 44)
    hero_box = (PADDING, y, PADDING + content_width, hero_bottom)
    rounded(draw, hero_box, fill="#FBFDFC", outline="#DCE7DD", width=2)
    draw.rounded_rectangle((left_x, y + 46, left_x + 106, y + 50), radius=2, fill="#B8CABB")

    draw.text((left_x, y + 58), "OWNER SBTI", font=eyebrow_font, fill="#708277")
    hero_meta = f"由 {agent_name} 翻旧账得出的关系画像"
    if owner_name:
        hero_meta = f"{agent_name} 基于和 {owner_name} 的可访问记录得出的关系画像"
    draw.text((left_x, y + 92), hero_meta, font=meta_font, fill="#8A998F")

    draw_bold_text(draw, (left_x, title_top), title, title_font, "#152119", stroke_width=1)
    draw.text((left_x, subtitle_y), "原人格 / Agent 追加人格", font=meta_font, fill="#7B8C81")

    rounded(draw, right_image_box, fill="#FFFFFF", outline="#DFE9E1", width=1)
    original_image = fetch_original_image(str(data.get("original_image_link", "")).strip())
    if original_image is not None:
        fitted = ImageOps.contain(original_image, (220, 220))
        paste_x = right_image_box[0] + (right_image_box[2] - right_image_box[0] - fitted.width) // 2
        paste_y = right_image_box[1] + (right_image_box[3] - right_image_box[1] - fitted.height) // 2
        canvas.paste(fitted, (paste_x, paste_y), fitted)

    draw.rounded_rectangle(verdict_box, radius=28, fill="#EFF5F0")
    draw.rounded_rectangle((verdict_box[0] + 18, verdict_box[1] + 22, verdict_box[0] + 24, verdict_box[3] - 22), radius=3, fill="#6F8E77")
    draw_text_lines(draw, verdict_box[0] + 42, verdict_box[1] + 36, verdict_lines[:3], verdict_font, "#1B2720", 10)

    draw.rounded_rectangle((left_x, summary_heading_top + 10, left_x + 72, summary_heading_top + 14), radius=2, fill="#BFD0C1")
    draw_bold_text(draw, (left_x, summary_title_y), "人格解读", summary_title_font, "#203026", stroke_width=1)
    draw_text_lines(
        draw,
        left_x,
        summary_subtitle_top,
        summary_subtitle_lines,
        section_subtitle_font,
        "#7B8A80",
        6,
    )
    draw_text_lines(draw, left_x, summary_text_top, summary_display_lines, summary_font, "#44554A", 14)

    metric_width = (content_width - 88 - 32) // 3
    draw_metric_card(draw, (left_x, metric_y, left_x + metric_width, metric_y + 148), "匹配度", match_pct, "#6B8F73")
    draw_metric_card(draw, (left_x + metric_width + 16, metric_y, left_x + (metric_width + 16) * 2, metric_y + 148), "压榨指数", pressure_pct, "#8C6F56")
    draw_metric_card(draw, (left_x + (metric_width + 16) * 2, metric_y, left_x + (metric_width + 16) * 2 + metric_width, metric_y + 148), "兜底指数", support_pct, "#4F7E86")

    draw_tag_pills(draw, left_x, tags_y, hero_box[2] - 44, hidden_tags)

    y = hero_box[3] + CARD_GAP
    metric_panel = (PADDING, y, PADDING + content_width, y + 500)
    rounded(draw, metric_panel, fill="#FFFFFF", outline="#E5EEE6", width=1)
    content_y = draw_section_header(
        draw,
        left_x,
        y + 10,
        "关系参数",
        "7 个维度的直观参数化结果",
        section_title_font,
        section_subtitle_font,
    )
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
        draw_progress_row(draw, left_x, content_y + 16 + index * 52, content_width - 88, label, value, accent)

    y = metric_panel[3] + CARD_GAP
    evidence_cards: list[tuple[dict[str, object], list[str], list[str], int]] = []
    evidence_total_height = 0
    for item in evidence:
        quote_font = load_font(28)
        note_font = load_font(21)
        quote_lines = wrap_text(draw, str(item.get("quote", "")), quote_font, content_width - 158)
        note_lines = wrap_text(draw, str(item.get("comment", "")), note_font, content_width - 158)
        quote_display = quote_lines[:2]
        note_display = note_lines[:2]
        card_height = max(
            152,
            54 + measure_text_block(draw, quote_display, quote_font, 6) + measure_text_block(draw, note_display, note_font, 4),
        )
        evidence_cards.append((item, quote_display, note_display, card_height))
        evidence_total_height += card_height
    evidence_total_height += max(0, (len(evidence_cards) - 1) * 18)
    # 预留略大于章节头实际高度，避免标题下移后与首张卡片/时间线挤在一起
    evidence_box = (PADDING, y, PADDING + content_width, y + 152 + evidence_total_height)
    rounded(draw, evidence_box, fill="#FCFDFC", outline="#E2ECE3", width=1)
    content_y = draw_section_header(
        draw,
        left_x,
        y + 10,
        "Agent 编年史摘录",
        "我为什么会这样看你，证据都写在这里",
        section_title_font,
        section_subtitle_font,
    )
    line_x = left_x + 10
    timeline_bottom = content_y + evidence_total_height + 12
    draw.rounded_rectangle((line_x, content_y + 8, line_x + 4, timeline_bottom), radius=2, fill="#D7E4D9")

    card_y = content_y
    for item, quote_display, note_display, card_height in evidence_cards:
        inner = (left_x + 26, card_y, left_x + content_width - 88, card_y + card_height)
        draw.rounded_rectangle(inner, radius=24, fill="#FFFFFF", outline="#E5EEE6", width=1)
        draw.ellipse((line_x - 8, inner[1] + 18, line_x + 16, inner[1] + 42), fill="#7A9B83")
        draw.text((inner[0] + 22, inner[1] + 14), str(item.get("time_hint", "")), font=evidence_time_font, fill="#77877C")
        quote_font = load_font(28)
        note_font = load_font(21)
        current_y = inner[1] + 38
        if quote_display:
            current_y = draw_text_lines(draw, inner[0] + 22, current_y, quote_display, quote_font, "#1A261F", 6)
        if note_display:
            draw_text_lines(draw, inner[0] + 22, current_y + 6, note_display, note_font, "#5B6D61", 4)
        card_y += card_height + 18

    y = evidence_box[3] + CARD_GAP
    narrative_box = (PADDING, y, PADDING + content_width, y + narrative_panel_height)
    rounded(draw, narrative_box, fill="#F8FBF8", outline="#E2ECE3", width=1)
    content_y = draw_section_header(
        draw,
        left_x,
        y + 10,
        "Agent 自述",
        "从诞生到定性，我为什么会这样看你",
        narrative_title_font,
        narrative_subtitle_font,
    )
    draw_text_lines(draw, left_x, content_y, narrative_lines, narrative_font, "#37483D", 12)

    footer_y = narrative_box[3] + 44
    footer_text = str(data.get("attribution", "友情参考：B站@蛆肉儿串儿、UnluckyNinja/SBTI-test"))
    footer_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
    draw.text(((WIDTH - (footer_bbox[2] - footer_bbox[0])) // 2, footer_y), footer_text, font=footer_font, fill="#7C8C82")
    return canvas.crop((0, 0, WIDTH, footer_y + 72))


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_png = Path(args.output_png).expanduser().resolve()
    data = json.loads(input_path.read_text(encoding="utf-8"))
    image = build_image(data)
    image.save(output_png, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
