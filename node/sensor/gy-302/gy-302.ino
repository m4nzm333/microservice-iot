/**
 *  Id      : suhu1, kelembapan1
 *  Tipe    : sensor
 *  Model   : suhu, kelembapan
 */

// Light Meter Library
#include <BH1750.h>
#include <Wire.h>

// Wifi Library
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
WiFiClient espClient;
// MQTT Library
#include <PubSubClient.h>
PubSubClient client(espClient);

// PIN LIGHT METER
#define PIN_SDA 4
#define PIN_SCL 5
BH1750 lightMeter(0x5C);
// Identitas Perangkat
const char *rumah = "rumahku";
const char *idAlat = "cahaya1";
const char *model = "cahaya";
const char *tipe = "sensor";

// Wifi
const char *ssid = "Putra-SmartHome";
const char *password = "12345678";
// MQTT Broker
const char *mqtt_broker = "192.168.100.1";
const char *mqtt_username = "putra";
const char *mqtt_password = "123456";
const int mqtt_port = 1883;
char topic[80];

void setup()
{
    // Init Serial
    Serial.begin(115200);
    // Sensor Begin
    Wire.begin(PIN_SDA, PIN_SCL);
    lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE);
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
    // Susun Topic
    sprintf(topic, "/%s/%s/%s/%s", rumah, tipe, model, idAlat);
    // Client MQTT Begin
    client.setServer(mqtt_broker, mqtt_port);
    while (!client.connected())
    {
        String client_id = "suhu1-";
        client_id += String(WiFi.macAddress());
        Serial.printf("Mencoba koneksi ke Broker menggunakan id %s \n", client_id.c_str());
        if (client.connect(client_id.c_str(), mqtt_username, mqtt_password))
        {
            Serial.println("Broker terhubung . . .");
        }
        else
        {
            Serial.printf("Gagal koneksi broker, Status Code = %d\n", client.state());
            delay(2000);
        }
    }
}

void loop()
{
    // Deteksi Temperatur dan kirim ke MQTT
    float cahayaValue = 0;
    if (lightMeter.measurementReady())
    {
        cahayaValue = lightMeter.readLightLevel();
        Serial.println(cahayaValue);
        client.publish(topic, String(cahayaValue).c_str(), true);
    }
    client.loop();
    delay(10000);
}