from time import sleep
from datetime import datetime
import requests
import os

print("===============")
print("Trigger Service")
print("===============\n")

while True:
    # Contoh scheduler berjalan di saat jam tertentu harian
    allTrigger = requests.get('http://api-trigger:8080/getAll')

    allTrigger = allTrigger.json()
    for trigger in allTrigger:
        idSensor = trigger['sensor']['id']
        sensorValue = trigger['sensorValue']
        idControl = trigger['control']['id']
        controlValue = trigger['controlValue']
        jenis = trigger['jenis']

        # Get Last Data
        lastData = requests.get(
            'http://api-sensor:8080/getLastDataById', params={"id": idSensor})
        lastData = lastData.json()

        control = requests.get(
            'http://api-control:8080/getById', params={"id": idControl})
        control = control.json()

        # If Last data Exist
        if lastData and control:

            if control['value'] != controlValue:
                # Toleransi last data sebesar 5 menit sebelumnya
                lastDataTime = datetime.strptime(
                    lastData['ts'], '%Y-%m-%d %H:%M:%S')
                now = datetime.now()

                if now > lastDataTime and ((now - lastDataTime).total_seconds() / 60.0 <= 5):
                    # Jika Jenis Lebih Dari
                    if jenis == 'more than' and lastData['value'] >= sensorValue:
                        print("Trigger {sensor} {currentValue} {jenis} {sensorData} set {control} to {controlValue}".format(
                            sensor=idSensor, currentValue=lastData['value'], jenis=jenis, sensorData=sensorValue, control=idControl, controlValue=controlValue))
                        requests.get('http://api-control:8080/setValue',
                                     params={'id': idControl, 'trigger': 'triggered', 'value': controlValue}, verify=False)
                    # Jika Jenis Sama Dengan
                    if jenis == 'equal' and lastData['value'] == sensorValue:
                        requests.get('http://api-control:8080/setValue',
                                     params={'id': idControl, 'trigger': 'triggered', 'value': controlValue}, verify=False)
                        print("Trigger {sensor} {currentValue} {jenis} {sensorData} set {control} to {controlValue}".format(
                            sensor=idSensor, currentValue=lastData['value'], jenis=jenis, sensorData=sensorValue, control=idControl, controlValue=controlValue))
                    # Jika Jenis Kurang Dari
                    if jenis == 'less than' and lastData['value'] <= sensorValue:
                        requests.get('http://api-control:8080/setValue',
                                     params={'id': idControl, 'trigger': 'triggered', 'value': controlValue}, verify=False)
                        print("Trigger {sensor} {currentValue} {jenis} {sensorData} set {control} to {controlValue}".format(
                            sensor=idSensor, currentValue=lastData['value'], jenis=jenis, sensorData=sensorValue, control=idControl, controlValue=controlValue))

    # Delay selama 5 detik
    sleep(5)
