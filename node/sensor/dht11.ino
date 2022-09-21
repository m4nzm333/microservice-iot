/**
 *  Id      : suhu1, kelembapan1
 *  Tipe    : sensor
 *  Model   : suhu, kelembapan
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

// DHT11
DHT dht(DHTPIN, DHTTYPE);

// Identitas Perangkat
const char *rumah = "rumahku";
const char *idAlatTemp = "suhu1";
const char *idAlatHum = "kelembapan1";
const char *modelTemp = "suhu";
const char *modelHum = "kelembapan";
const char *tipe = "sensor";

// Wifi
const char *ssid = "Putra-SmartHome";
const char *password = "12345678";
// MQTT Broker
const char *mqtt_broker = "192.168.100.1";
const char *mqtt_username = "putra";
const char *mqtt_password = "123456";
const int mqtt_port = 1883;
char topicTemp[80];
char topicHum[80];

void setup()
{
    // Init Serial
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
    // Susun Topic
    sprintf(topicTemp, "/%s/%s/%s/%s", rumah, tipe, modelTemp, idAlatTemp);
    sprintf(topicHum, "/%s/%s/%s/%s", rumah, tipe, modelHum, idAlatHum);
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
    float newT = dht.readTemperature();
    if (!isnan(newT))
    {
        Serial.println(newT);
        client.publish(topicTemp, String(newT).c_str(), true);
    }
    // Deteksi Kelembapan dan kirim ke MQTT
    float newH = dht.readHumidity();
    if (!isnan(newH))
    {
        Serial.println(newH);
        client.publish(topicHum, String(newH).c_str(), true);
    }

    client.loop();
    delay(5000);
}