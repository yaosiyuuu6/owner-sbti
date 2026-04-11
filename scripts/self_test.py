#!/usr/bin/env python3
"""Local self-test for the owner-sbti skill."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def py() -> str:
    return sys.executable or "python3"


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[OK] {message}")


def main() -> None:
    skill_dir = Path(__file__).resolve().parent.parent
    required = [
        skill_dir / "SKILL.md",
        skill_dir / "README.md",
        skill_dir / "agents" / "openai.yaml",
        skill_dir / "references" / "original-types.md",
        skill_dir / "references" / "original-assets.md",
        skill_dir / "references" / "relationship-types.md",
        skill_dir / "references" / "portable-agent-spec.md",
        skill_dir / "references" / "voice-guide.md",
        skill_dir / "references" / "report-spec.md",
        skill_dir / "scripts" / "deliver_report.py",
        skill_dir / "scripts" / "finalize_report.py",
        skill_dir / "scripts" / "render_owner_sbti_image.py",
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
        "top_evidence",
        "narrative",
    ]:
        if key not in data:
            fail(f"Sample payload is missing key: {key}")
    ok("Sample payload shape looks valid")

    validate_script = skill_dir / "scripts" / "validate_report_json.py"
    render_script = skill_dir / "scripts" / "render_owner_sbti_image.py"
    finalize_script = skill_dir / "scripts" / "finalize_report.py"
    png_out = skill_dir / "assets" / "example-report.png"

    validate_result = subprocess.run(
        [py(), str(validate_script), "--input", str(sample)],
        capture_output=True,
        text=True,
    )
    if validate_result.returncode != 0:
        fail(f"Validator failed:\n{validate_result.stderr.strip() or validate_result.stdout.strip()}")
    ok("Validator executed successfully")

    render_result = subprocess.run(
        [
            py(),
            str(render_script),
            "--input",
            str(sample),
            "--output-png",
            str(png_out),
        ],
        capture_output=True,
        text=True,
    )
    if render_result.returncode != 0:
        fail(f"Image renderer failed:\n{render_result.stderr.strip() or render_result.stdout.strip()}")
    ok("Image renderer executed successfully")

    finalize_result = subprocess.run(
        [
            py(),
            str(finalize_script),
            "--input",
            str(sample),
            "--output-png",
            str(png_out),
            "--deliver",
            "none",
        ],
        capture_output=True,
        text=True,
    )
    if finalize_result.returncode != 0:
        fail(f"Finalize script failed:\n{finalize_result.stderr.strip() or finalize_result.stdout.strip()}")
    if str(png_out) not in finalize_result.stdout:
        fail("Finalize script did not return the expected PNG path")
    ok("Finalize script executed successfully")

    if not png_out.exists() or png_out.stat().st_size <= 0:
        fail("Generated PNG is missing or empty")
    ok("Generated image output exists")

    print("[DONE] owner-sbti local self-test passed")


if __name__ == "__main__":
    main()
