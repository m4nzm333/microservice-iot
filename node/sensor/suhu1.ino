/**
 *  Id      : suhu1
 *  Tipe    : sensor
 *  Model   : suhu
 */

// DHT Library
#include <DHT.h>
#define DHTPIN 5
#define DHTTYPE DHT11
// Wifi Library
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
WiFiClient espClient;
// MQTT Library
#include <PubSubClient.h>
PubSubClient client(espClient);

// Wifi
const char *ssid = "Putra-SmartHome";
const char *password = "12345678";
// MQTT Broker
const char *mqtt_broker = "192.168.100.1";
const char *topic = "suhu1";
const char *mqtt_username = "putra";
const char *mqtt_password = "123456";
const int mqtt_port = 1883;

DHT dht(DHTPIN, DHTTYPE);

void setup()
{
    Serial.begin(115200);
    // Sensor Begin
    dht.begin();
    // Wifi Begin
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Connected to WiFi");

    // Client MQTT Begin
    client.setServer(mqtt_broker, mqtt_port);
    while (!client.connected())
    {
        String client_id = "suhu1-";
        client_id += String(WiFi.macAddress());
        Serial.printf("The client %s connects to the mqtt broker\n", client_id.c_str());
        if (client.connect(client_id.c_str(), mqtt_username, mqtt_password))
        {
            Serial.println("My SmartHome MQTT Server connected");
        }
        else
        {
            Serial.printf("failed with state %d\n", client.state());
            delay(2000);
        }
    }
}

void loop()
{
    float newT = dht.readTemperature();
    if (!isnan(newT))
    {
        Serial.println(newT);
        client.publish(topic, String(newT).c_str(), true);
    }
    client.loop();
    delay(5000);
}