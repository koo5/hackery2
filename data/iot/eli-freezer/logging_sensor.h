#include "esphome.h"
#include "LittleFS.h"

namespace esphome {
namespace logging_sensor {

// Example custom component that reads a sensor (e.g. ADC) and writes to SPIFFS
class LoggingSensor : public PollingComponent, public sensor::Sensor {
 public:
  // Poll every 1 second
  LoggingSensor() : PollingComponent(1000) {}

  void setup() override {
    // Initialize SPIFFS (or LittleFS)
    // The 'true' argument means "format if necessary"
    if (!SPIFFS.begin(true)) {
      ESP_LOGE("LoggingSensor", "Failed to mount SPIFFS");
    }
  }

  void update() override {
    // Example: read from ADC pin on ESP32-S2 Mini
    float value = analogRead(1);  // Replace with the correct ADC pin

    // Publish the reading to ESPHome
    publish_state(value);

    // Add to RAM buffer for batching
    buffer_.push_back(value);

    // Example: write to flash once we reach 50 readings
    if (buffer_.size() >= 50) {
      flush_to_file();
    }
  }

 protected:
  // Temporary buffer in RAM
  std::vector<float> buffer_;

  void flush_to_file() {
    // Open (or create) file in append mode
    File f = SPIFFS.open("/sensor_data.csv", FILE_APPEND);
    if (!f) {
      ESP_LOGE("LoggingSensor", "Failed to open file for appending");
      return;
    }

    // Write each buffered reading as CSV or one value per line
    for (float val : buffer_) {
      f.println(String(val));
    }
    f.close();

    // Clear the buffer after writing
    buffer_.clear();
  }
};

}  // namespace logging_sensor
}  // namespace esphome

