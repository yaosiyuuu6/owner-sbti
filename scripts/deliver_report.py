#!/usr/bin/env python3
"""Deliver an owner-sbti PNG image to a supported chat channel."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import shutil
import subprocess
import urllib.error
import urllib.request
import uuid
from pathlib import Path


CHANNELS = ("auto", "none", "lark", "telegram", "whatsapp")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, help="Path to the PNG image.")
    parser.add_argument("--caption", help="Optional caption or text summary.")
    parser.add_argument("--channel", choices=CHANNELS, default="auto", help="Delivery channel.")
    parser.add_argument("--target", help="Optional explicit target for the selected channel.")
    return parser.parse_args()


def env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


def build_multipart(fields: dict[str, str], files: dict[str, Path]) -> tuple[bytes, str]:
    boundary = f"----owner-sbti-{uuid.uuid4().hex}"
    chunks: list[bytes] = []

    for key, value in fields.items():
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
        chunks.append(str(value).encode("utf-8"))
        chunks.append(b"\r\n")

    for key, path in files.items():
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(
            f'Content-Disposition: form-data; name="{key}"; filename="{path.name}"\r\n'.encode()
        )
        chunks.append(f"Content-Type: {mime}\r\n\r\n".encode())
        chunks.append(path.read_bytes())
        chunks.append(b"\r\n")

    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def post_json(url: str, payload: dict[str, object], headers: dict[str, str] | None = None) -> dict[str, object]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


def post_multipart(
    url: str,
    fields: dict[str, str],
    files: dict[str, Path],
    headers: dict[str, str] | None = None,
) -> dict[str, object]:
    data, content_type = build_multipart(fields, files)
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": content_type, **(headers or {})},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


def deliver_lark(image: Path, caption: str | None, target: str | None) -> dict[str, str]:
    chat_id = None
    user_id = None
    if target:
        if target.startswith("oc_"):
            chat_id = target
        else:
            user_id = target
    else:
        chat_id = env("OWNER_SBTI_LARK_CHAT_ID")
        user_id = env("OWNER_SBTI_LARK_USER_ID")
    if not chat_id and not user_id:
        raise RuntimeError("Missing Lark target. Set OWNER_SBTI_LARK_CHAT_ID or OWNER_SBTI_LARK_USER_ID.")

    image_arg = f"./{image.name}"
    base = ["lark-cli", "im", "+messages-send", "--as", "bot", "--image", image_arg]
    if chat_id:
        send_cmd = base + ["--chat-id", chat_id]
        target_value = chat_id
    else:
        send_cmd = base + ["--user-id", user_id]
        target_value = user_id or ""

    result = subprocess.run(send_cmd, capture_output=True, text=True, check=False, cwd=str(image.parent))
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Lark image send failed")

    if caption:
        text_cmd = ["lark-cli", "im", "+messages-send", "--as", "bot", "--text", caption]
        if chat_id:
            text_cmd += ["--chat-id", chat_id]
        else:
            text_cmd += ["--user-id", user_id or ""]
        subprocess.run(text_cmd, capture_output=True, text=True, check=False)

    return {"channel": "lark", "target": target_value}


def deliver_telegram(image: Path, caption: str | None, target: str | None) -> dict[str, str]:
    bot_token = env("OWNER_SBTI_TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_TOKEN")
    chat_id = target or env("OWNER_SBTI_TELEGRAM_CHAT_ID", "TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        raise RuntimeError("Missing Telegram target. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.")

    payload = {"chat_id": chat_id}
    if caption:
        payload["caption"] = caption

    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    response = post_multipart(url, payload, {"photo": image})
    if not response.get("ok"):
        raise RuntimeError(f"Telegram send failed: {response}")
    return {"channel": "telegram", "target": str(chat_id)}


def deliver_whatsapp(image: Path, caption: str | None, target: str | None) -> dict[str, str]:
    access_token = env("OWNER_SBTI_WHATSAPP_ACCESS_TOKEN", "WHATSAPP_ACCESS_TOKEN")
    phone_id = env("OWNER_SBTI_WHATSAPP_PHONE_NUMBER_ID", "WHATSAPP_PHONE_NUMBER_ID")
    to = target or env("OWNER_SBTI_WHATSAPP_TO", "WHATSAPP_TO")
    if not access_token or not phone_id or not to:
        raise RuntimeError(
            "Missing WhatsApp target. Set WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID, and WHATSAPP_TO."
        )

    headers = {"Authorization": f"Bearer {access_token}"}
    upload = post_multipart(
        f"https://graph.facebook.com/v19.0/{phone_id}/media",
        {"messaging_product": "whatsapp", "type": "image/png"},
        {"file": image},
        headers=headers,
    )
    media_id = upload.get("id")
    if not media_id:
        raise RuntimeError(f"WhatsApp upload failed: {upload}")

    payload: dict[str, object] = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {"id": media_id},
    }
    if caption:
        payload["image"] = {"id": media_id, "caption": caption}

    sent = post_json(f"https://graph.facebook.com/v19.0/{phone_id}/messages", payload, headers=headers)
    if sent.get("error"):
        raise RuntimeError(f"WhatsApp send failed: {sent}")
    return {"channel": "whatsapp", "target": str(to)}


def auto_channel() -> str:
    forced = env("OWNER_SBTI_CHANNEL")
    if forced in CHANNELS:
        return forced
    if env("OWNER_SBTI_LARK_CHAT_ID", "OWNER_SBTI_LARK_USER_ID") and shutil.which("lark-cli"):
        return "lark"
    if env("OWNER_SBTI_TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_TOKEN") and env(
        "OWNER_SBTI_TELEGRAM_CHAT_ID", "TELEGRAM_CHAT_ID"
    ):
        return "telegram"
    if env("OWNER_SBTI_WHATSAPP_ACCESS_TOKEN", "WHATSAPP_ACCESS_TOKEN") and env(
        "OWNER_SBTI_WHATSAPP_PHONE_NUMBER_ID", "WHATSAPP_PHONE_NUMBER_ID"
    ) and env("OWNER_SBTI_WHATSAPP_TO", "WHATSAPP_TO"):
        return "whatsapp"
    return "none"


def main() -> None:
    args = parse_args()
    image = Path(args.image).expanduser().resolve()
    if not image.exists():
        raise SystemExit(f"Image not found: {image}")

    channel = args.channel if args.channel != "auto" else auto_channel()
    caption = args.caption.strip() if args.caption else None

    if channel == "none":
        print(json.dumps({"status": "skipped", "channel": "none", "image": str(image)}, ensure_ascii=False))
        return

    try:
        if channel == "lark":
            result = deliver_lark(image, caption, args.target)
        elif channel == "telegram":
            result = deliver_telegram(image, caption, args.target)
        elif channel == "whatsapp":
            result = deliver_whatsapp(image, caption, args.target)
        else:
            raise RuntimeError(f"Unsupported channel: {channel}")
    except (RuntimeError, urllib.error.URLError) as exc:
        print(
            json.dumps(
                {"status": "fallback", "channel": channel, "image": str(image), "error": str(exc)},
                ensure_ascii=False,
            )
        )
        return

    result["status"] = "sent"
    result["image"] = str(image)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
