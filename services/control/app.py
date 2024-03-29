from flask import Flask, jsonify, request
import pymongo
import json
from bson.json_util import dumps, loads
from bson import ObjectId
from datetime import timezone, datetime, timedelta
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Get environment variables
DB_HOSTNAME = os.getenv('DB_HOSTNAME', default='127.0.0.1')
DB_PORT = os.getenv('DB_PORT', default=27017)
DB_USERNAME = os.getenv('DB_USERNAME', default='root')
DB_PASSWORD = os.getenv('DB_PASSWORD', default='123456')
DB_NAME = os.getenv('DB_NAME', default='myiot')


myclient = pymongo.MongoClient("mongodb://{username}:{password}@{hostname}:{port}/".format(
    hostname=DB_HOSTNAME, port=DB_PORT, username=DB_USERNAME, password=DB_PASSWORD))
mydb = myclient[DB_NAME]


@app.route('/')
def index():
    return 'Selamat Datang di API Control'


@app.route('/countAll')
def countControlAll():
    mycol = mydb["devices"]
    myquery = {"type": "sensor"}
    mydoc = mycol.find(myquery, projection={"data": False, "_id": False})
    json_data = dumps(list(mydoc), indent=2)
    print(json_data)
    return jsonify({"count": len(json_data)})


# ===============
# CRUD Device
# ===============
@app.route('/getAll')
def getDevicesAll():
    mycol = mydb["devices"]
    myquery = {"jenis.tipe": "control"}
    mydoc = mycol.find(myquery, projection={"data": False, "_id": False})
    json_data = list(mydoc)
    return json_data


@app.route('/getById')
def getDevicesById():
    idDevice = request.args.get('id')
    mycol = mydb["devices"]
    myquery = {
        "jenis.tipe": "control",
        "id": idDevice
    }
    mydoc = mycol.find_one(myquery, projection={"_id": False})
    if mydoc:
        return mydoc
    else:
        jsonify([])


@app.route('/insertDevice', methods=['POST'])
def insertDevices():
    idDevice = request.form.get('id')
    nama = request.form.get('nama', idDevice)
    model = request.form.get('model')
    rumah = request.form.get('rumah', default='rumahku')
    value = request.form.get('value', default=0)

    mydict = {
        "id": idDevice,
        "jenis": {
            "tipe": 'control',
            "model": model,
            "metode": "saklar"
        },
        "nama": nama,
        "rumah": rumah,
        "value": value
    }
    mycol = mydb["devices"]
    mycol.insert_one(mydict)
    return 'success'


@app.route('/updateById', methods=['POST'])
def updateDeviceById():
    idDevice = request.form.get('id')
    nama = request.form.get('nama', idDevice)
    model = request.form.get('model')
    rumah = request.form.get('rumah', default='rumahku')
    value = request.form.get('value', default=0)

    mycol = mydb["devices"]
    myquery = {"id": idDevice}

    if (nama):
        newvalues = {"$set":  {
            "jenis": {
                "tipe": 'control',
                "model": model,
                "metode": "saklar"
            },
            "nama": nama,
            "rumah": rumah,
            "value": value
        }}
        mycol.update_one(myquery, newvalues)
    return 'success'


@app.route('/deleteById')
def deleteDeviceById():
    idDevice = request.args.get('id')
    myquery = {
        "id": idDevice
    }
    mycol = mydb["devices"]
    mycol.delete_one(myquery)
    return 'success'


# ===============
# Set Status Device
# ===============


@app.route('/toggle')
def toogleControlById():
    idDevice = request.args.get('id')
    trigger = request.args.get('trigger', default="manual")
    mycol = mydb["devices"]
    myquery = {
        "jenis.tipe": "control",
        "id": idDevice
    }
    mydoc = mycol.find_one(myquery, projection={"_id": False})
    if mydoc:
        if mydoc['value']:
            mydoc['value'] = 0
            newvalues = {"$set": {"value": mydoc['value']}}
            mycol.update_one(myquery, newvalues)
        else:
            mydoc['value'] = 1
            newvalues = {"$set": {"value": mydoc['value']}}
            mycol.update_one(myquery, newvalues)
        # Masukkan data history
        historyDict = {
            "idDevice": idDevice,
            "ts": datetime.now() + timedelta(hours=-8),
            "value": mydoc['value'],
            "trigger": trigger
        }
        historyCol = mydb["history"]
        historyCol.insert_one(historyDict)

        return mydoc
    else:
        return jsonify([])


@app.route('/setValue')
def setValueById():
    idDevice = request.args.get('id', '')
    trigger = request.args.get('trigger', default="manual")
    value = request.args.get('value', default=0)
    mycol = mydb["devices"]
    myquery = {
        "id": idDevice
    }
    mydoc = mycol.find_one(myquery, projection={"_id": False})
    if mydoc:
        newvalues = {"$set": {"value": value}}
        mycol.update_one(myquery, newvalues)
        mydoc = mycol.find_one(myquery, projection={"_id": False})

        # Masukkan data history
        historyDict = {
            "idDevice": idDevice,
            "ts": datetime.now() + timedelta(hours=-8),
            "value": value,
            "trigger": trigger
        }
        historyCol = mydb["history"]
        historyCol.insert_one(historyDict)

        return dumps(mydoc)
    else:
        return jsonify([])

# ===============
# Data History Control
# ===============


@app.route('/getHistoryByIdDate')
def getHistoryByIdDate():
    idDevice = request.args.get('id')
    date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))

    dateStartObj = datetime.strptime(
        date + " 00:00:00", "%Y-%m-%d %H:%M:%S") - timedelta(hours=8)
    dateEndObj = datetime.strptime(
        date + " 23:59:59", "%Y-%m-%d %H:%M:%S") - timedelta(hours=8)

    myquery = {
        "idDevice": idDevice,
        'ts': {
            '$gte': dateStartObj,
            '$lte': dateEndObj
        }
    }
    mycol = mydb["history"]
    mydoc = mycol.find(myquery, projection={"_id": False})
    mydoc = list(mydoc)

    if mydoc:
        dataReturn = []
        for x in mydoc:
            x['ts'] = (x['ts'] + timedelta(hours=8)
                       ).strftime("%Y-%m-%d %H:%M:%S")
            dataReturn.append(x)

        return jsonify(mydoc)
    else:
        return jsonify([])


app.run(host='0.0.0.0', port=8080, debug=True)
