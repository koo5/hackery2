// freezer2 — Phase 0 vertical slice.
//
// Goal: prove the BLE + Web Bluetooth bulk-history path on a real ESP32-C3 and an Android phone.
// NO sensor, NO flash ring buffer yet — history is a *synthetic* dataset generated on the fly, so
// we can stream tens of thousands of records without any RAM buffer. It implements the real
// HELLO / READ_LOG / LIVE / SET_TIME protocol from docs/PROTOCOL.md, so the PWA decoder we write
// against it is the same one Phase 1 will use.
//
// Framework: Arduino-ESP32 + NimBLE-Arduino 2.x.

#include <Arduino.h>
#include <NimBLEDevice.h>
#include <math.h>
#include "esp_mac.h"
#include "protocol.h"

// ---------------------------------------------------------------- synthetic dataset
#define SPIKE_BASE_EPOCH 1750000000UL   // ~2025-06-15, arbitrary (no RTC in Phase 0)
#define SPIKE_STEP       600u           // 10 min between records
#define SPIKE_COUNT      4032u          // 28 days @ 144/day
#define THRESH_HIGH_C    (-1500)        // -15.00 C: above this = excursion/alarm

static inline uint32_t gen_epoch(uint32_t i) { return SPIKE_BASE_EPOCH + i * SPIKE_STEP; }

// Deterministic fake freezer curve: ~-18 C with a daily ±0.5 C swing, a once-a-day defrost bump,
// and one multi-record "door left open" warming excursion a third of the way through.
static fz2_rec_t gen_record(uint32_t i) {
	fz2_rec_t r;
	r.epoch = gen_epoch(i);
	uint32_t slot = i % 144;                       // sample index within the day
	float day = (float)slot / 144.0f;
	int mean = -1800 + (int)lroundf(50.0f * sinf(2.0f * (float)M_PI * day)); // ±0.5 C daily
	if (slot == 72 || slot == 73) mean += 300;     // daily defrost bump
	uint32_t exc = SPIKE_COUNT / 3;
	if (i >= exc && i <= exc + 3) mean += 1000;    // door-open excursion → warms to ~-8 C
	int spread_lo = 30 + (int)(i % 7) * 5;
	int spread_hi = 30 + (int)(i % 5) * 7;
	r.mean_c = (int16_t)mean;
	r.min_c  = (int16_t)(mean - spread_lo);
	r.max_c  = (int16_t)(mean + spread_hi);
	r.flags  = (i == 0) ? FZ2_FLAG_BOOT : 0;
	if (r.max_c > THRESH_HIGH_C) r.flags |= (FZ2_FLAG_EXCURSION | FZ2_FLAG_ALARM_HIGH);
	r.rsv = 0;
	return r;
}

// ---------------------------------------------------------------- BLE state
static NimBLECharacteristic *g_cmd  = nullptr;
static NimBLECharacteristic *g_live = nullptr;

static volatile bool     g_connected = false;
static volatile uint16_t g_mtu       = 23;       // updated on MTU exchange

// READ_LOG streaming cursor (advanced from loop(), never from the BLE callback)
static volatile bool g_streaming = false;
static uint32_t      g_cursor    = 0;            // next record index to send
static uint32_t      g_end       = 0;            // exclusive end index
static uint32_t      g_sent      = 0;            // records sent this stream (for the terminator)
static uint16_t      g_seq       = 0;

static volatile bool g_live_on   = false;
static uint32_t      g_live_last = 0;

static uint32_t g_clock        = 0;              // device UTC (set via SET_TIME); 0 = unset
static bool     g_clock_uncert = true;

// ---------------------------------------------------------------- helpers
static void notify_cmd(const uint8_t *buf, size_t len) {
	g_cmd->setValue(buf, len);
	g_cmd->notify();
}

