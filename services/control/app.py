from flask import Flask, jsonify, request
import pymongo
import json
from bson.json_util import dumps, loads
from bson import ObjectId
from datetime import timezone, datetime, timedelta
import os

app = Flask(__name__)

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
    return '<h2>Selamat Datang Di API Control</h2>'


# ===============
# CRUD Device
# ===============
@app.route('/devices/getAll')
def getDevicesAll():
    mycol = mydb["devices"]
    mydoc = mycol.find({
        "jenis.tipe": "control"
    }, projection={"_id": False})
    try:
        myData = list(mydoc)
        return jsonify(myData)
    except:
        return jsonify([])


@app.route('/devices/getById')
def getDevicessById():
    idDevice = request.args.get('id')
    mycol = mydb["devices"]
    mydoc = mycol.find_one({
        'jenis.tipe': 'control',
        'id': idDevice
    }, projection={"_id": False})
    try:
        return jsonify(mydoc)
    except:
        return jsonify([])

@app.route('/value')
def getValueById():
    idDevice = request.args.get('id')
    try:
        mycol = mydb["devices"]
        mydoc = mycol.find_one({
            'jenis.tipe': 'control',
            'id': idDevice
        }, projection={'_id' : False, "value": True})
        return jsonify(mydoc['value'])
    except:
        return jsonify(None)

# TODO: CRUD Devices

# ===============
# History
# ===============
@app.route('/setValue')
def setValue():
    idDevice = request.args.get('id')
    value = int(request.args.get('value'))
    trigger = request.args.get('trigger', 'manual')
    deviceCol = mydb['devices']
    historyCol = mydb['history']
    try:
        device = deviceCol.find_one({
            'jenis.tipe': 'control',
            'id': idDevice
        }, projection={"_id": False})
        deviceCol.update_one({
            'jenis.tipe': 'control',
            'id': idDevice
        }, {
            '$set': {
                'value': value
            }
        })
        historyCol.insert_one({
            'idDevice': idDevice,
            'ts': datetime.now(),
            'value': value,
            'trigger': trigger
        })
        return jsonify({'status': 'success'})
    except:
        return jsonify({'status': 'failed'})


@app.route('/getHistoryByDate')
def getHistoryByIdByDate():
    try:
        idDevice = request.args.get('id')
        date = request.args.get('date')
        dateStartObj = datetime.strptime(
            date + " 00:00:00", "%Y-%m-%d %H:%M:%S")
        dateEndObj = datetime.strptime(
            date + " 23:59:59", "%Y-%m-%d %H:%M:%S")

        historyCol = mydb['history']
        myCursor = historyCol.find({
            "idDevice": idDevice,
            'ts': {
                '$gte': dateStartObj,
                '$lte': dateEndObj
            }
        }, projection={'_id': False})

        dataReturn = []
        for x in list(myCursor):
            x['ts'] = x['ts'].strftime('%Y-%m-%d %H:%M:%S')
            dataReturn.append(x)

        return jsonify(dataReturn)
    except:
        return jsonify([])


app.run(host='0.0.0.0', port=8080, debug=True)
