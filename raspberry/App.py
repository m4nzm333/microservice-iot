import paho.mqtt.client as mqtt
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

sensorDataLast = {}
apiUrl = 'http://api.myiot.com'


def on_message(client, userdata, message):
    topic = message.topic
    payload = float(message.payload.decode("utf-8"))

    # Tampilkan di console
    print("\nData : Masuk {topic} => {payload}".format(topic=topic,
          payload=payload))

    topicArray = topic.split('/')

    # Cek jika key ada di dalam last data
    if topic in sensorDataLast.keys():
        # Cek jika data masih sama dengan yang dulu
        if sensorDataLast[topic] == payload:
            print("Data : !!! Warning !!! Value {topic} sama".format(
                topic=topic))
        else:
            topicArray = topic.split('/')
            # Cek jika data lengkap
            if len(topicArray) == 5:
                rumah = topicArray[1]
                tipe = topicArray[2]
                model = topicArray[3]
                idAlat = topicArray[4]
                print(tipe)

                # Ambil data perangkat dari database dan cek jika exist
                respond = requests.get(apiUrl + "/sensor/getById?",
                                       params={"id": idAlat}, verify=False).json()
                # Cek jika perangkat terdaftar
                if respond == []:
                    # Tambahkan perangkat ke database
                    print("Devices : Perangkat Tidak Ditemukan")

                # Simpan data ke database
                requests.post(apiUrl + "/sensor/insertData",
                              data={
                                  "id": idAlat,
                                  "value": payload,
                                  "model": model
                              }, verify=False)

    sensorDataLast[topic] = payload


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)


client = mqtt.Client(client_id="server-grab")
client.username_pw_set(username="putra", password="123456")

client.on_message = on_message
client.on_connect = on_connect

client.connect(host="192.168.137.2", port=1883)


client.loop_start()

client.subscribe("#")
time.sleep(30)

client.loop_stop()

while True:
    time.sleep(30)
