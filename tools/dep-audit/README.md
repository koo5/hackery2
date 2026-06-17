# dep-audit

Reusable, cooled-off [`pip-audit`](https://github.com/pypa/pip-audit) environment
for auditing Python project dependencies against the PyPI Advisory DB / OSV.

## Why this exists

`uvx pip-audit` (or any floating install) re-fetches packages from PyPI on every
run, re-exposing you to whatever was published in the last few hours — the usual
supply-chain attack vector (hijacked maintainer, malicious point release). This
env is built **once** with a cooldown applied to the **whole dependency tree**,
then reused.

## Pinned setup (reproducible)

- Tool: `pip-audit==2.10.0`
- Cooldown cutoff: `--exclude-newer 2026-02-27` (~90 days before build on 2026-05-27)
  — ignores every distribution (incl. transitive deps) uploaded after this date.
- Base Python: system `/usr/bin/python3` (3.12.x — needs working `ensurepip`/`venv`,
  which uv-managed Pythons here lack).
- Resolver/installer: `uv` (verifies index hashes by default).

Rebuild identically with `./rebuild.sh`.

## Usage

    # Audit a pinned requirements file (builds a temp resolver venv):
    ~/hackery2/tools/dep-audit/.venv/bin/pip-audit -r path/to/requirements.txt

    # Audit an already-installed environment (no resolution):
    ~/hackery2/tools/dep-audit/.venv/bin/pip-audit --path path/to/site-packages

Or via the fish alias: `dep-audit ...`

`.venv/` is gitignored; only this README and rebuild.sh are tracked.
