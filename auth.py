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
    flash,
    make_response
)

import os
from main import app
import db
import settings
import time
import hashlib

def create_session(request, user_id):
    # 1 Generate new cookie SHA256(nonce, ts, username, SECRET_KEY)
    hasher = hashlib.sha256()
    hasher.update(os.urandom(16))
    hasher.update(user_id.to_bytes(8, 'little'))
    hasher.update(bytes(settings.SECRET_KEY, encoding='utf-8'))
    cookie = hasher.hexdigest()
    
    # 2 insert new session in Session table
    cursor = g.dbhandle.cursor()
    db.create_session(cursor, user_id, cookie)
    g.dbhandle.commit()
    
    return cookie

def get_session(request):
    cookie = request.cookies.get('login')
    if not cookie:
        return False
    
    cursor = g.dbhandle.cursor()
    session = db.get_session(cursor, cookie)
    if not session:
        return False
        
    ts = session
    if ts + settings.SESSION_LIFETIME < time.time():
        print("Session expired for cookie %s" % cookie)
        return False
    
    return True
    
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            #check username & password in db
            cursor = g.dbhandle.cursor()
            user_id = db.check_login(cursor, username, password)
            if user_id:
                cookie = create_session(request, user_id)
                response = make_response(redirect(url_for('webindex')))
                response.set_cookie('login', cookie)
                return response
            else:
                return render_template('login.html')    
        else:
            print("Error!")
            return render_template('login.html')

def logout():
    pass