static void send_hello() {
	uint8_t b[48];
	size_t o = 0;
	b[o++] = CMD_HELLO;
	b[o++] = 0x00;                                            // status ok
	b[o++] = FZ2_PROTO_VER;
	uint16_t fw = 0x0001; memcpy(b + o, &fw, 2); o += 2;     // fw_ver
	uint16_t hw = 0x0C03; memcpy(b + o, &hw, 2); o += 2;     // hw_id ("C3")
	uint32_t svc = FZ2_SVC_HISTORY | FZ2_SVC_LIVE | FZ2_SVC_ALARMS;
	memcpy(b + o, &svc, 4); o += 4;
	uint8_t mac[6]; esp_read_mac(mac, ESP_MAC_BT);           // stable device_id
	memcpy(b + o, mac, 6); o += 6;
	b[o++] = (uint8_t)sizeof(fz2_rec_t);                     // rec_size = 12
	uint32_t total  = SPIKE_COUNT;             memcpy(b + o, &total,  4); o += 4;
	uint32_t oldest = gen_epoch(0);            memcpy(b + o, &oldest, 4); o += 4;
	uint32_t newest = gen_epoch(SPIKE_COUNT-1);memcpy(b + o, &newest, 4); o += 4;
	uint32_t clk = g_clock ? g_clock : newest; memcpy(b + o, &clk,    4); o += 4;
	b[o++] = g_clock_uncert ? 1 : 0;
	int16_t cur = gen_record(SPIKE_COUNT - 1).mean_c; memcpy(b + o, &cur, 2); o += 2;
	b[o++] = 0;                                              // alarm_state
	notify_cmd(b, o);
}

static void start_read_log(const uint8_t *p, size_t n) {
	uint8_t mode = (n >= 2) ? p[1] : LOG_ALL;
	uint32_t first = 0, end = SPIKE_COUNT;
	if (mode == LOG_LASTN && n >= 4) {
		uint16_t cnt = p[2] | (p[3] << 8);
		first = (cnt >= SPIKE_COUNT) ? 0 : SPIKE_COUNT - cnt;
	} else if (mode == LOG_SINCE && n >= 6) {
		uint32_t since; memcpy(&since, p + 2, 4);
		if (since < SPIKE_BASE_EPOCH) first = 0;
		else {
			uint32_t idx = (since - SPIKE_BASE_EPOCH) / SPIKE_STEP + 1; // first epoch > since
			first = (idx > SPIKE_COUNT) ? SPIKE_COUNT : idx;
		}
	} // else LOG_ALL → whole range
	g_cursor = first; g_end = end; g_sent = 0; g_seq = 0; g_streaming = true;
}

// pump one history packet from loop(); commit the cursor only if the notify was queued
static void pump_stream() {
	if (g_cursor >= g_end) {                                  // terminator
		uint8_t t[6];
		t[0] = CMD_READ_LOG; t[1] = LOG_DONE;
		memcpy(t + 2, &g_sent, 4);
		g_cmd->setValue(t, 6);
		if (g_cmd->notify()) g_streaming = false;
		return;
	}
	uint16_t budget  = (g_mtu > 23 ? g_mtu : 23) - 3;        // ATT payload
	uint16_t maxrecs = (budget > 5) ? (budget - 5) / sizeof(fz2_rec_t) : 1;
	if (maxrecs < 1)  maxrecs = 1;
	if (maxrecs > 40) maxrecs = 40;                          // cap to keep buf small

	uint8_t buf[5 + 40 * sizeof(fz2_rec_t)];
	buf[0] = CMD_READ_LOG; buf[1] = LOG_CHUNK;
	buf[2] = g_seq & 0xFF; buf[3] = (g_seq >> 8) & 0xFF;
	uint32_t c = g_cursor; uint8_t cnt = 0; size_t o = 5;
	while (cnt < maxrecs && c < g_end) {
		fz2_rec_t r = gen_record(c);
		memcpy(buf + o, &r, sizeof(r)); o += sizeof(r);
		c++; cnt++;
	}
	buf[4] = cnt;
	g_cmd->setValue(buf, o);
	if (g_cmd->notify()) { g_cursor = c; g_sent += cnt; g_seq++; } // else retry next loop
}

static void send_live() {
	fz2_rec_t r = gen_record(SPIKE_COUNT - 1);
	uint8_t b[8]; size_t o = 0;
	uint32_t e = gen_epoch(SPIKE_COUNT - 1); memcpy(b + o, &e, 4); o += 4;
	memcpy(b + o, &r.mean_c, 2); o += 2;
	b[o++] = r.flags;
	b[o++] = 0;                                              // alarm_state
	g_live->setValue(b, o);
	g_live->notify();
}

