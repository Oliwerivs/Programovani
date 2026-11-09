#include "Adafruit_Sensor.h"
#include "Adafruit_AM2320.h"
#include <ESP8266WiFi.h>
 
String apiKey = "859R8DRWYACMXF14";     //  Enter your Write API key from ThingSpeak
 
const char *ssid =  "Vydrany19";     // replace with your wifi ssid and wpa2 key
const char *pass =  "Bax-358@-25a4X";
const char* server = "api.thingspeak.com";

float t_offset = -1.5;
 
//#define DHTPIN 0          //pin where the dht11 is connected
 
//DHT dht(DHTPIN, DHT11);
 
WiFiClient client;
 
Adafruit_AM2320 am2320 = Adafruit_AM2320();

void setup() 
{
      Serial.begin(9600);
       while (!Serial) {
        delay(10); // hang out until serial port opens
  }
       Serial.println("Connecting to ");
       Serial.println(ssid);
 
       WiFi.begin(ssid, pass);
 
      while (WiFi.status() != WL_CONNECTED) 
     {
            delay(500);
            Serial.print(".");
     }
      Serial.println("");
      Serial.println("WiFi connected");
      // Print wifi IP addess
     Serial.println("IP address: ");
     Serial.println(WiFi.localIP());

      Serial.println("Adafruit AM2320 Basic Test");
       am2320.begin();
 
}
 
void loop() 
{
  
      float h = am2320.readHumidity();
      float t = am2320.readTemperature();
          t += t_offset;

              if (isnan(h) || isnan(t)) 
                 {
                     Serial.println("Failed to read from sensor!");
                      delay(1000);
                      return;
                 }
 
                         if (client.connect(server,80))   //   "184.106.153.149" or api.thingspeak.com
                      {  
                            
                             String postStr = apiKey;
                             postStr +="&field1=";
                             postStr += String(t);
                             postStr +="&field2=";
                             postStr += String(h);
                             postStr += "\r\n\r\n";
 
                             client.print("POST /update HTTP/1.1\n");
                             client.print("Host: api.thingspeak.com\n");
                             client.print("Connection: close\n");
                             client.print("X-THINGSPEAKAPIKEY: "+apiKey+"\n");
                             client.print("Content-Type: application/x-www-form-urlencoded\n");
                             client.print("Content-Length: ");
                             client.print(postStr.length());
                             client.print("\n\n");
                             client.print(postStr);
 
                             Serial.print("Temperature: ");
                             Serial.print(t);
                             Serial.print(" degrees Celcius, Humidity: ");
                             Serial.print(h);
                             Serial.println("%. Send to Thingspeak.");
                        }
          client.stop();
 
          Serial.println("Waiting...");
  
  // thingspeak needs minimum 15 sec delay between updates

     Serial.print("Temp: "); Serial.println(am2320.readTemperature());
     Serial.print("Hum: "); Serial.println(am2320.readHumidity());

  delay(2000);
}