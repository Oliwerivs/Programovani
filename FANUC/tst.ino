// ============================================================
//  ESP8266 + DHT11 → ThingSpeak  |  Battery-Optimised
//  Deep Sleep between readings to maximise battery life
//
//  Libraries required (install via Arduino Library Manager):
//    - DHT sensor library  (Adafruit)
//    - Adafruit Unified Sensor
//    - ESP8266WiFi         (bundled with ESP8266 board package)
//
//  Board: NodeMCU 1.0 (ESP-12E Module) or bare ESP-01/ESP-12
//  IMPORTANT: Wire GPIO16 (D0) → RST for deep sleep wake-up!
// ============================================================

#include <ESP8266WiFi.h>
#include <DHT.h>

// ── User Configuration ───────────────────────────────────────
#define WIFI_SSID       "YOUR_SSID"
#define WIFI_PASSWORD   "YOUR_PASSWORD"

#define TS_API_KEY      "YOUR_THINGSPEAK_WRITE_API_KEY"
#define TS_HOST         "api.thingspeak.com"
#define TS_PORT         80

// ThingSpeak field mapping
// Field 1 → Temperature (°C)
// Field 2 → Humidity (%)
// Field 3 → Battery voltage (V)  [optional]

// ── Hardware Pins ────────────────────────────────────────────
#define DHT_PIN         D4       // GPIO2 — data pin
#define DHT_TYPE        DHT11
#define BATT_PIN        A0       // Analog pin for battery voltage divider

// ── Power / Timing Settings ──────────────────────────────────
// Deep sleep duration in microseconds
// 300e6 = 5 minutes between readings (good balance)
// 60e6  = 1 minute  (more data, shorter battery life)
// 900e6 = 15 minutes (longest battery life)
#define SLEEP_DURATION_US   300e6    // 5 minutes

// Max time to wait for WiFi connection before giving up + sleeping
#define WIFI_TIMEOUT_MS     15000    // 15 seconds

// Number of DHT read retries before giving up
#define DHT_MAX_RETRIES     5
#define DHT_RETRY_DELAY_MS  500

// ── Battery Voltage Divider ───────────────────────────────────
// Voltage divider: R1=100kΩ top, R2=220kΩ bottom → A0 max 1.0V
// ADC reference = 1.0V on ESP8266
// Vbatt = ADC_reading * (R1+R2)/R2 * (1.0/1023.0)
// Adjust VDIV_RATIO for your actual resistor values
#define VDIV_RATIO          (320.0 / 220.0)  // (R1+R2)/R2

// ── Globals ──────────────────────────────────────────────────
DHT dht(DHT_PIN, DHT_TYPE);

