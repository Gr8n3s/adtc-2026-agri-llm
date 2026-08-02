#!/usr/bin/env bash
# Starts llama-server, waits for the model to load, then opens the chat CLI.
# Needs: model weights downloaded already (download_model.sh), llama-server on PATH.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL_PATH="$HERE/model/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
PORT=8090

if [[ ! -f "$MODEL_PATH" ]]; then
  echo "model not found at $MODEL_PATH — run download_model.sh first" >&2
  exit 1
fi

if ! command -v llama-server > /dev/null 2>&1; then
  echo "error: llama-server not found on PATH" >&2
  exit 1
fi

echo "starting llama-server (this can take ~10-60s to load the model)…"
setsid nohup llama-server -m "$MODEL_PATH" --ctx-size 4096 --parallel 1 --port "$PORT" \
  > "$HERE/app/server.log" 2>&1 < /dev/null &
disown

for _ in $(seq 1 60); do
  if grep -q "listening on" "$HERE/app/server.log" 2>/dev/null; then
    break
  fi
  sleep 2
done

if ! grep -q "listening on" "$HERE/app/server.log" 2>/dev/null; then
  echo "server did not come up in time — check app/server.log" >&2
  exit 1
fi

echo "server ready."
python3 "$HERE/app/chat.py"
