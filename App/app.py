from flask import Flask, request, jsonify
from PrivateTasks.water_management_task import add_schedule_to_system

app = Flask(__name__)

@app.route('/set_schedule', methods=['POST'])
def set_schedule():
    data = request.json
    name = data.get('name')
    area = data.get('area')
    fertilizer1 = data.get('fertilizer1')
    fertilizer2 = data.get('fertilizer2')
    fertilizer3 = data.get('fertilizer3')
    water = data.get('water')
    
    schedule = {
        'name': name,
        'area': area,
        'fertilizer1': fertilizer1,
        'fertilizer2': fertilizer2,
        'fertilizer3': fertilizer3,
        'water': water
    }
    
    add_schedule_to_system(schedule)
    
    return jsonify({"status": "success", "schedule": schedule})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
