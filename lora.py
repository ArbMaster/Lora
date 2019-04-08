
from main import app

@app.route('/lora/', methods=['POST'])
def uplink():
    if request.is_json:
        data = request.json['DevEUI_uplink']
        cursor = g.db.cursor()
        q = 'INSERT INTO Payload (deveui, payload, ts) VALUES (?, ?, ?)'
        values = (data['DevEUI'], data['payload_hex'], datetime.now().timestamp())
        cursor.execute(q, values)
        g.db.commit()
        return "", 200
    else:
        return "", 400