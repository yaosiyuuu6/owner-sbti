#!/usr/bin/env python3
"""Upload an owner-sbti report JSON payload to a publish service and print a public URL."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to report JSON.")
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("OWNER_SBTI_PUBLISH_ENDPOINT", ""),
        help="Publish API base URL. Defaults to OWNER_SBTI_PUBLISH_ENDPOINT.",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("OWNER_SBTI_PUBLISH_TOKEN", ""),
        help="Optional bearer token. Defaults to OWNER_SBTI_PUBLISH_TOKEN.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.endpoint:
        raise SystemExit("Missing publish endpoint. Set --endpoint or OWNER_SBTI_PUBLISH_ENDPOINT.")

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
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Publish failed: HTTP {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Publish failed: {exc.reason}") from exc

    data = json.loads(body)
    url = data.get("url")
    if not url:
        raise SystemExit(f"Publish response missing url: {body}")
    print(url)


if __name__ == "__main__":
    main()
