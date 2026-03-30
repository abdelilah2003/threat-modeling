#!/usr/bin/env bash
set -euo pipefail

docker build -f deployment/docker/Dockerfile -t enterprise-rag:${1:-latest} .
