print("===============")
print("Trigger Service")
print("===============\n")

from time import sleep
from datetime import datetime
import json
import requests

while True:
    print('Ini adalah scheduler')

    # Contoh scheduler berjalan di saat jam tertentu harian

    allScheduler = requests.get('http://api-scheduler:8080/getAll')
    # # allScheduler = requests.get('http://api.myiot.com/scheduler/getAll')

    allScheduler = allScheduler.json()

    for schedule in allScheduler:

        if schedule['jenis']['tipe'] == 'harian':
            print(schedule)

            timeTrigger = schedule['jenis']['jam']
            idDevice = schedule['control']['id']
            value = schedule['value']

            now = datetime.now()
            print(now)
            trigger = datetime.strptime('{} {}'.format(
                now.strftime("%Y-%m-%d"), timeTrigger), "%Y-%m-%d %H:%M")

            # TODO: Cek history

            # Toleransi schedule di bawah 5 menit
            if now > trigger and ((now - trigger).total_seconds() / 60.0 <= 5):
                print('set new status {control} to = {value}'.format(
                    control=schedule['control']['nama'], value=schedule['value']))
                print(idDevice)

                requests.get('http://api-control:8080/setValue',
                             params={'id': idDevice, 'trigger': 'scheduled', 'value': schedule['value']}, verify=False)
    sleep(5)
