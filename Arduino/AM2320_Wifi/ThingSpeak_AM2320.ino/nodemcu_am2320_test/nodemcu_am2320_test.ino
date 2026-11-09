// ============================================================
//  NodeMCU + AM2320 (I2C) → ThingSpeak
//  TEST VERSION — No deep sleep, uses delay() loop
//
//  AM2320 Wiring:
//    VDD → 3.3V
//    GND → GND
//    SDA → D2 (GPIO4)  + 4.7kΩ pull-up to 3.3V
//    SCL → D1 (GPIO5)  + 4.7kΩ pull-up to 3.3V
//
//  No D0→RST wire needed for this version!
//
//  Libraries required:
//    - Adafruit AM2320
//    - Adafruit Unified Sensor
//    - Adafruit BusIO
// ============================================================

#include <ESP8266WiFi.h>
#include <Wire.h>
#include <Adafruit_AM2320.h>

// ── WiFi & ThingSpeak ────────────────────────────────────────
#define WIFI_SSID         "Domus"
#define WIFI_PASSWORD     "vojnuvmestec22"

#define TS_API_KEY        "859R8DRWYACMXF14"
#define TS_HOST           "api.thingspeak.com"
#define TS_PORT           80

// ── Interval ─────────────────────────────────────────────────
// ThingSpeak free tier minimum = 15 seconds
#define INTERVAL_MS       15000

// ── I2C Pins ─────────────────────────────────────────────────
#define SDA_PIN           D2
#define SCL_PIN           D1

// ── Calibration Offsets ──────────────────────────────────────
//
//  HOW TO CALIBRATE:
//  1. Place a trusted reference thermometer/hygrometer
//     next to your AM2320 for 10-15 minutes
//  2. Compare the readings
//  3. Set offset = reference - sensor
//
//  Examples:
//    Sensor reads 25.5°C, reference shows 24.0°C
//    → offset = 24.0 - 25.5 = -1.5 → TEMP_OFFSET = -1.5
//
//    Sensor reads 52.0%, reference shows 57.0%
//    → offset = 57.0 - 52.0 = +5.0 → HUM_OFFSET = +5.0
//
#define TEMP_OFFSET       0.0    // °C  — adjust until sensor matches reference
#define HUM_OFFSET        0.0    // %RH — adjust until sensor matches reference

// ── Globals ──────────────────────────────────────────────────
Adafruit_AM2320 am2320;
unsigned long lastSendTime = 0;
int readingCount = 0;

// ============================================================
void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println(F("\n╔══════════════════════════════════════╗"));
  Serial.println(F("║  NodeMCU AM2320 — TEST MODE          ║"));
  Serial.println(F("║  No deep sleep — delay() loop        ║"));
  Serial.println(F("╚══════════════════════════════════════╝\n"));

  // Show active calibration offsets on boot
  Serial.printf("[CAL] Temp offset: %+.2f °C\n", TEMP_OFFSET);
  Serial.printf("[CAL] Hum  offset: %+.2f %%\n\n", HUM_OFFSET);

  // ── Init I2C & AM2320 ────────────────────────────────────
  Wire.begin(SDA_PIN, SCL_PIN);
  delay(2000); // AM2320 power-on warmup

  if (!am2320.begin()) {
    Serial.println(F("[ERROR] AM2320 not found!"));
    Serial.println(F("  Check: VDD→3.3V, GND→GND"));
    Serial.println(F("         SDA→D2,   SCL→D1"));
    Serial.println(F("         4.7kΩ pull-ups on SDA+SCL"));
    Serial.println(F("  Halting."));
    while (true) { delay(1000); }
  }
  Serial.println(F("[AM2320] Sensor OK"));

  // ── Connect WiFi ─────────────────────────────────────────
  Serial.print(F("[WiFi] Connecting to "));
  Serial.println(WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print('.');
  }
  Serial.printf("\n[WiFi] Connected!  IP: %s  RSSI: %ddBm\n\n",
                WiFi.localIP().toString().c_str(), WiFi.RSSI());

  Serial.printf("[INFO] Sending every %d seconds\n", INTERVAL_MS / 1000);
  Serial.println(F("─────────────────────────────────────────\n"));
}

