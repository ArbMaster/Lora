1. Install flask: pip install flask
2. Create Google MAPS API Key: https://developers.google.com/maps/documentation/javascript/get-api-key
3. Add environment variables
    export MAPS_API_KEY=<key>
    export FLASK_APP=main.py
4. Initialize DB: flask initdb
5. Run application: flask run --host=0.0.0.0 --port=8888