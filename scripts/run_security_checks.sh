#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports/security

pip-audit -r requirements.txt -f json -o reports/security/pip_audit.json || true
bandit -r app -f json -o reports/security/bandit.json || true

# Placeholder secret scan (replace with gitleaks/trufflehog in real pipelines)
if rg -n "(AKIA[0-9A-Z]{16}|-----BEGIN (RSA|OPENSSH|EC) PRIVATE KEY-----|xox[baprs]-[A-Za-z0-9-]+)" app scripts deployment model rag eval > reports/security/secret_scan.txt; then
  echo "Potential secrets detected" >&2
  exit 1
else
  echo "No obvious secrets found" > reports/security/secret_scan.txt
fi
