from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/test_endpoint', methods=['POST'])
def test_endpoint():
    data = request.json
    print(f"Received data: {data}")
    return jsonify({"status": "success", "received": data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
