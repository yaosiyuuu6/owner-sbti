#!/usr/bin/env python3
"""Validate, render, and auto-publish an owner-sbti report payload."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to report JSON.")
    parser.add_argument(
        "--output-html",
        help="Optional output HTML path. Defaults to <input>.html next to the JSON file.",
    )
    parser.add_argument(
        "--output-md",
        help="Optional output Markdown path. Defaults to <input>.md next to the JSON file.",
    )
    parser.add_argument(
        "--no-publish",
        action="store_true",
        help="Skip public publish and print only the local HTML path.",
    )
    parser.add_argument(
        "--publish-endpoint",
        help="Optional publish endpoint override for scripts/publish_report.py.",
    )
    parser.add_argument(
        "--publish-token",
        help="Optional publish token override for scripts/publish_report.py.",
    )
    return parser.parse_args()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def main() -> None:
    args = parse_args()
    skill_dir = Path(__file__).resolve().parent.parent
    input_path = Path(args.input).expanduser().resolve()
    stem = input_path.with_suffix("")
    html_out = Path(args.output_html).expanduser().resolve() if args.output_html else stem.with_suffix(".html")
    md_out = Path(args.output_md).expanduser().resolve() if args.output_md else stem.with_suffix(".md")

    validate = run(
        [
            sys.executable,
            str(skill_dir / "scripts" / "validate_report_json.py"),
            "--input",
            str(input_path),
        ]
    )
    if validate.returncode != 0:
        raise SystemExit(validate.stderr.strip() or validate.stdout.strip() or "Validation failed")

    render = run(
        [
            sys.executable,
            str(skill_dir / "scripts" / "render_owner_sbti.py"),
            "--input",
            str(input_path),
            "--output-html",
            str(html_out),
            "--output-md",
            str(md_out),
        ]
    )
    if render.returncode != 0:
        raise SystemExit(render.stderr.strip() or render.stdout.strip() or "Render failed")

    if args.no_publish:
        print(html_out)
        return

    publish_command = [
        sys.executable,
        str(skill_dir / "scripts" / "publish_report.py"),
        "--input",
        str(input_path),
    ]
    if args.publish_endpoint:
        publish_command.extend(["--endpoint", args.publish_endpoint])
    if args.publish_token:
        publish_command.extend(["--token", args.publish_token])

    publish = run(publish_command)
    if publish.returncode == 0:
        print(publish.stdout.strip())
        return

    print(html_out)
    sys.stderr.write(
        (publish.stderr.strip() or publish.stdout.strip() or "Publish failed; returned local HTML path instead.")
        + "\n"
    )


if __name__ == "__main__":
    main()
