#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-staging}"
echo "Deploying enterprise-rag to ${ENVIRONMENT} (simulation)"
mkdir -p reports
printf "{\n  \"environment\": \"%s\",\n  \"status\": \"deployed\"\n}\n" "${ENVIRONMENT}" > "reports/deploy_${ENVIRONMENT}.json"
