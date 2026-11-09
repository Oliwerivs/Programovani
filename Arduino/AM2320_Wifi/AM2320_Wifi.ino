// Feven Kitsune
// 11/16/2019

#include <ESP8266WiFi.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <FS.h>

#include "Adafruit_Sensor.h"
#include "Adafruit_AM2320.h"


// WiFi Settings
const char* ssid = "Domus";
const char* password = "vojnuvmestec22";

// Sensor data storage
float temperature;
const float temperature_offset = -4.0; // was -4.0
float humidity;
unsigned long last_refresh;

// WiFiServer Object
AsyncWebServer server(80);

// AM2320 Object
Adafruit_AM2320 am2320 = Adafruit_AM2320();
/*
String getHumidity() {
  Serial.println(humidity);
  return String(humidity);
}

String getTemperature() {
  Serial.println(temperature);
  return String(temperature);
}

String processor(const String& var) {
  return "OK";
}*/

void setup() {
  Serial.begin(9600);
  Serial.println("Room Weather Station");
  while (!Serial) {
    delay(10); // hang out until serial port opens
  }
  Serial.println("Adafruit AM2320 Basic Test");
  am2320.begin();
  // Check if SPIFFS FileSystem is enabled...
  if(!SPIFFS.begin()){
    Serial.println("An Error has occurred while mounting SPIFFS");
    return;
  }

  // Connect to WiFi
  am2320.begin();
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);

  // Wait for connection to finish...
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");

  Serial.println("AM2320 Test");
  if (!am2320.begin()) {
    Serial.println("Couldn't find AM2320 sensor!");
    while (1);
  }

  // Print the IP address
  Serial.print("Use this URL to connect: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/");
}

void loop() {

  temperature =am2320.readTemperature();
  temperature = temperature + temperature_offset;
  Serial.print("Temp: "); Serial.println(temperature);
  Serial.print("Hum: "); Serial.println(am2320.readHumidity());

  delay(2000);
}