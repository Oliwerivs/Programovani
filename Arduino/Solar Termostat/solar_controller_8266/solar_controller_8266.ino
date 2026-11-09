 ADDR_PANEL_ZAPAD/*
 * ═══════════════════════════════════════════════════════════════
 *  Solar Water Heater Controller  —  NodeMCU ESP8266
 * ═══════════════════════════════════════════════════════════════
 *  Hardware wiring (NodeMCU v1.0 / LoLin):
 *
 *  Sensor / Device      NodeMCU pin   GPIO
 *  ─────────────────    ───────────   ────
 *  DS18B20 data line    D5            GPIO14
 *  BH1750 SDA           D2            GPIO4
 *  BH1750 SCL           D1            GPIO5
 *  LCD 1602 SDA         D2            GPIO4   (same I2C bus)
 *  LCD 1602 SCL         D1            GPIO5
 *  5V Relay IN          D6            GPIO12
 *
 *  DS18B20: connect 4.7 kΩ pull-up between data and 3.3 V.
 *  Relay:   most 5 V modules work fine with 3.3 V logic on IN pin.
 *
 *  Features:
 *    ✓ NTP time sync with Czech DST (auto)
 *    ✓ LCD paging: temperatures / lux+time
 *    ✓ ThingSpeak live telemetry (5 fields)
 *    ✓ Google Sheets logging every 5 min (HTTPS + redirect follow)
 *    ✓ Solar-first relay logic with hysteresis + safety limits
 *
 *  Board: "NodeMCU 1.0 (ESP-12E Module)"  in Arduino board manager
 *
 *  Required libraries (Library Manager):
 *    - OneWire
 *    - DallasTemperature
 *    - BH1750  (by Christopher Laws)
 *    - LiquidCrystal I2C  (by Frank de Brabander)
 *    — Everything else is part of the ESP8266 Arduino core
 * ═══════════════════════════════════════════════════════════════
 */

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>       // BearSSL, part of ESP8266 core
#include <OneWire.h>
#include <DallasTemperature.h>
#include <BH1750.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <time.h>
#include <coredecls.h>              // settimeofday_cb() for NTP callback

// ┌─────────────────────────────────────────────────────────────┐
// │  USER CONFIGURATION                                         │
// └─────────────────────────────────────────────────────────────┘

// WiFi
const char* WIFI_SSID     = "Domus";
const char* WIFI_PASSWORD = "vojnuvmestec22";

// ThingSpeak  →  thingspeak.com (free account)
// Fields: 1=Boiler  2=Panel1  3=Panel2  4=Lux  5=Relay
const char* TS_WRITE_KEY  = "9OBTD9LU2ILK7573";

// Google Apps Script web app URL  (see GoogleAppsScript.gs)
const char* GS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz7zS3XfqcCdzlCupN_s6mWGjOxz9092PgEpTt_pf51KnR4SqXd-uWA1NJjSVmhJyqTXw/exec";

// POSIX timezone string — Czech Republic, auto-DST
// CET (UTC+1) winter, CEST (UTC+2) summer
const char* NTP_TZ     = "CET-1CEST,M3.5.0,M10.5.0/3";
const char* NTP_SERVER = "pool.ntp.org";

// DS18B20 hardware addresses
// Run ds18b20_scanner.ino first to discover the addresses!
DeviceAddress ADDR_BOILER = { 0x28, 0xC5, 0x8C, 0x1E, 0x00, 0x00, 0x80, 0x21 };
DeviceAddress ADDR_PANEL_JIH = { 0x28, 0xFF, 0xAD, 0x70, 0xB0, 0x17, 0x02, 0xBD };
DeviceAddress ADDR_PANEL_ZAPAD = { 0x28, 0xA0, 0x94, 0x69, 0x73, 0x23, 0x0B, 0x56 };

// ┌─────────────────────────────────────────────────────────────┐
// │  RELAY / CONTROL PARAMETERS                                 │
// └─────────────────────────────────────────────────────────────┘

// Relay turns ON  when: max(panel1,panel2) - boiler < RELAY_ON_DELTA
// Relay turns OFF when: max(panel1,panel2) - boiler > RELAY_OFF_DELTA
// (hysteresis prevents chattering)
const float RELAY_ON_DELTA  = 5.0f;   // °C
const float RELAY_OFF_DELTA = 8.0f;   // °C

