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
    return '<h1>Selamat Datang di API Cahaya</h1>'

# ===============
# CRUD Device
# ===============


@app.route('/devices/getAll')
def getDevicesAll():
    mycol = mydb["devices"]
    mydoc = mycol.find({
        "jenis.tipe": "sensor",
        "jenis.model": "cahaya",
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
        "jenis.tipe": "sensor",
        "jenis.model": "cahaya",
        'id': idDevice
    }, projection={"_id": False})
    try:
        return jsonify(mydoc)
    except:
        return jsonify([])


app.run(host='0.0.0.0', port=8080, debug=True)
