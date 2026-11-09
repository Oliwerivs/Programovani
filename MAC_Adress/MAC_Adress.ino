#include <ESP8266WiFi.h>

void setup()
{
    Serial.begin(9600);

    String mac = WiFi.macAddress();
    Serial.println(mac);
}

void loop() {}