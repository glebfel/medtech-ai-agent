#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== MedAssistAI ==="
echo ""

if ! command -v docker &>/dev/null; then
    echo "Docker not found. Install: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker info &>/dev/null; then
    echo "Docker daemon is not running. Start Docker and try again."
    exit 1
fi

if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Edit .env to add your API keys, then re-run this script."
    exit 0
fi

echo "Building and starting containers..."
docker compose up -d --build

echo ""
echo "Waiting for app to start..."
for i in $(seq 1 30); do
    if curl -s http://localhost:8501/_stcore/health &>/dev/null; then
        echo ""
        echo "MedAssistAI is ready: http://localhost:8501"
        exit 0
    fi
    printf "."
    sleep 1
done

echo ""
echo "App is starting... check: docker compose logs app"
echo "URL: http://localhost:8501"
