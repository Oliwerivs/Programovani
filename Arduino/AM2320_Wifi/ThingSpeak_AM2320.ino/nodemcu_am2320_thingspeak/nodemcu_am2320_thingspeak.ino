// ============================================================
//  NodeMCU + AM2320 (I2C) → ThingSpeak
//  PRODUCTION VERSION — Deep sleep enabled
//
//  AM2320 Wiring:
//    VDD → 3.3V
//    GND → GND
//    SDA → D2 (GPIO4)  + 4.7kΩ pull-up to 3.3V
//    SCL → D1 (GPIO5)  + 4.7kΩ pull-up to 3.3V
//
//  IMPORTANT: Wire D0 (GPIO16) → RST for deep sleep wake-up!
//  Disconnect D0→RST before uploading, reconnect after!
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

// ── Sleep Interval ───────────────────────────────────────────
// Uncomment ONE interval, keep the rest commented out
//
//                        seconds  × 1,000,000 = microseconds
//#define SLEEP_US   ( 5 * 60 * 1000000UL)   //  5 minutes
 #define SLEEP_US  (10 * 60 * 1000000UL)  // 10 minutes  ← recommended
// #define SLEEP_US  (20 * 60 * 1000000UL)  // 20 minutes
// #define SLEEP_US  (30 * 60 * 1000000UL)  // 30 minutes

// ── I2C Pins ─────────────────────────────────────────────────
#define SDA_PIN           D2
#define SCL_PIN           D1

// ── Timeouts ─────────────────────────────────────────────────
#define WIFI_TIMEOUT_MS   15000   // give up WiFi connect after 15s
#define TS_TIMEOUT_MS     5000    // give up ThingSpeak response after 5s

// ── Calibration Offsets ──────────────────────────────────────
// offset = reference thermometer − sensor reading
// Example: sensor 25.5°C, reference 24.0°C → TEMP_OFFSET = -1.5
#define TEMP_OFFSET       0.0    // °C
#define HUM_OFFSET        0.0    // %RH

// ── Globals ──────────────────────────────────────────────────
Adafruit_AM2320 am2320;

// ============================================================
void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.printf("\n[BOOT] AM2320 ThingSpeak — sleep: %lu min\n",
                SLEEP_US / 60000000UL);

  // Start with WiFi off during sensor read
  WiFi.mode(WIFI_OFF);
  WiFi.forceSleepBegin();
  delay(1);

  // ── Init I2C & AM2320 ────────────────────────────────────
  Wire.begin(SDA_PIN, SCL_PIN);
  delay(2000); // AM2320 power-on warmup

  if (!am2320.begin()) {
    Serial.println(F("[ERROR] AM2320 not found — sleeping"));
    goToSleep();
    return;
  }

  // ── Read sensor ───────────────────────────────────────────
  float rawTemp = am2320.readTemperature();
  float rawHum  = am2320.readHumidity();

  if (isnan(rawTemp) || isnan(rawHum)) {
    Serial.println(F("[AM2320] Read failed — sleeping"));
    goToSleep();
    return;
  }

  // ── Apply calibration ─────────────────────────────────────
  float temperature = rawTemp + TEMP_OFFSET;
  float humidity    = constrain(rawHum + HUM_OFFSET, 0.0, 100.0);

  Serial.printf("[AM2320] Temp: %.2f°C  Hum: %.2f%%\n",
                temperature, humidity);

  // ── Heat Index ────────────────────────────────────────────
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
  Serial.printf("[CALC]  Heat Index: %.2f°C\n", heatIndex);

  // ── Connect WiFi ─────────────────────────────────────────
  WiFi.forceSleepWake();
  delay(1);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print(F("[WiFi] Connecting"));
  unsigned long t0 = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - t0 > WIFI_TIMEOUT_MS) {
      Serial.println(F("\n[WiFi] Timeout — sleeping"));
      goToSleep();
      return;
    }
    delay(250);
    Serial.print('.');
  }
  Serial.printf("\n[WiFi] OK  RSSI: %ddBm\n", WiFi.RSSI());

  // ── Send to ThingSpeak ────────────────────────────────────
  bool ok = sendToThingSpeak(temperature, humidity, heatIndex);
  Serial.println(ok ? F("[TS] ✓ Sent!") : F("[TS] ✗ Failed"));

  // ── Clean up & sleep ──────────────────────────────────────
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);
  WiFi.forceSleepBegin();
  delay(1);

  goToSleep();
}

void loop() {} // never reached — deep sleep reboots via RST

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
    if (millis() - t0 > TS_TIMEOUT_MS) {
      client.stop();
      return false;
    }
    delay(10);
  }

  String resp = client.readStringUntil('\n');
  client.stop();
  return resp.indexOf("200") > 0;
}

// ============================================================
void goToSleep() {
  Serial.printf("[SLEEP] %lu minutes — good night!\n",
                SLEEP_US / 60000000UL);
  Serial.flush();
  ESP.deepSleep(SLEEP_US, WAKE_RF_DEFAULT);
}
