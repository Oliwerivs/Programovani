#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <Wire.h>
#include <BH1750.h>
#include <OneWire.h>

#define EEPROM_ADDRESS 0x50  // I2C address of EEPROM
#define MAC_ADDRESS_START 0  // Starting address of MAC address in EEPROM

void setup() {
  Serial.begin(115200);

  Wire.begin();

  byte macAddress[6];
  readMACAddress(macAddress);

  Serial.print("MAC Address: ");
  for (int i = 0; i < 6; i++) {
    Serial.print(macAddress[i], HEX);
    if (i < 5) {
      Serial.print(':');
    }
  }
  Serial.println();
}

void loop() {
  // Your main code here
}

void readMACAddress(byte *macAddress) {
  Wire.beginTransmission(EEPROM_ADDRESS);
  Wire.write((int)(MAC_ADDRESS_START >> 8)); // MSB of address
  Wire.write((int)(MAC_ADDRESS_START & 0xFF)); // LSB of address
  Wire.endTransmission();

  Wire.requestFrom(EEPROM_ADDRESS, 6);

  for (int i = 0; i < 6; i++) {
    if (Wire.available()) {
      macAddress[i] = Wire.read();
    }
  }
}