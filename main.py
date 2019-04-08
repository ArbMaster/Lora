#!/usr/bin/env python3

from __future__ import print_function

from contextlib import closing
from flask import (
    Flask, 
    g, 
    request, 
    render_template, 
    jsonify,
    abort
)

from pprint import pprint as pp
from datetime import datetime

import settings
import decoder
import sqlite3
from decoder import Payload

app = Flask(__name__)

def connect_db():
    return sqlite3.connect('lora.db')

@app.cli.command('initdb')
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read().decode('utf-8'))
        db.commit()
    
@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/lora/', methods=['POST'])
def uplink():
    if request.is_json:
        print(request.json)
        data = request.json['DevEUI_uplink']
        cursor = g.db.cursor()
        print(data['payload_hex'])
        q = 'INSERT INTO Payload (deveui, payload, ts) VALUES (?, ?, ?)'
        values = (data['DevEUI'], data['payload_hex'], datetime.now().timestamp())
        cursor.execute(q, values)
        g.db.commit()
        return "", 200
    else:
        return "", 400

        
@app.route('/web/')
def webindex():
    data = {
        'API_KEY': settings.MAPS_API_KEY,
    }    
    return render_template('index.html', **data)

def get_count(cursor):
    q = "SELECT COUNT(id) FROM Payload"
    return cursor.execute(q).fetchone()[0]
        
def get_all_records(cursor, offset, limit):
    result = []
    q = """SELECT deveui, payload, ts FROM Payload ORDER BY ts DESC LIMIT ? OFFSET ?"""
    for row in cursor.execute(q, (limit, offset)):
        deveui, data, ts = row
        payload = Payload(data)
        result.append({
            'DevEUI': deveui,
            'Source': payload.source,
            'Time': datetime.fromtimestamp(ts).strftime("%d-%m-%Y %H:%M:%S"),
            'UplinkCount': payload.uplink,
            'DownlinkCount': payload.downlink,
            'Latitude': payload.latitude,
            'Longitude': payload.longitude,
            'Temperature': payload.temperature,
        })
    return result
    
@app.route('/api/table', methods=['POST'])
def datatable():
    if not request.is_json:
        abort(400)
    received = request.json
    try:
        draw = received['draw']
        limit  = received['length']
        offset = received['start']
    except KeyError:
        abort(400)
    cursor = g.db.cursor()
    data = get_all_records(cursor, offset, limit)
    recordCount = get_count(cursor)
    result = {
        'draw': draw, 
        'recordsFiltered': recordCount, 
        'recordsTotal': recordCount,
        'data': data
    }
    return jsonify(result)
        
if __name__ == '__main__':
    app.run(host= '0.0.0.0', port=8888, debug=True)