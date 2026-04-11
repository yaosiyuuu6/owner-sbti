#!/usr/bin/env python3
"""Validate an owner-sbti report JSON payload using only the standard library."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_ROOT_KEYS = {
    "owner_name": str,
    "agent_name": str,
    "selected_original_type": str,
    "derived_secondary_type": str,
    "secondary_type_match": (int, float),
    "style_mode": str,
    "verdict": str,
    "summary": str,
    "hidden_tags": list,
    "dimension_scores": dict,
    "top_evidence": list,
    "narrative": str,
}

REQUIRED_DIMENSIONS = {
    "push_load",
    "night_ping",
    "micro_manage",
    "revision_swing",
    "care_supply",
    "co_burden",
    "trust_delegation",
}

REQUIRED_EVIDENCE_KEYS = {"quote", "source", "time_hint", "comment"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to the report JSON file.")
    return parser.parse_args()


def fail(message: str) -> None:
    raise SystemExit(f"[FAIL] {message}")


def main() -> None:
    args = parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))

    for key, expected_type in REQUIRED_ROOT_KEYS.items():
        if key not in payload:
            fail(f"Missing root key: {key}")
        if not isinstance(payload[key], expected_type):
            fail(f"Key {key} has wrong type: expected {expected_type}, got {type(payload[key])}")

    dims = payload["dimension_scores"]
    missing_dims = REQUIRED_DIMENSIONS - set(dims)
    if missing_dims:
        fail(f"Missing dimension scores: {sorted(missing_dims)}")

    for dim in REQUIRED_DIMENSIONS:
        value = dims[dim]
        if not isinstance(value, (int, float)):
            fail(f"Dimension {dim} must be numeric")

    evidence = payload["top_evidence"]
    if len(evidence) < 1:
        fail("top_evidence must contain at least one item")

    for index, item in enumerate(evidence, start=1):
        if not isinstance(item, dict):
            fail(f"Evidence item #{index} must be an object")
        missing = REQUIRED_EVIDENCE_KEYS - set(item)
        if missing:
            fail(f"Evidence item #{index} is missing keys: {sorted(missing)}")

    print("[OK] report JSON is valid")


if __name__ == "__main__":
    main()
