#!/bin/sh
set -eu
app=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
if [ -x "$app/.venv/bin/python" ]; then
    exec "$app/.venv/bin/python" "$app/main.py" "$@"
fi
if [ -x "$app/../.venv/bin/python" ]; then
    exec "$app/../.venv/bin/python" "$app/main.py" "$@"
fi
exec python3 "$app/main.py" "$@"
