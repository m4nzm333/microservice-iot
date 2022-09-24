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
    returnData = []
    for device in json_data:
        historyCol = mydb["history"]
        historyQuery = {"idDevice": device["id"]}
        historyDoc = historyCol.find_one(
            historyQuery, projection={"_id": False}, sort=[("ts", -1)])
        historyReturn = historyDoc
        historyReturn["ts"] = (historyReturn.get(
            'ts') + timedelta(hours=+8)).strftime('%Y-%m-%d %H:%M:%S')
        device['last_history'] = json.loads(json.dumps(historyDoc, indent=4, sort_keys=True, default=str))
        returnData.append(device)
    return returnData


@app.route('/getById')
def getDevicesById():
    idDevice = request.args.get('id')
    mycol = mydb["devices"]
    myquery = {
        "jenis.tipe": "control",
        "id": idDevice
    }
    mydoc = mycol.find(myquery, projection={"data": False, "_id": False})
    rowData = list(mydoc)
    if rowData:
        json_data = dumps(rowData[0], indent=2)
        print(json_data)
        return json_data
    else:
        return jsonify([])


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
    mydoc = mycol.find(myquery, projection={"data": False, "_id": False})
    rowData = list(mydoc)
    print(rowData)
    if rowData:
        json_data = dumps(rowData[0], indent=2)
        # print(json_data.value)
        json_data = json.loads(json_data)
        value = 0
        if json_data['value'] == 1:
            value = 0
            newvalues = {"$set": {"value": value}}
            mycol.update_one(myquery, newvalues)
        else:
            value = 1
            newvalues = {"$set": {"value": value}}
            mycol.update_one(myquery, newvalues)
        # Masukkan trigger
        if trigger == 'scheduled':

            mydict = {
                "idDevice": idDevice,
                "ts": datetime.now(),
                "value": value,
                "trigger": trigger
            }
            mycol = mydb["history"]
            mycol.insert_one(mydict)
        else:
            trigger = 'manual'
            mydict = {
                "idDevice": idDevice,
                "ts": datetime.now(),
                "value": value,
                "trigger": trigger
            }
            mycol = mydb["history"]
            mycol.insert_one(mydict)

        return json_data
    else:
        return jsonify([])


app.run(host='0.0.0.0', port=8080, debug=True)
