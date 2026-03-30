#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="${PYTHONPATH:-}:."

mkdir -p reports/junit
pytest app/tests -q --junitxml=reports/junit/unit_tests.xml
