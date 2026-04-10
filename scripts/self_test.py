#!/usr/bin/env python3
"""Local self-test for the owner-sbti skill.

This script intentionally uses only the Python standard library so the skill
can be checked on a fresh local environment.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[OK] {message}")


def main() -> None:
    skill_dir = Path(__file__).resolve().parent.parent
    required = [
        skill_dir / "SKILL.md",
        skill_dir / "agents" / "openai.yaml",
        skill_dir / "references" / "original-types.md",
        skill_dir / "references" / "original-assets.md",
        skill_dir / "references" / "relationship-types.md",
        skill_dir / "references" / "portable-agent-spec.md",
        skill_dir / "references" / "voice-guide.md",
        skill_dir / "references" / "report-spec.md",
        skill_dir / "scripts" / "render_owner_sbti.py",
        skill_dir / "scripts" / "validate_report_json.py",
        skill_dir / "assets" / "example-report.json",
    ]

    for path in required:
        if not path.exists():
            fail(f"Missing required file: {path}")
    ok("Required files are present")

    sample = skill_dir / "assets" / "example-report.json"
    data = json.loads(sample.read_text(encoding="utf-8"))
    for key in [
        "selected_original_type",
        "derived_secondary_type",
        "verdict",
        "summary",
        "share_caption",
        "top_evidence",
    ]:
        if key not in data:
            fail(f"Sample payload is missing key: {key}")
    ok("Sample payload shape looks valid")

    html_out = skill_dir / "assets" / "example-report.html"
    md_out = skill_dir / "assets" / "example-report.md"
    render_script = skill_dir / "scripts" / "render_owner_sbti.py"
    validate_script = skill_dir / "scripts" / "validate_report_json.py"

    validate_result = subprocess.run(
        [sys.executable, str(validate_script), "--input", str(sample)],
        capture_output=True,
        text=True,
    )
    if validate_result.returncode != 0:
        fail(f"Validator failed:\n{validate_result.stderr.strip() or validate_result.stdout.strip()}")
    ok("Validator executed successfully")

    result = subprocess.run(
        [
            sys.executable,
            str(render_script),
            "--input",
            str(sample),
            "--output-html",
            str(html_out),
            "--output-md",
            str(md_out),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"Renderer failed:\n{result.stderr.strip()}")
    ok("Renderer executed successfully")

    html_text = html_out.read_text(encoding="utf-8")
    md_text = md_out.read_text(encoding="utf-8")
    if "系统分享" not in html_text or "复制朋友圈文案" not in html_text:
        fail("Generated HTML is missing share controls")
    if data["derived_secondary_type"] not in html_text:
        fail("Generated HTML is missing the secondary type")
    if data["verdict"] not in md_text:
        fail("Generated Markdown is missing the verdict")
    ok("Generated outputs contain expected content")

    print("[DONE] owner-sbti local self-test passed")


if __name__ == "__main__":
    main()
