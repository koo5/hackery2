# Reference study: pvvx/ATC_MiThermometer

What we learned from the proven open-source logger and what we keep vs change. This is the closest
existing thing to freezer2 (flash ring buffer → BLE → Web Bluetooth graph UI), just on Telink TLSR
chips instead of ESP32, so we steal the *design*, not the code.

- Local clone studied: `/home/koom/repos/pvvx/ATC_MiThermometer/0/ATC_MiThermometer` (commit `2cd23c5`).
- Upstream: https://github.com/pvvx/ATC_MiThermometer
- Live Web Bluetooth history UI (great UX reference): https://pvvx.github.io/ATC_MiThermometer/GraphMemo.html
- Python client (protocol reference): `python-interface/atc_mi_interface/`

## Storage — `src/logger.c`, `src/logger.h`

Log-structured ring buffer on raw NOR flash. **This is the model we copy.**

- Region split into 4 KB **sectors**. Each sector begins with
  `memo_head_t { u32 id = 0x55AAC0DE; u16 flg }` — `flg=0xFFFF` open, `flg=0` closed.
- Record `memo_blk_t` = `{ u32 time(UTC); s16 val1(temp ×0.01°C); u16 val2(humi); u16 val0(vbat) }`
  = **10 bytes**. `(4096−6)/10 ≈ 409` records/sector.
- **Append-only:** erased flash is `0xFF`; writes only clear bits, so a record drops into erased
  space with no erase. Sector full → `memo_sec_close()` writes `flg=0`, then erase + init the next
  sector; `test_next_memo_sec_addr()` wraps `end → start`. Old data overwritten a sector at a time.
- **Boot recovery** `memo_init()`: find the sector with valid `id` and `flg==0xFFFF`; the first
  `0xFFFFFFFF` word inside is the write head.
- **Read** `get_memo(bnum, p)`: returns record `bnum` counting **back from newest**, walking sectors
  backward. `clear_memo()` erases all data sectors.
- **Averaging:** `cfg.averaging_measurements` sums N samples and stores the mean as one record →
  step interval = sample interval × N. Capacities: ~20.8k records (512 KB region) or ~51.9k (1 MB).
- Time: per-record absolute UTC from `wrk.utc_time_sec` (sentinel `0xFFFFFFFE` when clock unknown).

**Our changes:** ESP-IDF `esp_partition_{read,write,erase_range}` instead of Telink `flash_*`;
**12-byte record storing mean+min+max** per window (no humi/vbat — pvvx stores only the mean, we keep
the excursion envelope; `max_c` is the freezer-critical field); magic `0xF2C0DE01`; explicit
`time_uncertain`/`boot_marker` flags instead of a single time sentinel; same sector-ring mechanics.

## Protocol — `src/cmd_parser.{c,h}`, `src/app_att.c`, `src/ble.c`

- **One** custom service `0x1F10`, **one** RxTx characteristic `0x1F1F` (write + notify, CCCD 0x2902).
  Commands in / responses out on the same characteristic. (Plus Device Info 0x180A, Battery 0x180F,
  Telink OTA service.)
- Frame: request `[cmd][args]`, response `[cmd][status/data]`.
- Relevant commands (`CMD_ID_*` enum):
  - `0x00 DEV_ID` → `dev_id_t { pid, revision, hw_version, sw_version, dev_spec_data, u32 services }`
    — handshake with a **services bitmap** (ota, pincode, bindkey, history, screen, ths, …).
  - `0x23 UTC_TIME` → get/set device clock.
  - `0x33 MEASURE` → start/stop live measurement notifications while connected.
  - `0x35 LOGGER` → read history. Client writes `[0x35][cnt:u16]([start:u16])`; device streams.
  - `0x36 CLRLOG` → erase memory.
  - `0x71 MTU` → request MTU exchange (23..255).
- **History streaming** (`ble.c:send_memo_blk`): **one record per notification**,
  `[0x35][seq:u16][memo_blk_t(10B)]` = 13 bytes, seq = 1-based index; terminator `[0x35][0][0]`.
  Paced by the connection-event loop (`app.c`: `else if (rd_memo.cnt) send_memo_blk();`) so it streams
  one block per opportunity without blocking.

**Our changes:** our own 128-bit UUIDs (16-bit `0x1F1x` are not valid custom UUIDs and are awkward for
Web Bluetooth filters); **pack many records per notification** (full MTU, not one) for throughput;
add a **`SINCE epoch`** read mode for delta sync (pvvx only has count/last-N); split **live** onto its
own characteristic. Keep: single-service simplicity, opcode framing, services-bitmap handshake,
clock-sync command, seq-numbered stream with explicit terminator, queue-paced sending.

## UX reference

`GraphMemo.html` / `GraphAtc*.html` are the "installed-once web page connects over Web Bluetooth and
graphs the device's stored history" experience — exactly our PWA, minus PouchDB/CouchDB. Worth
opening the page source for client-side Web Bluetooth patterns (request, MTU, notification handling).
