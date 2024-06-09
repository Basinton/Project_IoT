from flask import Flask, request, jsonify

app = Flask(__name__)

# Example endpoint
@app.route('/trigger_task', methods=['POST'])
def trigger_task():
    data = request.json
    message = data.get('message')
    print(f"Received message: {message}")
    return jsonify({"status": "success", "message": message})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
