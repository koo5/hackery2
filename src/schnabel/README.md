# schnabel

An SDK for letting cooperating processes write into, read from, and subscribe to a shared quadstore-shaped runtime state. Working name; expect a rename if a better one turns up.

**Status:** design sketch. No code yet. The conversation that produced this lives in `docs/`.

## Reading order

- [`docs/vision.md`](docs/vision.md) — what we're trying to do and why
- [`docs/prior-art.md`](docs/prior-art.md) — what we learned from existing systems (brn, pyin, app.js, Tracker3, AllegroGraph, MQTT, …)
- [`docs/decisions.md`](docs/decisions.md) — choices made, alternatives considered, and why (append-only log)
- [`docs/design.md`](docs/design.md) — the current proposed API + connection-descriptor shape
- [`docs/roadmap.md`](docs/roadmap.md) — staged plan, phase 0 → phase 5

## Where this came from

The first concrete users are `bfg` (btrfsgit) and `backup.py` in hackery2. The original problem: backup runs produce one concatenated log with no per-invocation framing, the parent snapshot bfg picks is never surfaced, and there's no byte accounting. Those three asks turned into "let's build the realtime, RDF-native, audit-log-as-runtime-state thing we've been talking about for years."

If this proves useful, it will be promoted out of hackery2 into its own repo.

## Name

German *Schnabel* = beak. The Roman *rostrum* (speaker's platform) was decorated with bronze ship-beaks (*rostra*) taken from defeated fleets — the platform itself an append-only physical record of past speech-acts. *Halt den Schnabel!* means "shut your beak," so the name is at once a speaking-organ, a platform for oratory, and (since processes here are finally free to speak append-only) a small joke at the expense of the silent walled garden it replaces.
