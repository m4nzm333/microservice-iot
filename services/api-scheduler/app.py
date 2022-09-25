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
    return 'Selamat Datang di API Scheduler'


@app.route('/countAll')
def countSchedulerAll():
    mycol = mydb["scheduler"]
    mydoc = mycol.find(projection={"data": False, "_id": False})
    json_data = dumps(list(mydoc), indent=2)
    print(json_data)
    return jsonify({"count": len(json_data)})


# ===============
# CRUD Jadwal
# ===============
@app.route('/getAll')
def getSchedulerAll():
    mycol = mydb["scheduler"]
    mydoc = mycol.find(projection={"_id": False})
    json_data = dumps(list(mydoc), indent=2)
    json_data = json.loads(json_data)
    returnData = []
    for schedule in json_data:
        controlCol = mydb["devices"]
        controlQuery = {
            "jenis.tipe": "control",
            "id": schedule['control']
        }
        controlDoc = controlCol.find(controlQuery, projection={
                                     "_id": False, "rumah": False, "value": False})
        rowData = list(controlDoc)
        if rowData:
            schedule['control'] = rowData[0]
        else:
            schedule['control'] = {}
        returnData.append(schedule)

    return jsonify(returnData)


@app.route('/getById')
def getSchedulerById():
    idJadwal = request.args.get('id')
    mycol = mydb["scheduler"]
    myquery = {
        "id": idJadwal
    }
    mydoc = mycol.find_one(myquery, projection={"_id": False})
    if mydoc:
        return mydoc
    else:
        return jsonify([])


@app.route('/insert', methods=['POST'])
def insertScheduler():
    idJadwal = request.form.get('id')
    nama = request.form.get('nama', idJadwal)
    control = request.form.get('control')
    rumah = request.form.get('rumah', default='rumahku')
    value = request.form.get('value', default=0)
    jamHarian = request.form.get('jamHarian', default="00:00")

    mydict = {
        "id": idJadwal,
        "jenis": {
            "tipe": 'harian',
            "jam": jamHarian,
        },
        "nama": nama,
        "rumah": rumah,
        "control": control,
        "value": value
    }
    mycol = mydb["scheduler"]
    mycol.insert_one(mydict)
    return 'success'


@app.route('/updateById', methods=['POST'])
def updateSchedulerById():
    idJadwal = request.form.get('id')
    nama = request.form.get('nama', idJadwal)
    control = request.form.get('control')
    rumah = request.form.get('rumah', default='rumahku')
    value = request.form.get('value', default=0)
    jamHarian = request.form.get('jamHarian', default="00:00")

    mycol = mydb["scheduler"]
    myquery = {"id": idJadwal}
    
    newvalues = {"$set":  {
        "jenis": {
            "tipe": 'harian',
            "jam": jamHarian,
        },
        "nama": nama,
        "rumah": rumah,
        "control": control,
        "value": value
    }}
    mycol.update_one(myquery, newvalues)
    return 'success'


@app.route('/deleteById')
def deleteDeviceById():
    idJadwal = request.args.get('id')
    myquery = {
        "id": idJadwal
    }
    mycol = mydb["scheduler"]
    mycol.delete_one(myquery)
    return 'success'

app.run(host='0.0.0.0', port=8080, debug=True)
