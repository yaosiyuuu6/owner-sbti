#!/usr/bin/env python3
"""Validate and render an owner-sbti report payload into a PNG image."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to report JSON.")
    parser.add_argument(
        "--output-png",
        help="Optional output PNG path. Defaults to <input>.png next to the JSON file.",
    )
    return parser.parse_args()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def py() -> str:
    return sys.executable or "python3"


def main() -> None:
    args = parse_args()
    skill_dir = Path(__file__).resolve().parent.parent
    input_path = Path(args.input).expanduser().resolve()
    stem = input_path.with_suffix("")
    default_png = stem.with_name(f"{stem.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png")
    png_out = Path(args.output_png).expanduser().resolve() if args.output_png else default_png

    validate = run(
        [
            py(),
            str(skill_dir / "scripts" / "validate_report_json.py"),
            "--input",
            str(input_path),
        ]
    )
    if validate.returncode != 0:
        raise SystemExit(validate.stderr.strip() or validate.stdout.strip() or "Validation failed")

    render = run(
        [
            py(),
            str(skill_dir / "scripts" / "render_owner_sbti_image.py"),
            "--input",
            str(input_path),
            "--output-png",
            str(png_out),
        ]
    )
    if render.returncode != 0:
        raise SystemExit(render.stderr.strip() or render.stdout.strip() or "Image render failed")

    print(png_out)


if __name__ == "__main__":
    main()
