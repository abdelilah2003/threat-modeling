#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="${PYTHONPATH:-}:."

mkdir -p reports/junit
python - <<'PY'
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

ok = True

res = client.get('/health')
if res.status_code != 200:
    ok = False

res = client.post('/ask', json={'question': 'What are AI release guardrails?'})
if res.status_code != 200 or 'answer' not in res.json():
    ok = False

xml = f'''<testsuite name="smoke" tests="2" failures="{0 if ok else 1}"></testsuite>'''
open('reports/junit/smoke_tests.xml', 'w', encoding='utf-8').write(xml)

if not ok:
    raise SystemExit(1)
PY
