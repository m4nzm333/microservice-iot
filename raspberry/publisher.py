"""
    Ini adalah program untuk mengambil data control dari server
    menggunakan HTTP kemudian melakukan publish status yang nantinya
    diambil oleh perangkat control melalui MQTT
"""
import paho.mqtt.client as mqtt
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Alamat API
apiUrl = 'http://api.myiot.com'


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)


client = mqtt.Client(client_id="raspi-publisher")
client.username_pw_set(username="putra", password="123456")

client.on_connect = on_connect

client.connect(host="192.168.100.1", port=1883)

while True:
    # Ambil data control
    respond = requests.get(apiUrl + "/control/getAll")

    for device in respond.json(): 
        idDevice = device['id']
        rumah = device['rumah']
        tipe = 'control'
        model = device['jenis']['model']
        value = device['value']
        # Bikin string topic
        topic = '/{rumah}/{tipe}/{model}/{idAlat}'.format(rumah=rumah, tipe=tipe, model=model, idAlat=idDevice)
        client.publish(topic, value)
        print('Publish {topic} => {value}'.format(topic=topic, value=value))

    # Delay 3 detik
    time.sleep(3)