// ============================================================
void loop() {
  unsigned long now = millis();

  if (now - lastSendTime >= INTERVAL_MS || lastSendTime == 0) {
    lastSendTime = now;
    readingCount++;

    Serial.printf("── Reading #%d ──────────────────────────\n", readingCount);

    // ── Read raw values from AM2320 ───────────────────────
    float rawTemp = am2320.readTemperature();
    float rawHum  = am2320.readHumidity();

    if (isnan(rawTemp) || isnan(rawHum)) {
      Serial.println(F("[AM2320] Read failed — skipping"));
      return;
    }

    // ── Apply calibration offsets ─────────────────────────
    float temperature = rawTemp + TEMP_OFFSET;
    float humidity    = rawHum  + HUM_OFFSET;

    // Clamp humidity to valid 0–100% range
    humidity = constrain(humidity, 0.0, 100.0);

    // ── Print raw vs calibrated side by side ─────────────
    // Helpful for dialling in your offsets during testing
    Serial.printf("[RAW]  Temp: %.2f °C   Hum: %.2f %%\n", rawTemp, rawHum);
    Serial.printf("[CAL]  Temp: %.2f °C   Hum: %.2f %%\n", temperature, humidity);

    // ── Heat Index (uses calibrated values) ───────────────
    float heatIndex = temperature;
    if (temperature >= 27.0 && humidity >= 40.0) {
      float t = temperature, h = humidity;
      heatIndex = -8.78469475556
        + 1.61139411    * t
        + 2.33854883889 * h
        - 0.14611605    * t * h
        - 0.012308094   * t * t
        - 0.016424828   * h * h
        + 0.002211732   * t * t * h
        + 0.00072546    * t * h * h
        - 0.000003582   * t * t * h * h;
    }
    Serial.printf("[CALC] Heat Index: %.2f °C\n", heatIndex);

    // ── Reconnect WiFi if dropped ─────────────────────────
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println(F("[WiFi] Reconnecting..."));
      WiFi.reconnect();
      unsigned long t0 = millis();
      while (WiFi.status() != WL_CONNECTED && millis() - t0 < 10000) {
        delay(500); Serial.print('.');
      }
      if (WiFi.status() != WL_CONNECTED) {
        Serial.println(F("[WiFi] Failed — skipping send"));
        return;
      }
      Serial.println(F("[WiFi] Reconnected"));
    }

    // ── Send calibrated values to ThingSpeak ──────────────
    bool ok = sendToThingSpeak(temperature, humidity, heatIndex);
    Serial.println(ok ? F("[TS] ✓ Sent!") : F("[TS] ✗ Failed"));
    Serial.printf("[NEXT] Next in %d seconds\n\n", INTERVAL_MS / 1000);
  }
}

// ============================================================
bool sendToThingSpeak(float temp, float hum, float hi) {
  WiFiClient client;
  if (!client.connect(TS_HOST, TS_PORT)) {
    Serial.println(F("[TS] Connection failed"));
    return false;
  }

  String body = "api_key=";
  body += TS_API_KEY;
  body += "&field1=" + String(temp, 2);
  body += "&field2=" + String(hum,  2);
  body += "&field3=" + String(hi,   2);

  client.println("POST /update HTTP/1.1");
  client.println("Host: " + String(TS_HOST));
  client.println(F("Content-Type: application/x-www-form-urlencoded"));
  client.println("Content-Length: " + String(body.length()));
  client.println(F("Connection: close"));
  client.println();
  client.print(body);

  unsigned long t0 = millis();
  while (!client.available()) {
    if (millis() - t0 > 5000) { client.stop(); return false; }
    delay(10);
  }

  String resp = client.readStringUntil('\n');
  client.stop();
  return resp.indexOf("200") > 0;
}
