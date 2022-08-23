from flask import Flask, jsonify, request
import pymongo
import json
from bson.json_util import dumps, loads

app = Flask(__name__)

host = '127.0.0.1:27017'

myclient = pymongo.MongoClient(
    "mongodb://root:123456@{host}/".format(host=host))
mydb = myclient["myiot"]


@app.route('/')
def index():
    return 'Selamat datang di api asap'


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


app.run(host='0.0.0.0', port=8080, debug=True)