// ---------------------------------------------------------------- callbacks
class CmdCallbacks : public NimBLECharacteristicCallbacks {
	void onWrite(NimBLECharacteristic *c, NimBLEConnInfo &info) override {
		NimBLEAttValue v = c->getValue();
		const uint8_t *p = v.data();
		size_t n = v.length();
		if (n == 0) return;
		switch (p[0]) {
		case CMD_HELLO:
			send_hello();
			break;
		case CMD_READ_LOG:
			start_read_log(p, n);                            // streamed from loop()
			break;
		case CMD_GET_TIME: {
			uint8_t b[7]; b[0] = CMD_GET_TIME; b[1] = 0;
			memcpy(b + 2, &g_clock, 4); b[6] = g_clock_uncert ? 1 : 0;
			notify_cmd(b, 7);
			break;
		}
		case CMD_SET_TIME:
			if (n >= 5) { memcpy(&g_clock, p + 1, 4); g_clock_uncert = false; }
			{ uint8_t b[2] = {CMD_SET_TIME, 0}; notify_cmd(b, 2); }
			break;
		case CMD_LIVE:
			g_live_on = (n >= 2) ? (p[1] != 0) : true;
			{ uint8_t b[2] = {CMD_LIVE, (uint8_t)(g_live_on ? 1 : 0)}; notify_cmd(b, 2); }
			break;
		case CMD_CLEAR_LOG: {                                // no-op in Phase 0, just ack
			uint8_t b[2] = {CMD_CLEAR_LOG, 0}; notify_cmd(b, 2);
			break;
		}
		case CMD_GET_CONFIG: {
			uint8_t b[8]; size_t o = 0; b[o++] = CMD_GET_CONFIG; b[o++] = 0;
			uint16_t interval = SPIKE_STEP; memcpy(b + o, &interval, 2); o += 2;
			int16_t hi = THRESH_HIGH_C; memcpy(b + o, &hi, 2); o += 2;
			int16_t lo = -3000;         memcpy(b + o, &lo, 2); o += 2;
			notify_cmd(b, o);
			break;
		}
		default: {
			uint8_t b[2] = {p[0], 0xFF}; notify_cmd(b, 2);   // unsupported
			break;
		}
		}
	}
};

class ServerCallbacks : public NimBLEServerCallbacks {
	void onConnect(NimBLEServer *s, NimBLEConnInfo &info) override {
		g_connected = true;
		// ask for a snappy connection interval (7.5–22.5 ms) to speed bulk transfer
		s->updateConnParams(info.getConnHandle(), 6, 18, 0, 200);
	}
	void onDisconnect(NimBLEServer *s, NimBLEConnInfo &info, int reason) override {
		g_connected = false; g_streaming = false; g_live_on = false; g_mtu = 23;
		NimBLEDevice::startAdvertising();
	}
	void onMTUChange(uint16_t mtu, NimBLEConnInfo &info) override { g_mtu = mtu; }
};

// ---------------------------------------------------------------- setup / loop
void setup() {
	Serial.begin(115200);
	delay(200);
	Serial.println("\nfreezer2 Phase-0 spike");

	NimBLEDevice::init(FZ2_DEVICE_NAME);
	NimBLEDevice::setMTU(247);

	NimBLEServer *server = NimBLEDevice::createServer();
	server->setCallbacks(new ServerCallbacks());

	NimBLEService *svc = server->createService(FZ2_SVC_UUID);
	g_cmd = svc->createCharacteristic(
		FZ2_CMD_UUID,
		NIMBLE_PROPERTY::READ | NIMBLE_PROPERTY::WRITE | NIMBLE_PROPERTY::WRITE_NR |
		NIMBLE_PROPERTY::NOTIFY);
	g_cmd->setCallbacks(new CmdCallbacks());
	g_live = svc->createCharacteristic(
		FZ2_LIVE_UUID, NIMBLE_PROPERTY::READ | NIMBLE_PROPERTY::NOTIFY);
	// NimBLE 2.x starts services automatically when the server starts (no svc->start()).

	NimBLEAdvertising *adv = NimBLEDevice::getAdvertising();
	adv->addServiceUUID(FZ2_SVC_UUID);
	adv->setName(FZ2_DEVICE_NAME);
	adv->enableScanResponse(true);
	NimBLEDevice::startAdvertising();

	Serial.println("advertising; waiting for a phone…");
}

void loop() {
	if (g_connected && g_streaming) pump_stream();

	if (g_connected && g_live_on && millis() - g_live_last > 2000) {
		g_live_last = millis();
		send_live();
	}
	delay(2);   // gentle pacing so notify tx buffers can drain
}
