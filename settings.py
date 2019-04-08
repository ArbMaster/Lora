import os

try:
    MAPS_API_KEY = os.environ['MAPS_API_KEY']
except KeyError:
    raise("You must set MAPS_API_KEY environment variable!")

try:
    SECRET_KEY = os.environ['SECRET_KEY']
except KeyError:
    raise("You must set SECRET_KEY environment variable!")
    
DATABASE = 'lora.db'