from flask import Flask, render_template
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sensor')
def sensor():
    return render_template('sensor.html')


@app.route('/control')
def control():
    return render_template('control.html')


@app.route('/scheduler')
def scheduler():
    return render_template('scheduler.html')


@app.route('/trigger')
def trigger():
    return render_template('trigger.html')


app.run(host='0.0.0.0', port=8080, debug=True)
