/**
 *  Id      : lampu1
 *  Tipe    : control
 *  Model   : saklar
 */

// Wifi Library
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
WiFiClient espClient;
// MQTT Library
#include <PubSubClient.h>
PubSubClient client(espClient);
// PIN Perangkat
#define PIN_LAMPU 0
// Identitas Perangkat
const char *rumah = "rumahku";
const char *idAlatLampu = "lampu1";
const char *model = "lampu";
const char *tipe = "control";

// Wifi
const char *ssid = "Putra-SmartHome";
const char *password = "12345678";

// MQTT Broker
const char *mqtt_broker = "192.168.100.1";
const char *mqtt_username = "putra";
const char *mqtt_password = "123456";
const int mqtt_port = 1883;
char topicLampu[50];

// Ketika terdapat pesan subscribe
void callback(char *topic, byte *payload, unsigned int length)
{
    payload[length] = '\0';
    int value = String((char *)payload).toInt();

    Serial.println(topic);
    Serial.println(value);
    if(value == 1){
        digitalWrite(PIN_LAMPU, LOW);
    } else {
        digitalWrite(PIN_LAMPU, HIGH);
    }
}

void setup()
{
    // Init Serial
    Serial.begin(115200);
    // Pin Mode
    pinMode(PIN_LAMPU, OUTPUT);
    // Wifi Begin
    Serial.printf("Connecting to %s \n", ssid);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Connected to WiFi");
    // Susun Topic
    sprintf(topicLampu, "/%s/%s/%s/%s", rumah, tipe, model, idAlatLampu);
    // Client MQTT Begin
    client.setServer(mqtt_broker, mqtt_port);
    while (!client.connected())
    {
        String client_id = "saklar2-";
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
    client.setCallback(callback);
    client.subscribe(topicLampu);
}

void loop()
{
    // TODO: Reconnect ke broker jika koneksi terputus
    client.loop();
}
