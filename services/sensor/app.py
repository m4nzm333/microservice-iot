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
    return 'Selamat Datang di API Sensor'


@app.route('/countAll')
def countSensorAll():
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
    myquery = {"jenis.tipe": "sensor"}
    mydoc = mycol.find(myquery, projection={"data": False, "_id": False})
    json_data = dumps(list(mydoc), indent=2)
    dataReturn = []
    for device in json.loads(json_data):
        print(device['jenis']['model'])
        myquery = {"idDevice": device['id']}
        mycol = mydb[device['jenis']['model']]
        mydoc = mycol.find(myquery, projection={
                           "data": False, "_id": False}).sort("ts", -1)
        lists = json.loads(dumps(list(mydoc)))
        if lists == []:
            device['last_data'] = []
        else:
            device['last_data'] = lists[0]
        dataReturn.append(device)
    return jsonify(dataReturn)


@app.route('/getById')
def getDevicessById():
    idDevice = request.args.get('id')
    mycol = mydb["devices"]
    myquery = {
        "jenis.tipe": "sensor",
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
@app.route('/insertData', methods=['POST'])
def insertData():
    idDevice = request.form.get('id')
    value = request.form.get('value')
    model = request.form.get('model')
    if idDevice:
        mycol = mydb[model]
        mycol.insert_one({
            '_id': ObjectId(),
            'value': value,
            'ts': datetime.utcnow(),
            'idDevice': idDevice
        })
        return 'success'
    else:
        return 'id missing'


@app.route('/getDataByDevice')
def getDataByDevice():
    try:
        idDevice = request.args.get('id')

        mycol = mydb["devices"]
        myquery = {
            "jenis.tipe": "sensor",
            "id": idDevice
        }
        mydoc = mycol.find(myquery, projection={"data": False, "_id": False})
        rowData = list(mydoc)
        if len(rowData) != 0:
            model = rowData[0]['jenis']['model']
            mycol = mydb[model]
            myquery = {
                "idDevice": idDevice,
            }
            mydoc = mycol.find(myquery, projection={"_id": False})
            mydata = list(mydoc)
            returnData = []
            for i in mydata:
                returnData.append({
                    'value': i.get('value'),
                    'ts': (i.get('ts') + timedelta(hours=+8)).strftime('%Y-%m-%d %H:%M:%S')
                })
                print(returnData)
            
            

            return jsonify(returnData)
        else:
            return jsonify(returnData)
    except:
        return jsonify([])


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


@app.route('/getLastById')
def getLastById():
    return jsonify([])


app.run(host='0.0.0.0', port=8080, debug=True)
