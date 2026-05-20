# 1 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino"
# 2 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino" 2
# 3 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino" 2
# 4 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino" 2
# 5 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino" 2
//#include <Adafruit_SleepyDog.h>

/*Put your SSID & Password*/
const char* ssid = "Domus"; // Enter SSID here
//const char* corpassrect_password = "Bax-358@-25a4X";  Enter Password here
const char* password = "vojnuvmestec22";

// Variables to store the current and previous time
unsigned long previousMillis = 0;
const long interval = 10000; // Blink interval in milliseconds (1 second)

ESP8266WebServer server(80);

uint8_t LED1pin = D7;
bool LED1status = 0x0;

uint8_t LED2pin = D6;
bool LED2status = 0x0;

BH1750 lightMeter;


void setup() {
  Serial.begin(9600);
  Wire.begin();
  delay(100);
  pinMode(LED1pin, 0x01);
  pinMode(LED2pin, 0x01);
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
  Serial.print("Got IP: "); Serial.println(WiFi.localIP());

  server.on("/", handle_OnConnect);
  server.on("/led1on", handle_led1on);
  server.on("/led1off", handle_led1off);
  server.on("/led2on", handle_led2on);
  server.on("/led2off", handle_led2off);
  server.onNotFound(handle_NotFound);

  server.begin();
  Serial.println("HTTP server started");

  lightMeter.begin();

  Serial.println(((reinterpret_cast<const __FlashStringHelper *>(
# 81 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino" 3
                (__extension__({static const char __pstr__[] __attribute__((__aligned__(4))) __attribute__((section( "\".irom0.pstr." "ESP8266_pokus.ino" "." "81" "." "122" "\", \"aSM\", @progbits, 1 #"))) = (
# 81 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino"
                "BH1750 Test begin"
# 81 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino" 3
                ); &__pstr__[0];}))
# 81 "C:\\Users\\oldab\\OneDrive\\Documents\\Arduino\\ESP8266_pokus\\ESP8266_pokus.ino"
                ))));

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
  {digitalWrite(LED1pin, 0x1);}
  else
  {digitalWrite(LED1pin, 0x0);}

  if(LED2status)
  {digitalWrite(LED2pin, 0x1);}
  else
  {digitalWrite(LED2pin, 0x0);}
}

void handle_OnConnect() {
  LED1status = 0x0;
  LED2status = 0x0;
  Serial.println("GPIO7 Status: OFF | GPIO6 Status: OFF");
  server.send(200, "text/html", SendHTML(LED1status,LED2status));
}

void handle_led1on() {
  LED1status = 0x1;
  Serial.println("GPIO7 Status: ON");
  server.send(200, "text/html", SendHTML(true,LED2status));

}

void handle_led1off() {
  LED1status = 0x0;
  Serial.println("GPIO7 Status: OFF");
  server.send(200, "text/html", SendHTML(false,LED2status));
}

void handle_led2on() {
  LED2status = 0x1;
  Serial.println("GPIO6 Status: ON");
  server.send(200, "text/html", SendHTML(LED1status,true));
}

void handle_led2off() {
  LED2status = 0x0;
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
