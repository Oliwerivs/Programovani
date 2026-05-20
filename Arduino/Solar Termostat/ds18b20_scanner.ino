/*
 * DS18B20 Address Scanner — NodeMCU ESP8266
 * ──────────────────────────────────────────────────────────────
 * Connect DS18B20 data pin to D5 (GPIO14) with 4.7 kΩ pull-up
 * to 3.3 V.  Open Serial Monitor at 115200 baud.
 *
 * Best practice: connect sensors ONE AT A TIME to know which
 * address belongs to which physical sensor (boiler / panel 1 / 2).
 * ──────────────────────────────────────────────────────────────
 */

#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS  14   // D5 on NodeMCU

OneWire           oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(115200);
  delay(1000);
  sensors.begin();

  int count = sensors.getDeviceCount();
  Serial.printf("\nFound %d DS18B20 sensor(s) on GPIO %d (D5)\n\n", count, ONE_WIRE_BUS);

  DeviceAddress addr;
  for (int i = 0; i < count; i++) {
    if (sensors.getAddress(addr, i)) {
      Serial.printf("Sensor %d:  { ", i + 1);
      for (int b = 0; b < 8; b++) {
        Serial.printf("0x%02X", addr[b]);
        if (b < 7) Serial.print(", ");
      }
      Serial.println(" }");
    } else {
      Serial.printf("Sensor %d: address read error\n", i + 1);
    }
  }
  Serial.println("\n--- Live temperatures ---");
}

void loop() {
  sensors.requestTemperatures();
  int count = sensors.getDeviceCount();
  for (int i = 0; i < count; i++) {
    Serial.printf("Sensor %d: %.2f °C\n", i + 1, sensors.getTempCByIndex(i));
  }
  Serial.println("---");
  delay(2000);
}
