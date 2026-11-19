#!/usr/bin/env bash
# Linux/Mac/VPS: instalar, probar y arrancar
set -e
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q -e .
[ -f .env ] || { cp .env.example .env; echo "Rellena DISCORD_WEBHOOK_DEFAULT en .env y vuelve a ejecutar"; exit 1; }
.venv/bin/cookgroup probe || true
.venv/bin/cookgroup test-webhook
exec .venv/bin/cookgroup run
