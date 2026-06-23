# freezer2 firmware

ESP32-C3, Arduino + NimBLE, built with PlatformIO.

## Phase 0 (current): protocol spike

`src/main.cpp` is a **vertical slice** — no sensor, no flash ring buffer. It serves a *synthetic*
28-day freezer dataset (generated on the fly, zero RAM buffer) over the real BLE protocol from
`../docs/PROTOCOL.md`: `HELLO`, `READ_LOG` (ALL / LASTN / SINCE), `LIVE`, `SET_TIME`/`GET_TIME`.
The point is to prove the Web Bluetooth bulk-transfer path on a real C3 + Android phone before
building the real device.

## Build & flash

```fish
pip install platformio          # if needed
cd ~/hackery2/data/iot/freezer2/firmware
pio run                          # build (also reports the binary size vs the 1.5 MB OTA slot)
pio run -t upload                # flash over USB
pio device monitor               # serial log @115200
```

Then open `../web/spike.html` (see `../web/README.md`) on an Android Chrome device and connect.

## Notes / known caveats

- **Not yet compiled or run** — written against the NimBLE-Arduino 2.x API; expect to shake out a
  build wrinkle or two on first `pio run`.
- History is streamed from `loop()` (not the BLE write callback) and the cursor only advances when
  `notify()` reports the packet was queued, so it self-throttles to the tx buffers. Crude but fine
  for the spike; Phase 1 will pace per connection event like pvvx.
- Records-per-packet scales with the negotiated MTU (`onMTUChange`). Android Chrome usually lands
  ~247 → ~19 records/notification.
- UUIDs in `include/protocol.h` are placeholders shared with the PWA — regenerate before production.

## Phase 1 (next)

Add `adafruit/Adafruit_MAX31865` + `adafruit/RTClib` to `lib_deps`; implement the `logdata` ring
buffer via `esp_partition`; replace `gen_record()` with real sampling + 10-min mean/min/max windows.
