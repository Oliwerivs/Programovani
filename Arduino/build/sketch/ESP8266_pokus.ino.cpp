#include <Arduino.h>
#line 1 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino"
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <Wire.h>
#include <BH1750.h>
//#include <Adafruit_SleepyDog.h>

/*Put your SSID & Password*/
const char* ssid = "Domus";  // Enter SSID here
//const char* corpassrect_password = "Bax-358@-25a4X";  Enter Password here
const char* password = "vojnuvmestec22";

// Variables to store the current and previous time
unsigned long previousMillis = 0;
const long interval = 10000; // Blink interval in milliseconds (1 second)

ESP8266WebServer server(80);

uint8_t LED1pin = D7;
bool LED1status = LOW;

uint8_t LED2pin = D6;
bool LED2status = LOW;

BH1750 lightMeter;


#line 27 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino"
void setup();
#line 84 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino"
void loop();
#line 110 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino"
void handle_OnConnect();
#line 117 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino"
void handle_led1on();
#line 124 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino"
void handle_led1off();
#line 130 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino"
void handle_led2on();
#line 136 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino"
void handle_led2off();
#line 142 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino"
void handle_NotFound();
#line 146 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino"
String SendHTML(uint8_t led1stat,uint8_t led2stat);
#line 27 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino"
void setup() {
  Serial.begin(9600);
  Wire.begin();
  delay(100);
  pinMode(LED1pin, OUTPUT);
  pinMode(LED2pin, OUTPUT);
 /*  // Pokus o login od uzivatele--------------------------
  Serial.println("Zadej SSID:");
  while (Serial.available() == 0){}  // Ceka na data
  String ssid = Serial.readStringUntil('\n');
  ssid.trim();

  Serial.println("Zadej heslo:");
  while (Serial.available() == 0){}  // Ceka na data
  String password_temp = Serial.readStringUntil('\n');
  password_temp.trim();
  if (password_temp.equals(correct_password)){
    Serial.println("Spravne heslo."); 
    String password = password_temp;

  } else {
    Serial.println("Spatne heslo. Sorry jako!");
  }
*/

  //------------------------------------------------------
  Serial.println("Connecting to ");
  Serial.println(ssid);

  //connect to your local wi-fi network
  WiFi.begin(ssid,password);

  //check wi-fi is connected to wi-fi network
  while (WiFi.status() != WL_CONNECTED) {
  delay(1000);
  Serial.print(".");
 
  }
  Serial.println("");
  Serial.println("WiFi connected..!");
  Serial.print("Got IP: ");  Serial.println(WiFi.localIP());

  server.on("/", handle_OnConnect);
  server.on("/led1on", handle_led1on);
  server.on("/led1off", handle_led1off);
  server.on("/led2on", handle_led2on);
  server.on("/led2off", handle_led2off);
  server.onNotFound(handle_NotFound);

  server.begin();
  Serial.println("HTTP server started");

  lightMeter.begin();

  Serial.println(F("BH1750 Test begin"));

}
void loop() {
// WebSerial.println("Hello!");
  delay(2000);
// LUX sensor part ----------------------------
unsigned long currentMillis = millis();
if (currentMillis-previousMillis >= interval){
  float lux = lightMeter.readLightLevel();
  Serial.print("Light: ");
  Serial.print(lux);
  Serial.println(" lx");
  previousMillis = currentMillis;
  }  
//----------------------------------------------

  server.handleClient();
  if(LED1status)
  {digitalWrite(LED1pin, HIGH);}
  else
  {digitalWrite(LED1pin, LOW);}
  
  if(LED2status)
  {digitalWrite(LED2pin, HIGH);}
  else
  {digitalWrite(LED2pin, LOW);}
}

void handle_OnConnect() {
  LED1status = LOW;
  LED2status = LOW;
  Serial.println("GPIO7 Status: OFF | GPIO6 Status: OFF");
  server.send(200, "text/html", SendHTML(LED1status,LED2status)); 
}

void handle_led1on() {
  LED1status = HIGH;
  Serial.println("GPIO7 Status: ON");
  server.send(200, "text/html", SendHTML(true,LED2status)); 
 
}

void handle_led1off() {
  LED1status = LOW;
  Serial.println("GPIO7 Status: OFF");
  server.send(200, "text/html", SendHTML(false,LED2status)); 
}

void handle_led2on() {
  LED2status = HIGH;
  Serial.println("GPIO6 Status: ON");
  server.send(200, "text/html", SendHTML(LED1status,true)); 
}

void handle_led2off() {
  LED2status = LOW;
  Serial.println("GPIO6 Status: OFF");
  server.send(200, "text/html", SendHTML(LED1status,false)); 
}

void handle_NotFound(){
  server.send(404, "text/plain", "Not found");
}

String SendHTML(uint8_t led1stat,uint8_t led2stat){
  String ptr = "<!DOCTYPE html> <html>\n";
  ptr +="<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0, user-scalable=no\">\n";
  ptr +="<title>LED Control</title>\n";
  ptr +="<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}\n";
  ptr +="body{margin-top: 50px;} h1 {color: #444444;margin: 50px auto 30px;} h3 {color: #444444;margin-bottom: 50px;}\n";
  ptr +=".button {display: block;width: 80px;background-color: #1abc9c;border: none;color: white;padding: 13px 30px;text-decoration: none;font-size: 25px;margin: 0px auto 35px;cursor: pointer;border-radius: 4px;}\n";
  ptr +=".button-on {background-color: #1abc9c;}\n";
  ptr +=".button-on:active {background-color: #16a085;}\n";
  ptr +=".button-off {background-color: #34495e;}\n";
  ptr +=".button-off:active {background-color: #2c3e50;}\n";
  ptr +="p {font-size: 14px;color: #888;margin-bottom: 10px;}\n";
  ptr +="</style>\n";
  ptr +="</head>\n";
  ptr +="<body>\n";
  ptr +="<h1>ESP8266 Web Server,blikani LEDek</h1>\n";
    ptr +="<h3>Using Station(STA) Mode</h3>\n";
  
   if(led1stat)
  {ptr +="<p>LED1 Status: ON</p><a class=\"button button-off\" href=\"/led1off\">OFF</a>\n";}
  else
  {ptr +="<p>LED1 Status: OFF</p><a class=\"button button-on\" href=\"/led1on\">ON</a>\n";}

  if(led2stat)
  {ptr +="<p>LED2 Status: ON</p><a class=\"button button-off\" href=\"/led2off\">OFF</a>\n";}
  else
  {ptr +="<p>LED2 Status: OFF</p><a class=\"button button-on\" href=\"/led2on\">ON</a>\n";}

  ptr +="</body>\n";
  ptr +="</html>\n";
  return ptr;
}
