#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="${PYTHONPATH:-}:."

python - <<'PY'
from __future__ import annotations
import json
from pathlib import Path
import yaml

from app.rag_pipeline import RagPipeline


def token_set_similarity(a: str, b: str) -> float:
    aset = set(a.lower().split())
    bset = set(b.lower().split())
    if not aset or not bset:
        return 0.0
    return len(aset & bset) / len(aset | bset)

pipeline = RagPipeline()
dataset = json.loads(Path("eval/datasets/eval.json").read_text(encoding="utf-8"))

rows = []
sim_scores = []
grounded_hits = 0
expected_hit_rate = 0
for item in dataset:
    out = pipeline.ask(item["question"])
    answer = out["answer"]
    docs = out["retrieved_documents"]
    ctx = " ".join(d["content"] for d in docs).lower()

    contains = item.get("expected_contains", [])
    hit = all(term.lower() in answer.lower() for term in contains)
    if hit:
        expected_hit_rate += 1

    sim = token_set_similarity(" ".join(contains), answer)
    grounded = all(term.lower() in ctx for term in contains)
    if grounded:
        grounded_hits += 1

    sim_scores.append(sim)
    rows.append({
        "id": item["id"],
        "question": item["question"],
        "answer": answer,
        "similarity": round(sim, 4),
        "grounded": grounded,
        "expected_contains_hit": hit,
    })

avg_similarity = sum(sim_scores) / len(sim_scores)
groundedness = grounded_hits / len(dataset)
expected_contains_rate = expected_hit_rate / len(dataset)

report = {
    "samples": len(dataset),
    "avg_similarity": round(avg_similarity, 4),
    "groundedness": round(groundedness, 4),
    "expected_contains_rate": round(expected_contains_rate, 4),
    "rows": rows,
}

Path("reports/eval").mkdir(parents=True, exist_ok=True)
Path("reports/eval/eval_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

manifest = yaml.safe_load(Path("ai_release.yaml").read_text(encoding="utf-8"))
gates = manifest["quality_gates"]

errors = []
if avg_similarity < gates["eval_similarity_min"]:
    errors.append("avg_similarity below threshold")
if groundedness < gates["eval_groundedness_min"]:
    errors.append("groundedness below threshold")
if expected_contains_rate < gates["expected_contains_rate_min"]:
    errors.append("expected_contains_rate below threshold")

if errors:
    for err in errors:
        print(f"ERROR: {err}")
    raise SystemExit(1)

print(json.dumps(report, indent=2))
print("Model evaluation passed")
PY
