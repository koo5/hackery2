# freezer2 — BLE GATT protocol (firmware ↔ PWA contract)

> The single source of truth for the wire format. Both the C3 firmware and the PWA implement this.
> Modeled on pvvx/ATC_MiThermometer (see `PVVX-NOTES.md`) with two changes: **multi-record packets**
> and a **`since`-based delta read**. Version this doc; bump `PROTO_VER` on any breaking change.

`PROTO_VER = 1`

## 1. GATT layout

One custom primary service. **Generate real 128-bit UUIDs** (`uuidgen`) before coding — the values
below are placeholders sharing one base so they're easy to swap.

| Role | UUID (placeholder) | Properties |
|---|---|---|
| Service | `f2c70001-9a1f-4b1e-8a2d-1c0ffeec0001` | — |
| **CMD** characteristic | `f2c70002-9a1f-4b1e-8a2d-1c0ffeec0001` | Write (no rsp) + Notify (CCCD 0x2902) |
| **LIVE** characteristic | `f2c70003-9a1f-4b1e-8a2d-1c0ffeec0001` | Notify |

Also expose standard **Device Information** (0x180A) for fw/hw strings. Web Bluetooth must list the
service UUID in `filters` *and* `optionalServices` of `requestDevice`.

All multi-byte integers are **little-endian**.

## 2. Framing

- **Request** (PWA → device, write to CMD): `[cmd:u8][args…]`
- **Response** (device → PWA, notify on CMD): `[cmd:u8][status:u8][payload…]`
  - `status`: `0x00` ok, `0xFF` error/unsupported, command-specific otherwise.
- The CMD channel is **half-duplex per command**: send one command, consume its response(s) (a
  stream ends with an explicit terminator), then send the next.

Negotiate the **largest MTU** both sides allow (C3 supports 247; ask for it on connect). All "many
records per packet" sizing below assumes the negotiated `ATT_MTU − 3` payload budget.

## 3. Commands

| Code | Name | Direction / payload |
|---|---|---|
| `0x00` | `HELLO` | Req: `[0x00]`. Rsp: handshake struct (below). The first thing the PWA sends. |
| `0x23` | `GET_TIME` | Req: `[0x23]`. Rsp: `[0x23][0][epoch:u32][uncertain:u8]`. |
| `0x24` | `SET_TIME` | Req: `[0x24][epoch:u32]`. Rsp: `[0x24][0]`. Sets DS3231, clears `time_uncertain`. |
| `0x33` | `LIVE` | Req: `[0x33][on:u8]`. Enables/disables periodic LIVE-char notifications. Rsp: `[0x33][on]`. |
| `0x35` | `READ_LOG` | Req: see §4. Streams records on CMD. |
| `0x36` | `CLEAR_LOG` | Req: `[0x36][magic:u32=0xC1EA2106]`. Rsp: `[0x36][0]`. Magic guards against accident. |
| `0x40` | `GET_CONFIG` | Req: `[0x40]`. Rsp: config struct (interval, averaging, thresholds, name). |
| `0x41` | `SET_CONFIG` | Req: `[0x41][config…]`. Rsp: `[0x41][0]`. Persists to NVS. |
| `0x71` | `MTU` | Optional explicit MTU request, if not relying on auto-negotiation. |

### 3.1 `HELLO` response (handshake — everything the PWA needs to plan a sync)

```
[0x00][0x00]
  proto_ver   : u8     // = 1
  fw_ver      : u16    // BCD or monotonic
  hw_id       : u16    // board/sensor id
  services    : u32    // capability bitmap (history, live, alarms, pin, ota, …)
  device_id   : u8[6]  // stable id (BLE MAC, or NVS UUID) → PouchDB deviceId
  rec_size    : u8     // = 12 (lets the client stay forward-compatible)
  total_recs  : u32    // records currently stored in the ring
  oldest_epoch: u32    // epoch of the oldest record still in the ring
  newest_epoch: u32    // epoch of the newest record
  clock_epoch : u32    // device UTC now
  clock_uncert: u8     // 1 = RTC suspect (osc-stop seen, no SET_TIME since)
  cur_centi_c : s16    // current temperature ×0.01 °C (0x7FFF = fault)
  alarm_state : u8     // live alarm flags
```

The PWA uses `oldest_epoch` to detect ring overwrite gaps, `newest_epoch` to know if it's already
caught up, and `clock_*` to decide whether to `SET_TIME`.

## 4. `READ_LOG` — history streaming (delta sync)

### Request
```
[0x35][mode:u8][arg…]
  mode 0x01  SINCE : arg = [since_epoch:u32]   // stream all records with epoch > since_epoch
  mode 0x02  LASTN : arg = [count:u16]         // stream the newest `count` records (pvvx-style)
  mode 0x03  ALL   : no arg                     // stream everything in the ring
```
Normal sync uses **SINCE** with the max epoch already in PouchDB (0 ⇒ first full pull).

### Response stream (notifications on CMD)
Each data packet carries **as many whole records as fit** in the MTU (at MTU 247 the payload budget
is 244 B → 5-byte header + `⌊239/12⌋ = 19` records per packet):
```
[0x35][0x01][seq:u16][n:u8][ rec_t × n ]      // status 0x01 = "data chunk"
   rec_t = [epoch:u32][mean_c:s16][min_c:s16][max_c:s16][flags:u8][rsv:u8]   // 12 bytes, matches flash record
```
- `seq` increments per data packet (0,1,2,…) so the client can detect drops/order.
- Records are streamed **oldest→newest** within the requested range.

End of stream:
```
[0x35][0x00][total:u32]      // status 0x00 = "done", total = records actually sent
```
Error:
```
[0x35][0xFF][reason:u8]
```

### Client algorithm (PWA)
```
since = max(localPouch.epoch(deviceId), 0)
if (since < hello.oldest_epoch) markGap(deviceId, since, hello.oldest_epoch)   // ring overwrote
write CMD [0x35, 0x01, since]
loop notifications:
  if status == 0x01: decode n records, bulkDocs into PouchDB (deterministic _id ⇒ idempotent)
  if status == 0x00: done (optionally assert count)
  if status == 0xFF: surface error, retry/backoff
```

### Firmware side
Mirror pvvx's pacing: keep a `read_cursor`; on each BLE connection event where the tx queue has room,
emit the next packet (fill it with records up to the MTU), advance the cursor, until the range is
exhausted, then send the `done` terminator. Pulling from the flash ring uses the `get_memo`-style
backward/forward sector walk (see `PVVX-NOTES.md` §Storage).

## 5. LIVE characteristic

While `LIVE` is on, the device notifies on the LIVE char every measurement (or every few seconds):
```
[epoch:u32][centi_c:s16][flags:u8][alarm_state:u8]
```
Independent of the CMD channel so a live view doesn't interfere with a history pull.

## 6. Advertisement (no-connect quick read)

Broadcast the current temperature in the adv payload using the **BTHome v2** unencrypted format
(temperature object) plus the device name. A phone (or any BTHome-aware tool, e.g. Home Assistant)
then sees the live value **without connecting**. Connect only to pull history or change config.

## 7. Versioning & compatibility

- `proto_ver` in `HELLO` gates client behavior. Additive changes (new commands, new `services` bits)
  don't bump it; layout changes to existing structs do.
- `rec_size` in `HELLO` lets the client handle a future wider record (e.g. min/max) without breaking.
