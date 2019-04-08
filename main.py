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

import settings

app = Flask(__name__)
app.secret_key = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
#session.init_app(app)

from pprint import pprint as pp

import db
import lora

@app.before_request
def before_request():
    g.dbhandle = db.connect()

@app.teardown_request
def teardown_request(exception):
    g.dbhandle.close()        
        
@app.route('/web/')
def webindex():
    data = {
        'API_KEY': settings.MAPS_API_KEY,
    }  
    return render_template('index.html', **data)

@app.route('/admin/', methods=['GET', 'POST'])
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
def datatable():
    if not request.is_json:
        abort(400)
        return
    received = request.json
    try:
        draw = received['draw']
        limit  = received['length']
        offset = received['start']
    except KeyError:
        abort(400)
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
        
if __name__ == '__main__':
    
    app.run(host= '0.0.0.0', port=8888, debug=True)