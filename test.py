from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

CM4_URL = 'http://172.28.182.53:5000'

@app.route('/trigger_task', methods=['POST'])
def trigger_task():
    data = request.json
    response = requests.post(f'{CM4_URL}/trigger_task', json=data)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
