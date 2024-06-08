from flask import Flask, request, jsonify
import threading
from PrivateTasks.water_management_task import WaterManagementTask, add_schedule_to_system

app = Flask(__name__)

# Danh sách lưu trữ các lịch tưới
schedules = []

# Hàm đơn giản để tính toán thời gian tưới
def calculate_watering_time(water_ml):
    return water_ml / 1000  # 1000ml tương ứng với 1 giây

@app.route('/set_schedule', methods=['POST'])
def set_schedule():
    data = request.json
    name = data.get('name')
    area = data.get('area')
    fertilizer1 = data.get('fertilizer1')
    fertilizer2 = data.get('fertilizer2')
    fertilizer3 = data.get('fertilizer3')
    water = data.get('water')
    
    watering_time = calculate_watering_time(water)
    
    schedule = {
        'name': name,
        'area': area,
        'fertilizer1': fertilizer1,
        'fertilizer2': fertilizer2,
        'fertilizer3': fertilizer3,
        'water': water,
        'watering_time': watering_time
    }
    
    schedules.append(schedule)
    
    # Tương tác với hệ thống hiện tại để thêm lịch tưới
    add_schedule_to_system(schedule)
    
    return jsonify({"status": "success", "schedule": schedule})

if __name__ == '__main__':
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000}).start()
