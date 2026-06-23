// freezer2 BLE protocol — shared constants. Mirror of docs/PROTOCOL.md (PROTO_VER 1).
// Keep this file and the PWA's decoder in lockstep.
#pragma once
#include <stdint.h>

#define FZ2_PROTO_VER   1
#define FZ2_DEVICE_NAME "freezer2-spike"

// 128-bit UUIDs — PLACEHOLDERS sharing one base. Regenerate with `uuidgen` before production,
// but firmware and PWA must always use the same values.
#define FZ2_SVC_UUID  "f2c70001-9a1f-4b1e-8a2d-1c0ffeec0001"
#define FZ2_CMD_UUID  "f2c70002-9a1f-4b1e-8a2d-1c0ffeec0001"
#define FZ2_LIVE_UUID "f2c70003-9a1f-4b1e-8a2d-1c0ffeec0001"

// CMD opcodes
enum {
	CMD_HELLO      = 0x00,
	CMD_GET_TIME   = 0x23,
	CMD_SET_TIME   = 0x24,
	CMD_LIVE       = 0x33,
	CMD_READ_LOG   = 0x35,
	CMD_CLEAR_LOG  = 0x36,
	CMD_GET_CONFIG = 0x40,
	CMD_SET_CONFIG = 0x41,
	CMD_MTU        = 0x71,
};

// READ_LOG request modes
enum { LOG_SINCE = 0x01, LOG_LASTN = 0x02, LOG_ALL = 0x03 };
// READ_LOG response status byte
enum { LOG_DONE = 0x00, LOG_CHUNK = 0x01, LOG_ERR = 0xFF };
// CLEAR_LOG guard magic
#define FZ2_CLEAR_MAGIC 0xC1EA2106u

// services capability bitmap (HELLO)
#define FZ2_SVC_HISTORY (1u << 0)
#define FZ2_SVC_LIVE    (1u << 1)
#define FZ2_SVC_ALARMS  (1u << 2)
#define FZ2_SVC_PIN     (1u << 3)
#define FZ2_SVC_OTA     (1u << 4)

// record flags
#define FZ2_FLAG_ALARM_HIGH  (1u << 0)
#define FZ2_FLAG_ALARM_LOW   (1u << 1)
#define FZ2_FLAG_FAULT       (1u << 2)
#define FZ2_FLAG_TIME_UNCERT (1u << 3)
#define FZ2_FLAG_BOOT        (1u << 4)
#define FZ2_FLAG_EXCURSION   (1u << 5)

// 12-byte log record — identical layout in flash and on the wire (little-endian).
typedef struct __attribute__((packed)) {
	uint32_t epoch;   // UTC seconds at window end
	int16_t  mean_c;  // window mean x0.01 C  (0x7FFF = fault)
	int16_t  min_c;   // window min  x0.01 C
	int16_t  max_c;   // window max  x0.01 C  (freezer-critical)
	uint8_t  flags;
	uint8_t  rsv;
} fz2_rec_t;
