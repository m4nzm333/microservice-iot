from time import sleep
from datetime import datetime
import pymongo
import requests

while True:
    print('Ini adalah scheduler')
    # Contoh scheduler berjalan di saat jam tertentu harian
    timeTrigger = "19:55"
    idDevice = 'lampu1'

    now = datetime.now()
    trigger = datetime.strptime('{} {}'.format(
        now.strftime("%Y-%m-%d"), timeTrigger), "%Y-%m-%d %H:%M")

    print(trigger)
    print(now)
    if now > trigger and ((now - trigger).total_seconds() / 60.0 <= 5):
        print('update')
        requests.get('http://api.myiot.com/control/toggle',
                     params={'id': idDevice, 'trigger': 'scheduled'}, verify=False)
    sleep(5)