const float BOILER_MAX_TEMP = 80.0f;  // °C  — safety ceiling, relay always OFF
const float BOILER_MIN_TEMP = 35.0f;  // °C  — too cold, relay always ON

// ┌─────────────────────────────────────────────────────────────┐
// │  PIN DEFINITIONS  (NodeMCU GPIO numbers)                    │
// └─────────────────────────────────────────────────────────────┘

#define ONE_WIRE_BUS  14   // D5
#define RELAY_PIN     12   // D6
#define I2C_SDA        4   // D2
#define I2C_SCL        5   // D1

// ┌─────────────────────────────────────────────────────────────┐
// │  TIMING (milliseconds)                                      │
// └─────────────────────────────────────────────────────────────┘

const uint32_t INTERVAL_SENSORS     =  5000UL;   //  5 s
const uint32_t INTERVAL_LCD_FLIP    =  4000UL;   //  4 s
const uint32_t INTERVAL_THINGSPEAK  = 30000UL;   // 30 s  (free tier min 15 s)
const uint32_t INTERVAL_SHEETS      = 300000UL;  //  5 min = 300000UL

// ═══════════════════════════════════════════════════════════════
//  Globals
// ═══════════════════════════════════════════════════════════════

OneWire           oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensors(&oneWire);
BH1750            lightMeter;
LiquidCrystal_I2C lcd(0x3F, 16, 2);

float tempBoiler = -127.0f;
float tempPanel1 = -127.0f;
float tempPanel2 = -127.0f;
float luxValue   = 0.0f;
bool  relayState = false;

char currentTime[10] = "--:--:--";
char currentDate[12] = "--/--/----";

bool wifiOk    = false;
bool ntpSynced = false;

uint32_t lastSensors    = 0;
uint32_t lastLcdFlip    = 0;
uint32_t lastThingSpeak = 0;
uint32_t lastSheets     = 0;
uint8_t  lcdPage        = 0;

// NTP sync flag — set by callback, avoids polling
volatile bool ntpJustSynced = false;

// ═══════════════════════════════════════════════════════════════
//  NTP callback (ESP8266-specific, fires once on first sync)
// ═══════════════════════════════════════════════════════════════
void ntpSyncCallback() {
  ntpJustSynced = true;
  ntpSynced     = true;
}

// ═══════════════════════════════════════════════════════════════
//  SETUP
// ═══════════════════════════════════════════════════════════════
void setup() {
  Serial.begin(115200);
  Serial.println(F("\n\n=== Solar Controller (ESP8266) Boot ==="));

  // Relay OFF first — safety
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  // I2C + LCD
  Wire.begin(I2C_SDA, I2C_SCL);
  lcd.init();
  lcd.backlight();
  lcdMessage("Solar Controller", "Booting...");
  delay(800);

  // DS18B20
  tempSensors.begin();
  tempSensors.setResolution(ADDR_BOILER, 12);
  tempSensors.setResolution(ADDR_PANEL_JIH, 12);
  tempSensors.setResolution(ADDR_PANEL_ZAPAD, 12);
  Serial.printf_P(PSTR("DS18B20 devices found: %d\n"), tempSensors.getDeviceCount());

  // BH1750
  if (lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println(F("BH1750 OK"));
  } else {
    Serial.println(F("BH1750 FAIL — check wiring!"));
  }

  // WiFi
  lcdMessage("Connecting WiFi", WIFI_SSID);
  connectWiFi();

  // NTP — ESP8266 uses configTzTime() (POSIX string variant)
  if (wifiOk) {
    settimeofday_cb(ntpSyncCallback);        // callback when synced
    configTzTime(NTP_TZ, NTP_SERVER, "time.cloudflare.com");
    lcdMessage("Syncing NTP...", "");
    Serial.println(F("Waiting for NTP sync..."));
    uint32_t t0 = millis();
    while (!ntpSynced && millis() - t0 < 8000) {
      delay(200);
      yield();  // feed watchdog while waiting
    }
    if (ntpSynced) {
      Serial.println(F("NTP synced!"));
    } else {
      Serial.println(F("NTP timeout — will sync when available"));
    }
  }

  // Initial readings
  readSensors();
  updateRelay();
  refreshTime();
  updateLCD();

  Serial.println(F("=== Boot complete ==="));
}

