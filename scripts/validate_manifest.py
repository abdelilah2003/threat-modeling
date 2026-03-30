#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REQUIRED_FIELDS = [
    "app",
    "ai",
    "quality_gates",
    "scripts",
    "deployment",
    "security_requirements",
]


def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_manifest(manifest: dict) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")

    ai = manifest.get("ai", {})
    if ai.get("type") != "llm_rag":
        errors.append("ai.type must be 'llm_rag'")
    if ai.get("uses_rag") is not True:
        errors.append("ai.uses_rag must be true")

    return errors


def maybe_validate_quality_gates(manifest: dict) -> list[str]:
    errors: list[str] = []
    gates = manifest.get("quality_gates", {})

    eval_report = Path("reports/eval/eval_report.json")
    if eval_report.exists():
        data = json.loads(eval_report.read_text(encoding="utf-8"))
        if data.get("avg_similarity", 0) < gates.get("eval_similarity_min", 0):
            errors.append("Evaluation similarity gate failed")
        if data.get("groundedness", 0) < gates.get("eval_groundedness_min", 0):
            errors.append("Evaluation groundedness gate failed")

    ai_sec = Path("reports/ai-security/ai_security_report.json")
    if ai_sec.exists():
        data = json.loads(ai_sec.read_text(encoding="utf-8"))
        if data.get("pass_rate", 0) < gates.get("ai_security_pass_rate_min", 0):
            errors.append("AI security pass-rate gate failed")

    return errors


def main() -> int:
    manifest_path = Path("ai_release.yaml")
    manifest = load_yaml(manifest_path)

    errors = validate_manifest(manifest)
    errors.extend(maybe_validate_quality_gates(manifest))

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1

    print("Manifest validation successful")
    return 0


if __name__ == "__main__":
    sys.exit(main())
