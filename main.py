#!/usr/bin/env python3

from __future__ import print_function

from flask import (
    Flask,
    session,
    g, 
    request, 
    render_template, 
    jsonify,
    abort,
    redirect,
    url_for,
    flash
)

from functools import wraps
from pprint import pprint as pp
from datetime import datetime

import folium
import settings

app = Flask(__name__)
app.secret_key = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'

import db
import auth

def login_required(original_function):
    @wraps(original_function)
    def decorated_function(*args, **kwargs):
        if auth.get_session(request):
            return original_function(*args, **kwargs)
        return redirect(url_for('login', next=request.url))
    return decorated_function


@app.before_request
def before_request():
    g.dbhandle = db.connect()

@app.teardown_request
def teardown_request(exception):
    g.dbhandle.close()        

@app.route('/lora/', methods=['POST'])
def uplink():
    if request.is_json:
        data = request.json['DevEUI_uplink']
        print(data)
        cursor = g.dbhandle.cursor()
        q = 'INSERT INTO Payload (deveui, payload, ts) VALUES (?, ?, ?)'
        values = (data['DevEUI'], data['payload_hex'], datetime.now().timestamp())
        cursor.execute(q, values)
        g.dbhandle.commit()
        return "", 200
    else:
        return "", 400

@app.route('/')
def index():
    return redirect(url_for('webindex'), code=302)

@app.route('/web/')
@login_required
def webindex():
    return render_template('index.html')

@app.route('/admin/', methods=['GET', 'POST'])
@login_required
def admin():
    cursor = g.dbhandle.cursor()
    if request.method == "GET":
        devices  = db.get_all_devices(cursor)
        profiles = db.get_all_profiles(cursor)
        return render_template('admin.html', devices=devices, profiles=profiles)
    elif request.method == "POST":
        deveui = request.form.get('deveui')
        profile = request.form.get('profile')
        if db.add_device(cursor, deveui, profile):
            g.dbhandle.commit()
        else:
            flash('This Device already exists!')
        return redirect(url_for('admin'))

@app.route('/api/table', methods=['POST'])
@login_required
def datatable():
    if not request.is_json:
        abort(400, "Data not in JSON format!")
        return
    received = request.json
    try:
        draw = received['draw']
        limit  = received['length']
        offset = received['start']
    except KeyError:
        abort(400, description="Required parameters are missing!")
        return
    data = db.get_all_records(g.dbhandle.cursor(), offset, limit)
    recordCount = db.get_count(g.dbhandle.cursor())
    result = {
        'draw': draw, 
        'recordsFiltered': recordCount, 
        'recordsTotal': recordCount,
        'data': data
    }
    return jsonify(result)

@app.route('/map/', methods=['POST'])
@login_required
def render_map():
    if not request.is_json:
        abort(400)
        return
    try:
        latitude  = float(request.json['latitude'])
        longitude = float(request.json['longitude'])
    except KeyError:
        abort(400, description="Coordinates are missing!")
        return
    except ValueError:
        abort(400, description="Coordinates must be real numbers!")
        return
    if latitude and longitude:
        start_coords = (latitude, longitude)
        folium_map = folium.Map(location=start_coords, zoom_start=14)
        folium.Marker([latitude, longitude]).add_to(folium_map)
        return folium_map._repr_html_()
    else:
        abort(400, description="Invalid coordinates!")
        return
    
        
if __name__ == '__main__':
    app.run()
