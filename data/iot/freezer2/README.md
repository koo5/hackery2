# freezer2 — offline cold-chain logger (ESP32-C3 + BLE + PWA)

A standalone temperature logger for a freezer in a place with **no Wi-Fi / no internet at the device**.
The ESP32 logs to its own flash forever. You walk up with an (Android) phone, the installed PWA
pulls new readings over **Bluetooth LE** into a local **PouchDB**, and *later* — whenever the phone
is online — PouchDB replicates to a **CouchDB** server. Nothing depends on the phone being online at
the moment it's next to the freezer.

This is a clean-slate, **custom-firmware** sibling of `../eli-freezer/` (which is the ESPHome/Wi-Fi
version). It exists because the requirements ruled ESPHome/Wi-Fi out — see `docs/DESIGN.md` §"Why not…".

## The shape of it

```
   ┌─────────────┐   BLE GATT    ┌──────────────┐   PouchDB↔CouchDB   ┌────────────┐
   │  ESP32-C3   │  (offline)    │  Phone PWA   │   replication       │  CouchDB   │
   │  PT100 +    │ ────────────▶ │  Web BT +    │  (when online,      │  (server,  │
   │  MAX31865   │  history sync │  PouchDB     │   later, anywhere)  │  durable)  │
   │  + DS3231   │               │  + uPlot     │ ──────────────────▶ │  aggregate │
   │  ring-buf   │               │  IndexedDB   │                     │            │
   │  in flash   │               └──────────────┘                     └────────────┘
   └─────────────┘
   source of truth        offline cache / sneakernet            durable multi-device store
```

The freezer's flash is the **source of truth**. Phones are **caches + sneakernet couriers**.
CouchDB is the **durable aggregate**. Records are write-once and globally addressed by
`(deviceId, epoch)`, so every copy is identical → replication is conflict-free.

## Status

Design done + **Phase 0 scaffolded** (not yet flashed/compiled): `firmware/` is a C3 spike serving a
synthetic history over the real BLE protocol, `web/spike.html` is a Web Bluetooth client that pulls
and graphs it. See `docs/DESIGN.md` §Roadmap for what's next.

## Docs

- [`docs/DESIGN.md`](docs/DESIGN.md) — full architecture, hardware, firmware, PWA, decisions, roadmap.
- [`docs/PROTOCOL.md`](docs/PROTOCOL.md) — the BLE GATT contract (the firmware ↔ PWA interface).
- [`docs/PVVX-NOTES.md`](docs/PVVX-NOTES.md) — what we learned from pvvx/ATC_MiThermometer and what we change.

## Hardware (target)

| Part | Role | Notes |
|---|---|---|
| ESP32-C3 SuperMini | MCU + BLE 5 | Mains-powered → always advertising + connectable. |
| MAX31865 + PT100 | precision temperature | SPI; ported from `../eli-freezer/`. |
| DS3231 | real-time clock | I²C; battery-backed. Mandatory — no NTP offline. |
| (optional) microSD | bulk/removable store | SPI, shares bus. Not the default; flash is enough. |
