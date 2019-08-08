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
import re

def delete_session(user_id):
    cursor = g.dbhandle.cursor()
    db.delete_session(cursor, user_id)
    g.dbhandle.commit()

def create_session(request, user_id):
    # 1 Generate new cookie SHA256(nonce, ts, username, SECRET_KEY)
    hasher = hashlib.sha256()
    hasher.update(os.urandom(16))
    hasher.update(user_id.to_bytes(8, 'little'))
    hasher.update(bytes(settings.SECRET_KEY, encoding='utf-8'))
    cookie = hasher.hexdigest()
    
    # Delete all previous session for this particular id
    delete_session(user_id)
    
    # 3 insert new session in Session table
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
        
    user_id, ts = session
    if ts + settings.SESSION_LIFETIME < time.time():
        print("Session expired for cookie %s" % cookie)
        return False
        
    return user_id

@app.route('/register/', methods=['GET', 'POST'])
def register():
    valid = True
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form.get('username')
        if not username:
            flash('You must provide a username!')
            valid = False
            
        email = request.form.get('email')
        if not email or not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('You must provide an email address!')
            valid = False

        password1 = request.form.get('password1')
        if not password1:
            flash('You must provide password!')
            valid = False
        
        password2 = request.form.get('password2')
        if not password1:
            flash('You must provide password!')
            valid = False
        
        if password1 != password2:
            flash('Passwords do not match!')
            valid = False
            
        cursor = g.dbhandle.cursor()
        
        if valid:
            user_id = db.add_user(cursor, username, password1, email)
            if user_id:
                cookie = create_session(cursor, user_id)
                response = make_response(redirect(url_for('webindex')))
                response.set_cookie('login', cookie)
                return response
            else:
                flash('This username is taken!')
                
        return render_template('register.html')
        
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
                flash('Invalid username or password!')
                return render_template('login.html')    
        else:
            flash('You must provide username and password!')
            return render_template('login.html')

@app.route('/logout/')
def logout():
    user_id = get_session(request)
    delete_session(user_id)
    return redirect(url_for('webindex'))
