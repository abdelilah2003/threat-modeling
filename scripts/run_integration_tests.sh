#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="${PYTHONPATH:-}:."

mkdir -p reports/junit
pytest app/tests/test_api.py -q --junitxml=reports/junit/integration_tests.xml
