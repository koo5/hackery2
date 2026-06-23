# freezer2 web

## Phase 0 (current): `spike.html`

A single-file Web Bluetooth client that connects to the C3 spike firmware, pulls the full synthetic
history, and graphs the **min/max band + mean** with uPlot. It speaks the real protocol
(`../docs/PROTOCOL.md`), so the decoder here is the seed of the Phase 1 PWA.

### Run it

Web Bluetooth needs a **secure context** — `https://` or `http://localhost`. `file://` won't work.
Serve locally and open in **Chrome/Edge on Android** (or desktop Chrome for a quick test):

```fish
cd ~/hackery2/data/iot/freezer2/web
python3 -m http.server 8000
# then browse to http://localhost:8000/spike.html
```

For an Android phone, reach your laptop over the LAN with HTTPS (Web Bluetooth requires it for
non-localhost). Easiest options: `npx http-server -S` with a self-signed cert, or tunnel via
`cloudflared`/`ngrok`. (Same-laptop desktop Chrome over `localhost` is the fastest smoke test.)

### What to watch

- The log prints **transfer + decode time** for the full dataset — that's the number Phase 0 exists
  to validate (is BLE bulk history "fast enough"? You said snappiness can be optimized later).
- The chart should show the daily swing, the daily defrost bumps, and one obvious warming excursion.

### Notes

- uPlot is loaded from a CDN here for convenience (you're online while developing). The real PWA will
  vendor it + add a service worker, manifest, and PouchDB.

## Phase 1+ (next)

Turn this into the installable PWA: PouchDB store with deterministic `<deviceId>:<epoch>` ids,
`READ_LOG SINCE <max local epoch>` delta sync, service worker + manifest, then CouchDB replication.
