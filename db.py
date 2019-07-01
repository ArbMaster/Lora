
import settings
import sqlite3
from contextlib import closing
from datetime import datetime

from main import app
from decoder import Payload

def connect():
    handle = sqlite3.connect(settings.DATABASE)
    handle.cursor().execute('PRAGMA foreign_keys = ON')
    return handle
   
@app.cli.command('initdb')
def init():
    with closing(connect()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read().decode('utf-8'))
        db.commit()
        
def get_count(cursor):
    q = "SELECT COUNT(id) FROM Payload"
    return cursor.execute(q).fetchone()[0]
        
        
def get_all_records(cursor, offset, limit):
    result = []
    q = """
        SELECT d.deveui, p.payload, p.ts, p.decoder
        FROM Payload p
        INNER JOIN Device d ON p.deveui = d.deveui
        INNER JOIN Profile p ON d.pid = p.pid
        ORDER BY ts DESC 
        LIMIT ? OFFSET ?
        """
    for row in cursor.execute(q, (limit, offset)):
        deveui, data, ts, decoder = row
        payload = Payload(data, decoder)
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


def get_all_profiles(cursor):
    query = "SELECT pid, name FROM profile"
    return cursor.execute(query).fetchall()
   
   
def get_all_devices(cursor):
    query = """
        SELECT d.deveui, p.name
        FROM Device d 
        INNER JOIN Profile p
        ON d.pid = p.pid
        """
    return cursor.execute(query).fetchall()
    
def add_device(cursor, deveui, profile):
    query = """
        INSERT INTO Device (deveui, pid)
        VALUES(?, ?)
        """
    try:
        cursor.execute(query, (deveui, profile))
    except sqlite3.IntegrityError:
        return False
    return True