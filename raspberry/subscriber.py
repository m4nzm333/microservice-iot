"""
    Ini adalah program untuk mengambil semua data dari topic MQTT Sensor 
    dengan cara subscribe kemudian mengirim data ke server menggunakna HTTP
"""
import paho.mqtt.client as mqtt
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Alamat API
apiUrl = 'http://api.myiot.com'

"""
 Fungsi ketika terdapat data pada topic
"""


def on_message(client, userdata, message):
    topic = message.topic
    payload = float(message.payload.decode("utf-8"))

    # Tampilkan di console
    print("\nData : Masuk {topic} => {payload}".format(topic=topic,
          payload=payload))

    topicArray = topic.split('/')

    # Cek jika data lengkap
    if len(topicArray) == 5:
        rumah = topicArray[1]
        tipe = topicArray[2]
        model = topicArray[3]
        idAlat = topicArray[4]

        # Jika tipe adalah sensor
        if tipe == 'sensor':
            # Ambil data perangkat dari database dan cek jika exist
            respond = requests.get(apiUrl + "/sensor/getById?",
                                   params={"id": idAlat}, verify=False).json()
            # Cek jika perangkat terdaftar
            if respond == []:
                # Tambahkan perangkat ke database
                requests.post(apiUrl + "/sensor/insertDevice",
                              data={
                                  "id": idAlat,
                                  "model": model,
                                  "rumah": rumah
                              }, verify=False)
                print("Devices : Perangkat Tidak Ditemukan")

            # Simpan data ke database
            requests.post(apiUrl + "/sensor/insertData",
                          data={
                              "id": idAlat,
                              "value": payload,
                              "model": model
                          }, verify=False)


"""
 Fungsi ketika koneksi berhasil
"""


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe("#")
    else:
        print("Failed to connect, return code %d\n", rc)


# Memulai koneksi
client = mqtt.Client(client_id="raspi-subscriber")
client.username_pw_set(username="putra", password="123456")

client.on_message = on_message
client.on_connect = on_connect

client.connect(host="192.168.100.1", port=1883)

client.loop_forever()
