#include <OneWire.h> 
#include <DallasTemperature.h>
#include "DHT.h"

// External Temp & Humidity
#define DHT_PIN 8
#define DHTTYPE DHT11
// Internal Temp
#define ONE_WIRE_BUS 22
// Sound
#define SOUND_SENSOR_PIN 19 


OneWire oneWire(ONE_WIRE_BUS); 
DallasTemperature sensors(&oneWire);

DHT dht(DHT_PIN, DHTTYPE); 

unsigned long last_time;
unsigned long last_ext_temp_time;
unsigned long last_bubulle_time;
unsigned long current_time;
const unsigned long ext_temp_period = 10 * 1000;
const unsigned long temp_period = 10 * 1000;
const unsigned long bubulle_period =  5;

void setup(void) 
{ 
  pinMode(SOUND_SENSOR_PIN, INPUT);
  // start serial port 
  Serial.begin(9600); 
  // Start up the library 
  last_time = millis();
  last_bubulle_time = last_time;
  last_ext_temp_time = last_time;
  
  // start sensors
  sensors.begin(); 
  dht.begin();
} 


void loop(void) 
{ 
  current_time = millis();

  // read & send temp every 5 ms
  if (current_time - last_bubulle_time >= bubulle_period) {
    last_bubulle_time = current_time;
    if (digitalRead(SOUND_SENSOR_PIN)) {
      Serial.println("{ \"bubulle\" : 1 }");
    }      
  }

  // read & send temp every 10 sec
  if (current_time - last_time >= temp_period) {
    last_time = current_time;
    sensors.requestTemperatures(); // Send the command to get temperature readings 
    float temp = sensors.getTempCByIndex(0);
    Serial.println("{ \"temp\" : " + String(temp) + " }");
  }

  if (current_time - last_ext_temp_time >= ext_temp_period) {
    last_ext_temp_time = current_time;
    float ext_humidity = dht.readHumidity();
    float ext_temperature = dht.readTemperature();
    Serial.println("{ \"ext_temp\" : " + String(ext_temperature) + ", \"ext_humidity\" : " + String(ext_humidity) + " }");
  }

  //delay(30);
} 