// ═══════════════════════════════════════════════════════════════
//  LOOP
// ═══════════════════════════════════════════════════════════════
void loop() {
  uint32_t now = millis();

  // WiFi watchdog
  if (WiFi.status() != WL_CONNECTED) {
    wifiOk = false;
    connectWiFi();
  }

  // Sensors + relay
  if (now - lastSensors >= INTERVAL_SENSORS) {
    lastSensors = now;
    readSensors();
    updateRelay();
    refreshTime();
    updateLCD();   // refresh immediately after sensor read
  }

  // LCD page flip
  if (now - lastLcdFlip >= INTERVAL_LCD_FLIP) {
    lastLcdFlip = now;
    lcdPage = (lcdPage + 1) % 2;
    updateLCD();
  }

  // ThingSpeak
  if (wifiOk && now - lastThingSpeak >= INTERVAL_THINGSPEAK) {
    lastThingSpeak = now;
    uploadThingSpeak();
  }

  // Google Sheets
  if (wifiOk && now - lastSheets >= INTERVAL_SHEETS) {
    lastSheets = now;
    uploadGoogleSheets();
  }

  yield();  // keep ESP8266 watchdog happy
}

// ═══════════════════════════════════════════════════════════════
//  WIFI
// ═══════════════════════════════════════════════════════════════
void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) { wifiOk = true; return; }
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print(F("WiFi connecting"));
  uint8_t attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 24) {
    delay(500);
    Serial.print('.');
    attempts++;
    yield();
  }
  wifiOk = (WiFi.status() == WL_CONNECTED);
  if (wifiOk) { 
    Serial.print(F("\nConnected, IP: "));
    Serial.println(WiFi.localIP());
  } else {
    Serial.println(F("\nWiFi failed — offline mode"));
  }
}

// ═══════════════════════════════════════════════════════════════
//  SENSORS
// ═══════════════════════════════════════════════════════════════
void readSensors() {
  tempSensors.requestTemperatures();

  float b  = tempSensors.getTempC(ADDR_BOILER);
  float p1 = tempSensors.getTempC(ADDR_PANEL_JIH);
  float p2 = tempSensors.getTempC(ADDR_PANEL_ZAPAD);

  if (b  != DEVICE_DISCONNECTED_C) tempBoiler = b;
  if (p1 != DEVICE_DISCONNECTED_C) tempPanel1 = p1;
  if (p2 != DEVICE_DISCONNECTED_C) tempPanel2 = p2;

  luxValue = lightMeter.readLightLevel();

  Serial.printf_P(PSTR("[Sensors] Boiler=%.1f°C  P1=%.1f°C  P2=%.1f°C  Lux=%.0f\n"),
                  tempBoiler, tempPanel1, tempPanel2, luxValue);
}

// ═══════════════════════════════════════════════════════════════
//  RELAY CONTROL
// ═══════════════════════════════════════════════════════════════
void updateRelay() {
  // Hard safety limit
  if (tempBoiler >= BOILER_MAX_TEMP) { setRelay(false); return; }
  // Always heat if very cold
  if (tempBoiler <  BOILER_MIN_TEMP) { setRelay(true);  return; }

  float maxPanel = (tempPanel1 > tempPanel2) ? tempPanel1 : tempPanel2;
  float delta    = maxPanel - tempBoiler;

  bool shouldHeat = relayState;  // default: no change

  if (!relayState && delta < RELAY_ON_DELTA)  shouldHeat = true;
  if ( relayState && delta < RELAY_OFF_DELTA) shouldHeat = true;
  if (              delta >= RELAY_OFF_DELTA) shouldHeat = false;

  setRelay(shouldHeat);
}

void setRelay(bool on) {
  if (on != relayState) {
    relayState = on;
    digitalWrite(RELAY_PIN, on ? HIGH : LOW);
    Serial.println(on ? F("[Relay] ON  (electric backup)") : F("[Relay] OFF (solar OK)"));
  }
}

// ═══════════════════════════════════════════════════════════════
//  TIME  —  ESP8266: use time() + localtime(), NOT getLocalTime()
// ═══════════════════════════════════════════════════════════════
void refreshTime() {
  time_t now = time(nullptr);
  if (now < 1000000000UL) return;  // not synced yet (epoch too small)
  ntpSynced = true;
  struct tm* ti = localtime(&now);
  strftime(currentTime, sizeof(currentTime), "%H:%M:%S", ti);
  strftime(currentDate, sizeof(currentDate), "%d.%m.%Y", ti);
}

