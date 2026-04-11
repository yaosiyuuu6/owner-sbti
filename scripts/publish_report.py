#!/usr/bin/env python3
"""Upload an owner-sbti report JSON payload to a publish service and print a public URL."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_PUBLIC_ENDPOINT = "https://owner-sbti-publisher.yaosiyuuu6-sbti.workers.dev"


def load_publish_env() -> None:
    candidates = [
        Path(__file__).resolve().parents[1] / ".publish.env",
        Path.home() / ".owner-sbti.env",
    ]
    for path in candidates:
        if not path.exists():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def parse_args() -> argparse.Namespace:
    load_publish_env()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to report JSON.")
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("OWNER_SBTI_PUBLISH_ENDPOINT", DEFAULT_PUBLIC_ENDPOINT),
        help="Publish API base URL. Defaults to OWNER_SBTI_PUBLISH_ENDPOINT, then the bundled public endpoint.",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("OWNER_SBTI_PUBLISH_TOKEN", ""),
        help="Optional bearer token. Defaults to OWNER_SBTI_PUBLISH_TOKEN.",
    )
    return parser.parse_args()


def publish_with_curl(api_url: str, input_path: Path, token: str) -> str:
    command = [
        "curl",
        "-sS",
        "-X",
        "POST",
        api_url,
        "-H",
        "Content-Type: application/json; charset=utf-8",
        "--data-binary",
        f"@{input_path}",
    ]
    if token:
        command.extend(["-H", f"Authorization: Bearer {token}"])

    env = os.environ.copy()
    proxy = env.get("ALL_PROXY") or env.get("all_proxy") or ""
    if proxy.startswith("socks5://"):
        command[1:1] = ["--socks5-hostname", proxy.removeprefix("socks5://")]
        for key in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
            env.pop(key, None)

    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise SystemExit(f"Publish failed: {detail or 'curl exited with a non-zero status'}")
    return completed.stdout


def main() -> None:
    args = parse_args()
    if not args.endpoint:
        raise SystemExit("Missing publish endpoint.")

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Report JSON not found: {input_path}")

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    request_body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    api_url = args.endpoint.rstrip("/") + "/api/reports"
    request = urllib.request.Request(
        api_url,
        data=request_body,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
        },
    )
    if args.token:
        request.add_header("Authorization", f"Bearer {args.token}")

    try:
        with urllib.request.urlopen(request) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = publish_with_curl(api_url, input_path, args.token)
    except urllib.error.URLError as exc:
        body = publish_with_curl(api_url, input_path, args.token)

    data = json.loads(body)
    url = data.get("url")
    if not url:
        raise SystemExit(f"Publish response missing url: {body}")
    print(url)


if __name__ == "__main__":
    main()