// ============================================================
void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println(F("\n\n[BOOT] ESP8266 DHT11 ThingSpeak Logger"));

  // Power optimisation: disable unused peripherals immediately
  WiFi.mode(WIFI_OFF);          // Start with WiFi off
  WiFi.forceSleepBegin();
  delay(1);

  // ── Read DHT11 ───────────────────────────────────────────
  dht.begin();
  delay(1000);                   // DHT11 needs 1s after power-on

  float temperature = NAN;
  float humidity    = NAN;

  for (int i = 0; i < DHT_MAX_RETRIES; i++) {
    temperature = dht.readTemperature();
    humidity    = dht.readHumidity();

    if (!isnan(temperature) && !isnan(humidity)) {
      Serial.printf("[DHT] Temp: %.1f°C  Humidity: %.1f%%\n",
                    temperature, humidity);
      break;
    }
    Serial.printf("[DHT] Read failed (attempt %d/%d), retrying...\n",
                  i + 1, DHT_MAX_RETRIES);
    delay(DHT_RETRY_DELAY_MS);
  }

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println(F("[DHT] All retries failed — going back to sleep"));
    goToSleep();
    return;
  }

  // ── Read Battery Voltage ──────────────────────────────────
  float battVoltage = readBatteryVoltage();
  Serial.printf("[BATT] Voltage: %.2fV\n", battVoltage);

  // Optional: sleep early if battery critically low (< 3.3V for LiPo)
  if (battVoltage > 0.5 && battVoltage < 3.3) {
    Serial.println(F("[BATT] Critical! Entering long sleep to protect battery."));
    ESP.deepSleep(3600e6);       // Sleep 1 hour if battery critical
    return;
  }

  // ── Connect to WiFi ───────────────────────────────────────
  WiFi.forceSleepWake();
  delay(1);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print(F("[WiFi] Connecting"));
  unsigned long wifiStart = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - wifiStart > WIFI_TIMEOUT_MS) {
      Serial.println(F("\n[WiFi] Timeout — going back to sleep"));
      goToSleep();
      return;
    }
    delay(250);
    Serial.print('.');
  }
  Serial.printf("\n[WiFi] Connected. IP: %s  RSSI: %ddBm\n",
                WiFi.localIP().toString().c_str(), WiFi.RSSI());

  // ── Send to ThingSpeak ────────────────────────────────────
  bool success = sendToThingSpeak(temperature, humidity, battVoltage);

  if (success) {
    Serial.println(F("[TS] Data sent successfully"));
  } else {
    Serial.println(F("[TS] Send failed"));
  }

  // ── Disconnect WiFi cleanly before sleep ──────────────────
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);
  WiFi.forceSleepBegin();
  delay(1);

  goToSleep();
}

// ── loop() is never reached (deep sleep reboots via RST) ────
void loop() {}

// ============================================================
//  Send temperature, humidity and battery to ThingSpeak
// ============================================================
bool sendToThingSpeak(float temp, float hum, float batt) {
  WiFiClient client;

  if (!client.connect(TS_HOST, TS_PORT)) {
    Serial.println(F("[TS] Connection failed"));
    return false;
  }

  // Build query string
  String body = "api_key=";
  body += TS_API_KEY;
  body += "&field1=" + String(temp, 1);
  body += "&field2=" + String(hum, 1);
  body += "&field3=" + String(batt, 2);

  // HTTP POST request
  client.println("POST /update HTTP/1.1");
  client.println("Host: " + String(TS_HOST));
  client.println(F("Content-Type: application/x-www-form-urlencoded"));
  client.println("Content-Length: " + String(body.length()));
  client.println(F("Connection: close"));
  client.println();
  client.println(body);

  // Wait for response (up to 5s)
  unsigned long timeout = millis();
  while (!client.available()) {
    if (millis() - timeout > 5000) {
      Serial.println(F("[TS] Response timeout"));
      client.stop();
      return false;
    }
    delay(10);
  }

  // Read first line of response to check status
  String responseLine = client.readStringUntil('\n');
  Serial.println("[TS] Response: " + responseLine);

  client.stop();

  // ThingSpeak returns "0" in body on failure
  return responseLine.indexOf("200") > 0;
}

// ============================================================
//  Read battery voltage via voltage divider on A0
// ============================================================
float readBatteryVoltage() {
  // Average 10 samples for stability
  int sum = 0;
  for (int i = 0; i < 10; i++) {
    sum += analogRead(BATT_PIN);
    delay(5);
  }
  float adcAvg = sum / 10.0;
  // ESP8266 ADC: 0–1023 maps to 0–1.0V
  float voltage = (adcAvg / 1023.0) * 1.0 * VDIV_RATIO;
  return voltage;
}

// ============================================================
//  Enter deep sleep — GPIO16 must be wired to RST to wake up
// ============================================================
void goToSleep() {
  Serial.printf("[SLEEP] Entering deep sleep for %.0f seconds...\n",
                SLEEP_DURATION_US / 1e6);
  Serial.flush();
  ESP.deepSleep(SLEEP_DURATION_US, WAKE_RF_DEFAULT);
  // Execution stops here — chip resets on wake
}