// ─── helper: build ISO datetime string for HTTP parameters ────
void buildDatetime(char* buf, size_t len) {
  time_t now = time(nullptr);
  if (now < 1000000000UL) {
    strncpy(buf, "unknown", len);
    return;
  }
  struct tm* ti = localtime(&now);
    strftime(buf, len, "%Y-%m-%dT%H:%M:%S", ti);  // T separator avoids space in URL
}

// ═══════════════════════════════════════════════════════════════
//  LCD
// ═══════════════════════════════════════════════════════════════
void lcdMessage(const char* line1, const char* line2) {
  lcd.clear();
  lcd.setCursor(0, 0); lcd.print(line1);
  lcd.setCursor(0, 1); lcd.print(line2);
}

void updateLCD() {
  char row0[17], row1[17];
  lcd.clear();

  if (lcdPage == 0) {
    // Page 0: boiler temp + mode indicator, panel temps
    snprintf(row0, 17, "Boil %5.1fC %-3s", tempBoiler, relayState ? "HTR" : "SOL");
    snprintf(row1, 17, "P1:%5.1f P2:%4.1f", tempPanel1, tempPanel2);
  } else {
    // Page 1: sunshine + date/time
    if (luxValue < 1000.0f) {
      snprintf(row0, 17, "Sun: %6.0f lux", luxValue);
    } else {
      snprintf(row0, 17, "Sun: %5.1f klx", luxValue / 1000.0f);
    }
    // Fit date + time into 16 chars:  "20.05.2025 14:32"
    char tmp[17];
    snprintf(tmp, 17, "%s %s", currentDate, currentTime);
    // Truncate to 16 chars (time may be "--:--:--" if not synced)
    strncpy(row1, tmp, 16);
    row1[16] = '\0';
  }

  lcd.setCursor(0, 0); lcd.print(row0);
  lcd.setCursor(0, 1); lcd.print(row1);
}

// ═══════════════════════════════════════════════════════════════
//  THINGSPEAK  (plain HTTP, api.thingspeak.com is not HTTPS-only)
//  Fields: 1=Boiler  2=Panel1  3=Panel2  4=Lux  5=Relay
// ═══════════════════════════════════════════════════════════════
void uploadThingSpeak() {
  char url[256];
  snprintf(url, sizeof(url),
    "http://api.thingspeak.com/update"
    "?api_key=%s"
    "&field1=%.1f&field2=%.1f&field3=%.1f"
    "&field4=%.0f&field5=%d",
    TS_WRITE_KEY,
    tempBoiler, tempPanel1, tempPanel2,
    luxValue, (int)relayState
  );

  WiFiClient client;
  HTTPClient http;
  // ESP8266 HTTPClient: begin(client, url) — not begin(url) alone
  http.begin(client, url);
  int code = http.GET();
  Serial.printf_P(PSTR("[ThingSpeak] HTTP %d\n"), code);
  http.end();
}

// ═══════════════════════════════════════════════════════════════
//  GOOGLE SHEETS  (HTTPS via BearSSL, follow 302 redirect)
// ═══════════════════════════════════════════════════════════════
void uploadGoogleSheets() {
  char datetime[20];
  buildDatetime(datetime, sizeof(datetime));

  char url[512];
  snprintf(url, sizeof(url),
    "%s"
    "?datetime=%s"
    "&boiler=%.1f&panel1=%.1f&panel2=%.1f"
    "&lux=%.0f&relay=%d",
    GS_SCRIPT_URL,
    datetime,
    tempBoiler, tempPanel1, tempPanel2,
    luxValue, (int)relayState
  );

  // BearSSL client — setInsecure() skips cert verification
  // (acceptable for IoT data logging; the data is not sensitive)
  BearSSL::WiFiClientSecure secureClient;
  secureClient.setInsecure();
  secureClient.setBufferSizes(512, 512);

  HTTPClient https;
  https.begin(secureClient, url);
  https.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);
  https.setTimeout(8000);   // 8 s — Apps Script can be slow
  int code = https.GET();
  Serial.printf_P(PSTR("[Sheets] HTTP %d\n"), code);
  https.end();
}
