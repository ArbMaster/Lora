import os

try:
    SECRET_KEY = os.environ['SECRET_KEY']
except KeyError:
    print("You must set SECRET_KEY environment variable!")
    exit(-1)

PATH = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(PATH, 'lora.db')
SESSION_LIFETIME = 30 * 60 #default 30 min inactivity
DEFAULT_DEVICE_LAT = 40.3258
DEFAULT_DEVICE_LNG = 09.8162
