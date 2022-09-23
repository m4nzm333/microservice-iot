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
def countControlAll():
    mycol = mydb["scheduler"]
    mydoc = mycol.find(projection={"data": False, "_id": False})
    json_data = dumps(list(mydoc), indent=2)
    print(json_data)
    return jsonify({"count": len(json_data)})


# ===============
# CRUD Jadwal
# ===============
@app.route('/getAll')
def getDevicesAll():
    mycol = mydb["scheduler"]
    mydoc = mycol.find(projection={"_id": False})
    json_data = dumps(list(mydoc), indent=2)
    print(json_data)
    return jsonify(json.loads(json_data))


@app.route('/getById')
def getDevicesById():
    idDevice = request.args.get('id')
    mycol = mydb["scheduler"]
    mydoc = mycol.find(projection={"_id": False})
    rowData = list(mydoc)
    if rowData:
        json_data = dumps(rowData[0], indent=2)
        print(json_data)
        return json_data
    else:
        return jsonify([])


app.run(host='0.0.0.0', port=8080, debug=True)
