import os

try:
    MAPS_API_KEY = os.environ['MAPS_API_KEY']
except KeyError:
    print("You must set MAPS_API_KEY environment variable!")
    exit(-1)

try:
    SECRET_KEY = os.environ['SECRET_KEY']
except KeyError:
    print("You must set SECRET_KEY environment variable!")
    exit(-1)

PATH = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(PATH, 'lora.db')