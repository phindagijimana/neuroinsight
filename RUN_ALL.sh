#!/usr/bin/env bash
set -euo pipefail

# Unified launcher: start/stop frontend (Vite), backend (FastAPI), Celery worker,
# Redis, and MinIO. Designed for local or HPC (OOD) usage.
#
# Usage:
#   ./RUN_ALL.sh                # start everything
#   ./RUN_ALL.sh --restart      # stop then start everything
#   ./RUN_ALL.sh --stop         # stop everything and exit
#   ./RUN_ALL.sh --gpu          # same as start; detects GPUs and logs info
#
# Notes:
# - Ports default to: Vite 56052, Backend 8000, Redis 6379, MinIO 9000
# - Vite proxies /api/* -> http://127.0.0.1:8000/* so the app is reachable on 56052 only

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$LOG_DIR"

export PYTHONPATH="$ROOT_DIR"
export CORS_ORIGINS="${CORS_ORIGINS:-http://localhost:56052}"
export REDIS_HOST="${REDIS_HOST:-127.0.0.1}"
export REDIS_PORT="${REDIS_PORT:-6379}"
export MINIO_ENDPOINT="${MINIO_ENDPOINT:-127.0.0.1:9000}"
export MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:-minioadmin}"
export MINIO_SECRET_KEY="${MINIO_SECRET_KEY:-minioadmin}"
export MINIO_BUCKET="${MINIO_BUCKET:-neuroinsight-data}"

ACTION="start"
GPU_HINT="false"
for arg in "$@"; do
  case "$arg" in
    --restart) ACTION="restart" ;;
    --stop) ACTION="stop" ;;
    --gpu) GPU_HINT="true" ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done

echo "[RUN_ALL] Working dir: $ROOT_DIR"
echo "[RUN_ALL] Logs: $LOG_DIR"

stop_all() {
  echo "[RUN_ALL] Stopping services ..."
  pkill -f "uvicorn backend.main:app" >/dev/null 2>&1 || true
  pkill -f "celery .*workers.celery_app" >/dev/null 2>&1 || true
  pkill -f "redis-server" >/dev/null 2>&1 || true
  pkill -f "minio" >/dev/null 2>&1 || true
  pkill -f "npx --yes vite" >/dev/null 2>&1 || true
  pkill -f "vite" >/dev/null 2>&1 || true
  pkill -f "node" >/dev/null 2>&1 || true
  sleep 2
}

start_redis() {
  if ss -ltn | grep -q ":${REDIS_PORT}"; then
    echo "[RUN_ALL] Redis already on :${REDIS_PORT}"
    return 0
  fi
  if command -v redis-server >/dev/null 2>&1; then
    echo "[RUN_ALL] Starting redis-server ..."
    redis-server --daemonize yes >/dev/null 2>&1 || true
    sleep 1
  else
    echo "[RUN_ALL] Starting Redis via Apptainer ..."
    nohup apptainer run docker://redis:7-alpine > "$LOG_DIR/redis.run.log" 2>&1 &
    sleep 2
  fi
}

start_minio() {
  if ss -ltn | grep -q ":9000"; then
    echo "[RUN_ALL] MinIO already on :9000"
    return 0
  fi
  echo "[RUN_ALL] Starting MinIO via Apptainer on :9000 ..."
  export MINIO_ROOT_USER="$MINIO_ACCESS_KEY"
  export MINIO_ROOT_PASSWORD="$MINIO_SECRET_KEY"
  MINIO_DATA_DIR="$ROOT_DIR/data/minio"
  mkdir -p "$MINIO_DATA_DIR"
  nohup apptainer run docker://minio/minio:latest server "$MINIO_DATA_DIR" --address ":9000" --console-address ":9001" \
    > "$LOG_DIR/minio.run.log" 2>&1 &
  sleep 3
}

start_backend() {
  echo "[RUN_ALL] Starting backend (uvicorn :8000) ..."
  pkill -f "uvicorn backend.main:app" >/dev/null 2>&1 || true
  nohup env PYTHONPATH="$PYTHONPATH" CORS_ORIGINS="$CORS_ORIGINS" \
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --log-level info \
    > "$LOG_DIR/backend.out" 2>&1 &
}

start_worker() {
  echo "[RUN_ALL] Starting Celery worker ..."
  pkill -f "celery .*workers.celery_app" >/dev/null 2>&1 || true
  if command -v celery >/dev/null 2>&1; then
    GPU_COUNT=$( (command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi --query-gpu=name --format=csv,noheader | wc -l) || echo 0 )
    echo "[RUN_ALL] Detected GPUs: ${GPU_COUNT}"
    nohup env PYTHONPATH="$PYTHONPATH" REDIS_HOST="$REDIS_HOST" REDIS_PORT="$REDIS_PORT" \
      celery -A workers.celery_app:celery_app worker -l info \
      > "$LOG_DIR/worker.out" 2>&1 &
  else
    echo "[RUN_ALL] ERROR: celery not found in PATH. Install with: pip install celery"
  fi
}

start_frontend() {
  echo "[RUN_ALL] Starting frontend (Vite :56052) ..."
  if ! ss -ltn | grep -q ":56052"; then
    (
      cd "$ROOT_DIR/frontend"
      nohup npx --yes vite --host 0.0.0.0 --port 56052 > "$LOG_DIR/vite-56052.out" 2>&1 &
    )
  else
    echo "[RUN_ALL] Vite already on :56052"
  fi
}

health_checks() {
  echo "[RUN_ALL] Waiting for backend health ..."
  for i in {1..40}; do
    if curl -sf http://127.0.0.1:8000/health >/dev/null; then break; fi; sleep 0.5; done
  echo -n "[RUN_ALL] Backend /health: "; curl -sI http://127.0.0.1:8000/health | head -n1 || true
  echo -n "[RUN_ALL] Proxy /api/health: "; curl -sI http://127.0.0.1:56052/api/health | head -n1 || true
  echo -n "[RUN_ALL] Proxy /api/jobs:   "; curl -sI http://127.0.0.1:56052/api/jobs/ | head -n1 || true
  echo -n "[RUN_ALL] MinIO live:        "; curl -sI http://127.0.0.1:9000/minio/health/live | head -n1 || true
}

case "$ACTION" in
  stop)
    stop_all
    echo "[RUN_ALL] Stopped."
    exit 0
    ;;
  restart)
    stop_all
    ;;
esac

if [ "$GPU_HINT" = "true" ]; then
  if command -v nvidia-smi >/dev/null 2>&1; then
    echo "[RUN_ALL] GPU mode requested and NVIDIA detected:"
    nvidia-smi || true
  else
    echo "[RUN_ALL] GPU mode requested but nvidia-smi not found; proceeding on CPU"
  fi
fi

echo "[RUN_ALL] Starting services ..."
start_redis
start_minio
start_backend
start_worker
start_frontend

sleep 2
health_checks

echo "[RUN_ALL] Ready. Open UI: http://localhost:56052/hippo_new_version.html"
echo "[RUN_ALL] Logs:"
echo "  Backend: $LOG_DIR/backend.out"
echo "  Worker:  $LOG_DIR/worker.out"
echo "  Frontend:$LOG_DIR/vite-56052.out"
echo "  Redis:   $LOG_DIR/redis.run.log (if apptainer)"
echo "  MinIO:   $LOG_DIR/minio.run.log (if apptainer)"





