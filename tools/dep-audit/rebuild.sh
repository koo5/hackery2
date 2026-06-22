#!/usr/bin/env bash
# Rebuild the cooled-off pip-audit env identically. See README.md.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PIP_AUDIT_VERSION="2.10.0"
EXCLUDE_NEWER="2026-02-27"   # whole-tree cooldown cutoff

rm -rf "$HERE/.venv"
uv venv --python /usr/bin/python3 "$HERE/.venv"
VIRTUAL_ENV="$HERE/.venv" uv pip install \
    --exclude-newer "$EXCLUDE_NEWER" \
    "pip-audit==$PIP_AUDIT_VERSION"

"$HERE/.venv/bin/pip-audit" --version
