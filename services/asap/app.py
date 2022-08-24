from flask import Flask, jsonify, request
import pymongo
import json
from bson.json_util import dumps, loads
from bson import ObjectId
from datetime import timezone, datetime, timedelta

app = Flask(__name__)

host = '127.0.0.1:27017'

myclient = pymongo.MongoClient(
    "mongodb://root:123456@{host}/".format(host=host))
mydb = myclient["myiot"]


@app.route('/')
def index():
    return 'Selamat datang di api asap'


# ===============
# CRUD Device
# ===============
@app.route('/devices/getAll')
def getDevicesAll():
    mycol = mydb["devices"]
    myquery = {"jenis": "sensor_asap"}
    mydoc = mycol.find(myquery, projection={"data": False, "_id": False})
    json_data = dumps(list(mydoc), indent=2)
    print(json_data)
    return jsonify(json.loads(json_data))


@app.route('/devices/getById')
def getDevicessById():
    idDevice = request.args.get('id')
    mycol = mydb["devices"]
    myquery = {
        "jenis": "sensor_asap",
        "id": idDevice
    }
    mydoc = mycol.find(myquery, projection={"data": False, "_id": False})
    rowData = list(mydoc)
    if rowData:
        json_data = dumps(rowData[0], indent=2)
        print(json_data)
        return jsonify(json.loads(json_data))
    else:
        return jsonify([])


@app.route('/devices/insert', methods=['POST'])
def insertDevices():
    idDevice = request.form.get('id')
    jenis = 'sensor_asap'
    nama = request.form.get('nama')
    rumah = request.form.get('rumah')

    mydict = {
        "id": idDevice,
        "jenis": jenis,
        "nama": nama,
        "rumah": rumah
    }
    mycol = mydb["devices"]
    mycol.insert_one(mydict)
    return 'success'


@app.route('/devices/update', methods=['POST'])
def updateDeviceById():
    idDevice = request.form.get('id')
    nama = request.form.get('nama')
    rumah = request.form.get('rumah')

    mycol = mydb["devices"]
    myquery = {
        "jenis": "sensor_asap",
        "id": idDevice
    }

    if (nama):
        newvalues = {"$set": {"nama": nama}}
        mycol.update_one(myquery, newvalues)
    if (rumah):
        newvalues = {"$set": {"rumah": rumah}}
        mycol.update_one(myquery, newvalues)
    return 'success'


@app.route('/devices/delete')
def deleteDeviceById():
    idDevice = request.args.get('id')
    myquery = {
        "id": idDevice
    }
    mycol = mydb["devices"]
    mycol.delete_one(myquery)
    return 'success'


# ===============
# Data
# ===============
@app.route('/data/insert', methods=['POST'])
def insertData():
    idDevice = request.form.get('id')
    value = request.form.get('value')
    if idDevice:
        mycol = mydb["asap"]
        mycol.insert_one({
            '_id': ObjectId(),
            'value': value,
            'ts': datetime.utcnow(),
            'idDevice': idDevice
        })
        return 'success'
    else:
        return 'id missing'


@app.route('/data/getByDate')
def getByDate():
    try:
        idDevice = request.args.get('id')
        date = request.args.get('date')
        dateStartObj = datetime.strptime(
            date + " 00:00:00", "%Y-%m-%d %H:%M:%S") - timedelta(hours=8)
        dateEndObj = datetime.strptime(
            date + " 23:59:59", "%Y-%m-%d %H:%M:%S") - timedelta(hours=8)

        if idDevice or date:
            mycol = mydb["asap"]

            myquery = {
                "idDevice": idDevice,
                'ts': {
                    '$gte': dateStartObj,
                    '$lte': dateEndObj
                }
            }
            mydoc = mycol.find(myquery)
            mydata = list(mydoc)
            returnData = []

            for i in mydata:
                returnData.append({
                    'value': i.get('value'),
                    'ts': (i.get('ts') + timedelta(hours=+8)).strftime('%Y-%m-%d %H:%M:%S')
                })
            print(returnData)
            return jsonify(returnData)
    except:
        return jsonify([])


app.run(host='0.0.0.0', port=8080, debug=True)
