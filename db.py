
import settings
import sqlite3
from contextlib import closing
from datetime import datetime

from main import app
from decoder import Payload

SQLITE_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

def get_dev_admin_loc(deveui):
    #to do if loc already is set on db if not return default loc
    return settings.DEFAULT_DEVICE_LAT, settings.DEFAULT_DEVICE_LNG

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

def get_count(cursor, user_id):
    q = """SELECT COUNT(id) FROM Payload p
    INNER JOIN Device d ON p.deveui = d.deveui
    WHERE d.uid = ? AND p.payload <> ""
    """
    return cursor.execute(q,(user_id,)).fetchone()[0]


def get_all_records(cursor, uid, offset, limit):
    result = []
    q = """
        SELECT d.deveui, p.payload, p.ts, prof.decoder
        FROM Payload p
        INNER JOIN Device d ON p.deveui = d.deveui
        INNER JOIN Profile prof ON d.pid = prof.pid
        WHERE d.uid = ? AND
        p.payload <> ""
        ORDER BY ts DESC
        LIMIT ? OFFSET ?
        """
    for row in cursor.execute(q, (uid, limit, offset)):
        deveui, data, ts, decoder = row
        payload = Payload(data, decoder)
        if not payload.latitude or not payload.longitude:
            payload.latitude, payload.longitude = get_dev_admin_loc(deveui)
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

def deg_fake_last_loc():
    import random
    result = []

    for i in range(10):
        lat = random.uniform(41.40, 41.99)
        lng = random.uniform(19.00, 19.80)
        result.append({
            'DevEUI': random.randint(10**14, 10**15),
            'Latitude': lat,
            'Longitude': lng,
        })
    return result

def get_last_loc(cursor, user_id):
    query = """SELECT d.deveui, p.payload, max(p.ts), prof.decoder
            FROM Payload p
            INNER JOIN Device d ON p.deveui = d.deveui
            INNER JOIN Profile prof ON d.pid = prof.pid
            WHERE d.uid = ? AND
            p.payload <> ""
            GROUP BY d.deveui
            """
    result = []
    for row in cursor.execute(query, (user_id,)):
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

def get_user(cursor, username):
    query = "SELECT id from User where username = ?"
    try:
        result = cursor.execute(query, (username, ))
        user_id = result.fetchone()
        return user_id
    except:
        return None

def add_user(cursor, username, password, email):
    query = "INSERT INTO User(username, password, email) VALUES(?, ?, ?)"
    try:
        cursor.execute(query, (username, password, email))
        print('Added user with id: %d' % cursor.lastrowid)
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return False
    except:
        print('DB add_user unknown error!')
        return False

def check_login(cursor, username, password):
    query = """
    SELECT id
    FROM User
    WHERE username = ? AND password = ?
    """
    try:
        result = cursor.execute(query, (username, password))
        return result.fetchone()[0]
    except IndexError:
        return False
    except:
        print("DB check_login Error!")
        return False

def create_session(cursor, user_id, cookie):
    query = """INSERT INTO Session (cookie, uid) VALUES(?, ?)"""
    try:
        cursor.execute(query, (cookie, user_id))
        return True
    except:
        return False

def get_session(cursor, cookie):
    query = "SELECT uid, ts FROM Session where cookie = ?"
    try:
        result = cursor.execute(query, (cookie, ))
        user_id, ts = result.fetchone()
        dt = datetime.strptime(ts, SQLITE_TIMESTAMP_FORMAT)
        return user_id, dt.timestamp()
    except IndexError:
        return False
    except:
        return False

def delete_session(cursor, user_id):
    query = "DELETE FROM Session where uid = ?"
    cursor.execute(query, (user_id, ))
