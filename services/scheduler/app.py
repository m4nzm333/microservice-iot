from time import sleep
from datetime import datetime
import pymongo
import requests

while True:
    print('Ini adalah scheduler')
    # Contoh scheduler berjalan di saat jam tertentu harian
    allScheduler = requests.get('http://api.myiot.com/scheduler/getAll')

    allScheduler = allScheduler.json()

    for schedule in allScheduler:

        if schedule['jenis']['tipe'] == 'harian':

            timeTrigger = schedule['jenis']['jam']
            idDevice = schedule['control']['id']
            value = schedule['value']

            now = datetime.now()
            trigger = datetime.strptime('{} {}'.format(
                now.strftime("%Y-%m-%d"), timeTrigger), "%Y-%m-%d %H:%M")

            # TODO: Cek history

            # Toleransi schedule di bawah 5 menit
            if now > trigger and ((now - trigger).total_seconds() / 60.0 <= 5):
                print('set new status to = {value}'.format(
                    value=schedule['value']))

                requests.get('http://api.myiot.com/control/setValue',
                             params={'id': idDevice, 'trigger': 'scheduled', 'value': schedule['value']}, verify=False)
    sleep(5)
