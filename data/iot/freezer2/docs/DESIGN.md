# freezer2 — Design

> Status: design. This is the reasoning + the plan. The wire contract lives in `PROTOCOL.md`;
> the reference study lives in `PVVX-NOTES.md`.

## 1. Requirements (locked)

These were decided explicitly and drive everything below:

1. **No internet at the ESP.** It must log standalone, for months, surviving power cuts.
2. **Phone keeps its own internet** while reading the freezer → the device must be a BLE peer the
   phone reaches *without* joining a Wi-Fi AP. (Rules out the SoftAP+HTTP approach.)
3. **Android-only / controlled phones** → **Web Bluetooth** is available (it does not exist on iOS).
4. **Custom firmware** is acceptable (we leave ESPHome).
5. **Don't depend on the phone being online next to the freezer.** Sync to the server happens
   *later*, through an on-phone buffer → **PouchDB (IndexedDB) → CouchDB**.
6. Cadence **1 record / 10 min**, **mains-powered** (no deep-sleep gymnastics).

### Why not the alternatives (so we don't relitigate)

- **ESPHome / Wi-Fi web UI** (`../eli-freezer/`): great, but forces the phone onto the ESP's AP,
  killing its internet (violates #2), and ESP32-**S2** has no BLE anyway.
- **Wi-Fi SoftAP + cached PWA over HTTP**: works on all phones incl. iOS, but same AP-switch problem (#2).
- **BLE + native/Capacitor app**: needed only if iOS mattered (#3 says it doesn't), so we skip the
  app-store friction and ship a pure installable PWA.

## 2. Hardware

| Part | Role | Pins / bus | Notes |
|---|---|---|---|
| **ESP32-C3 SuperMini** | MCU + BLE 5 | — | RISC-V, native USB, cheap. Mains-powered. |
| **MAX31865 + PT100** | precision temp | SPI (MISO/MOSI/CLK + CS) | Ported from `../eli-freezer/main.yaml`. |
| **DS3231** | RTC | I²C (SDA/SCL) | Battery-backed UTC. **Mandatory** (no NTP). Exposes an oscillator-stop flag we use for time integrity. |
| microSD (optional) | bulk store | SPI (shared, separate CS) | Only if we ever want removable media; internal flash is plenty. |

Mains power simplifies the firmware a lot vs pvvx (which is a coin-cell device): we stay
**always-connectable** and don't need advertise-then-deep-sleep duty cycling.

## 3. Firmware

### 3.1 Framework

**Recommendation: Arduino-ESP32 core + NimBLE-Arduino + Adafruit_MAX31865 + RTClib**, while using
the ESP-IDF `esp_partition` API directly for the raw ring buffer.

Rationale: mature, battle-tested sensor/RTC libraries (saves time on the boring parts), NimBLE is the
small/fast BLE stack, and `esp_partition` is reachable from the Arduino core anyway — so we still get
raw, sector-level flash control for the log. PlatformIO for the build.

*Alternative:* pure **ESP-IDF + NimBLE**. Cleaner partitioning story and no Arduino layer, but we'd
reimplement the MAX31865/DS3231 drivers (both are simple). Pick this if we want zero Arduino.

### 3.2 Storage — log-structured ring buffer on a raw flash partition

Cloned from pvvx (`PVVX-NOTES.md` §Storage), adapted to ESP-IDF flash:

- A dedicated **`logdata`** partition (raw, `type=data`, custom subtype) in `partitions.csv`.
- Treated as an array of **4096-byte sectors**, each:
  ```
  sector_head { u32 magic = 0xF2C0DE01 ; u16 flg ; u16 rsv }   // 8 bytes, aligned
      flg == 0xFFFF : sector open (currently being appended to)
      flg == 0x0000 : sector closed (full)
  record[...]                                                    // 8 bytes each, see below
  ```
- **Record** (`rec_t`, 12 bytes) — stores the **mean + min/max envelope** of each window:
  ```
  u32 epoch_utc      // seconds, device's DS3231 UTC at window end
  s16 mean_c         // window mean   ×0.01 °C  (e.g. -1850 = -18.50 °C)
  s16 min_c          // window minimum ×0.01 °C  (coldest sub-sample)
  s16 max_c          // window maximum ×0.01 °C  (warmest sub-sample — the dangerous one)
  u8  flags          // see below
  u8  rsv            // 0, reserved / future CRC
  ```
  Any field = `0x7FFF` means sensor fault for that window. `(4096 − 8) / 12 = 340` records per sector.
- **flags bits:** `bit0 alarm_high`, `bit1 alarm_low`, `bit2 sensor_fault`, `bit3 time_uncertain`
  (RTC oscillator-stop was seen → timestamp suspect until re-synced), `bit4 boot_marker`
  (first record after a reboot → marks a possible gap), `bit5 excursion_in_window` (set when `min_c`/
  `max_c` crossed a threshold — a fast "this window breached" marker derived from the envelope).
- **Append:** write the record at the current offset (flash erased = `0xFF`; a write only clears
  bits, so appending into erased space needs no erase). When the sector is full → write `flg=0` to
  close it, erase + init the next sector, wrapping `end → start`. Old data is overwritten sector-by-
  sector as the ring advances. **No filesystem, power-loss-safe by construction.**
- **Boot recovery:** scan sectors for the one with a valid magic and `flg==0xFFFF`; within it, the
  first `0xFFFFFFFF` epoch slot is the write head. (Exactly pvvx's `memo_init`.)

### 3.3 Partition layout & capacity (dual-OTA, 12-byte records, 1 rec / 10 min = 144 rec/day)

We keep **dual-OTA** (two app slots for safe firmware updates), which leaves the rest of a 4 MB C3
for `logdata`. With 1.5 MB app slots (headroom for an Arduino+NimBLE build that may grow):

```csv
# partitions.csv  (4 MB flash, dual-OTA + logdata)
# Name,    Type, SubType, Offset,    Size
nvs,       data, nvs,     0x9000,    0x6000     # 24K  config/thresholds/deviceId
otadata,   data, ota,     0xf000,    0x2000     # 8K
phy_init,  data, phy,     0x11000,   0x1000     # 4K
ota_0,     app,  ota_0,   0x20000,   0x180000   # 1.5M
ota_1,     app,  ota_1,   0x1a0000,  0x180000   # 1.5M
logdata,   data, 0x40,    0x320000,  0xE0000    # 896K  raw ring buffer (custom subtype)
```

| `logdata` size | app slots | sectors | records | retention @144/day |
|---|---|---|---|---|
| **896 KB** (default above) | 2 × 1.5 MB | 224 | ~76k | **~1.4 years** |
| 1.4 MB | 2 × 1.25 MB | 352 | ~120k | ~2.3 years |

So even with dual-OTA and the wider 12-byte record we get 1.4–2.3 years. If the firmware lands under
~1 MB we shrink the app slots to 1.25 MB and grow `logdata` accordingly — decide once we can measure
the binary. Flash wear is a non-issue: at ~340 records/sector and 144/day a sector is erased ~once
every 2.4 days → the ring spreads erases evenly and the ~100k-erase endurance lasts effectively
forever.

### 3.4 Sampling, averaging, excursions

- Sample the MAX31865 every **10 s** (as in the current eli-freezer config). 60 sub-samples / window.
- Aggregate the 10-min window into one record storing **mean + min + max** of the sub-samples
  (`rec_t`, §3.2). Because min/max come from the sub-samples, the 10-min record captures any transient
  excursion regardless of cadence — so we can keep the slow cadence and still never miss a spike.
  (This is the explicit trade chosen: **min/max fidelity > sample rate**.)
- For a freezer, **`max_c` is the safety-critical field** (warming = thawing); `min_c` is useful but
  secondary. The UI can draw a min..max band with a mean line — a rich, honest freezer chart.
- Set `excursion_in_window` (and the alarm flags) when min/max cross the configured thresholds.

### 3.5 Time integrity (the real gotcha with no internet)

- DS3231 holds UTC across power cuts (coin cell). Every record stamps the device's current UTC.
- On connect, the PWA reads the device clock (in the `HELLO` reply), compares to the phone clock, and
  if drift is large or the device flags `clock_uncertain`, the PWA issues `SET_TIME`.
- If the DS3231's **oscillator-stop flag** is set at boot (battery died / first power-up), the device
  marks subsequent records `time_uncertain` until a `SET_TIME` arrives. The UI shows those as suspect
  rather than silently trusting a wrong timestamp.
- `boot_marker` on the first post-reboot record lets the UI draw a possible gap.

### 3.6 Alarms (v1: detect + flag; actuation later)

- Configurable high/low thresholds, stored in NVS, settable over BLE (`SET_CONFIG`).
- v1: set record flags + report current alarm state in `HELLO`/live notifications.
- Later: drive a buzzer/LED (we already have buzzer modules — cf. `../viol-b18-voda-buzzer/`).

## 4. BLE protocol

Full contract in **`PROTOCOL.md`**. Summary: one custom 128-bit service, a **CMD** characteristic
(write+notify, commands in / framed responses + history stream out) and a **LIVE** characteristic
(notify, current temperature while connected). Current temperature is also broadcast in the
**advertisement** (BTHome-style) so a phone sees the live value instantly without connecting.

Sync is **delta-based**: the PWA knows the newest epoch it already holds for a device and asks
`READ_LOG since=<epoch>`; the device streams everything newer, many records per notification.

## 5. The phone PWA

### 5.1 Stack

- **Web Bluetooth** for transport (Chrome/Edge on Android + desktop).
- **PouchDB** for the local store (IndexedDB under the hood).
- **uPlot** for charts (tiny, handles 100k+ points).
- **Service worker + manifest** for install + full offline operation after first load.
- Plain TS/JS; no heavy framework needed (small app). Vite for the build.

### 5.2 Local data model (PouchDB)

One doc per record, **deterministic `_id`** so the same reading from any phone/session is the same
doc → idempotent writes, conflict-free replication:

```
_id   : "<deviceId>:<epoch_padded_hex>"   // e.g. "c3a1b2:000000006612ab90"
type  : "reading"
dev   : "<deviceId>"
t     : <epoch_utc>
mean  : <mean_c>      // ×0.01 °C
min   : <min_c>
max   : <max_c>
flags : <u8>
```

`deviceId` = a stable id the device returns in `HELLO` (its BLE MAC, or a UUID minted on first boot
and stored in NVS). Records are **immutable** (write-once) — we never update a reading, so there is
never a real document conflict.

A small per-device meta doc (`meta:<deviceId>`) caches name, thresholds, last-synced epoch, etc.

### 5.3 Sync flow (at the freezer, phone may be offline)

```
connect BLE
 → HELLO                         (learn deviceId, fw, clock, oldest/newest epoch, count, current temp)
 → if clock drift / uncertain: SET_TIME
 → since = max epoch in PouchDB for this device   (0 if none)
 → if since < device.oldest: mark a gap (ring overwrote data we never got)
 → READ_LOG since                (stream; bulkDocs into PouchDB as packets arrive)
 → disconnect
```

Everything here is local — no network needed. uPlot renders straight from PouchDB.

### 5.4 Server sync (later, whenever the phone has internet)

```
localPouch.sync(remoteCouch, { live: true, retry: true })   // or push-only
```

- Because `_id`s are deterministic and docs immutable, replication is **conflict-free** by design.
- **CouchDB setup needs:** CORS enabled (browser replication), per-user or per-device auth, and a DB
  layout — start with **one DB per device** (clean security + filtered sync) or a single shared DB
  with a `dev` field. Per-device DBs scale better for a fleet and let you hand one inspector access to
  only their freezers.
- This gives the **multi-freezer fleet view**, durable history beyond the ring buffer's window, and a
  base for CSV/PDF compliance export — all server-side, decoupled from the BLE path.

## 6. Security (not a v1 blocker, but plan for it)

BLE is open by default — anyone in range could read, set the clock, or **clear the log**. Plan:
- Leave **reads open** (history/live are not secret in a kitchen/lab).
- Gate **mutating** commands (`SET_TIME`, `SET_CONFIG`, `CLEAR_LOG`) behind a **PIN / BLE bonding**
  (pvvx has a pincode model to copy). Phase it in once the happy path works.

## 7. Roadmap / phasing

- **Phase 0 — vertical slice (de-risk the BLE+WebBT path).** C3 firmware that advertises the service,
  serves **canned/RAM** records over the CMD char (`HELLO` + `READ_LOG`), no sensor/flash yet. A
  one-file Web Bluetooth page that connects, pulls, and graphs with uPlot. Goal: prove bulk transfer
  feels OK on a real phone. (User isn't testing immediately, so this is scaffolding-ready.)
- **Phase 1 — real device.** Ring buffer on the `logdata` partition + MAX31865 + DS3231 + averaging.
  PWA: PouchDB store, delta sync, install/offline.
- **Phase 2 — server + fleet.** CouchDB + PouchDB replication, device picker / fleet view, alarm
  flags surfaced, CSV/PDF export.
- **Phase 3 — hardening.** PIN/bonding on mutating commands, buzzer/LED actuation, BLE OTA.

## 8. Decisions

**Resolved (2026-06-23):**
- ~~Partition layout~~ → **dual-OTA**, 1.5 MB app slots, ~896 KB `logdata` (~1.4 yr). §3.3.
- ~~Excursion fidelity~~ → **store mean + min + max** per window (12-byte record). §3.2, §3.4.
- ~~CouchDB hosting~~ → **deferred**; a box will be spun up later. Design stays Couch-ready (PouchDB
  works fully offline until then). Server/secret bits will live in `hackery_priv`.

**Still open:**
1. **Firmware framework:** Arduino-ESP32 + NimBLE-Arduino (recommended) vs pure ESP-IDF + NimBLE.
2. **App-slot vs log trade:** keep 1.5 MB slots (~1.4 yr) for safety, or commit to 1.25 MB slots
   (~2.3 yr) now? Best decided after measuring the actual firmware binary size.
