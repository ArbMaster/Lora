from main import app

from flask import Flask, g, abort, jsonify
from decoder import Payload
from datetime import datetime
        
def get_count(cursor):
    q = "SELECT COUNT(id) FROM Payload"
    return cursor.execute(q).fetchone()[0]
        
def get_all_records(cursor, offset, limit):
    result = []
    q = """SELECT deveui, payload, ts FROM Payload LIMIT ? OFFSET ?"""
    for row in cursor.execute(q, (limit, offset)):
        deveui, data, ts = row
        payload = Payload(data)
        result.append({
            'DevEUI': deveui,
            'Source': payload.source,
            'Time': datetime.fromtimestamp(ts).strftime("%d-%m-%Y %H:%M:%S"),
            'UplinkCount': payload.uplink,
            'DownlinkCount': payload.downlink,
            'Temperature': payload.temperature
        })
    return result

@app.route('/api/table', methods=['POST'])
def datatable():
    if not request.is_json:
        abort(400)
    received = request.json
    limit  = received['length']
    offset = received['start']
    cursor = g.db.cursor()
    data = get_all_records(cursor, offset, limit)
    result = {
        'draw': received['draw'], 
        'recordsFiltered': len(data), 
        'recordsTotal': get_count(cursor),
        'data': data
    }
    return jsonify(result)
    