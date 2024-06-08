import Ultilities.modbus485 as modbus485
from Ultilities.softwaretimer import softwaretimer

class WaterManagementTask:
    def __init__(self, modbus, notification_func):
        self.modbus = modbus
        self.notification_func = notification_func
        self.state = 'IDLE'
        self.current_mixer = 0
        self.mixer_ids = modbus.fertilizer_mixers
        self.area_selector_ids = modbus.area_selectors
        self.pump_in_relay_id = modbus.pump_in
        self.pump_out_relay_id = modbus.pump_out
        self.timer = softwaretimer()
        self.schedules = []
        self.current_schedule = None

    def activate_relay(self, relay_id, state):
        self.modbus.setDevice(self.modbus.ser, relay_id, state)

    def calculate_mixing_time(self, fertilizer_amount):
        # Assuming 1ml = 0.25s
        return fertilizer_amount * 0.25 * 1000  # Convert to milliseconds

    def calculate_watering_time(self, water_ml):
        # Assuming 1000ml = 20s
        return water_ml * 20  # Convert to milliseconds

    def run(self):
        if self.state == 'IDLE' and self.schedules:
            self.state = 'SELECTING_AREA'
            self.current_area_selector = 0
            self.current_schedule = self.schedules.pop(0)
            self.activate_relay(self.area_selector_ids[self.current_area_selector], True)
            print(f"Started selecting area with selector {self.area_selector_ids[self.current_area_selector]}")
            self.timer.start(10000)  # 10 seconds

        elif self.state == 'SELECTING_AREA':
            if self.timer.is_expired():
                self.activate_relay(self.area_selector_ids[self.current_area_selector], False)
                print(f"Stopped selecting area with selector {self.area_selector_ids[self.current_area_selector]}")
                self.state = 'MIXING'
                self.current_mixer = 0
                mixing_time = self.calculate_mixing_time(self.current_schedule['fertilizer1'])
                self.timer.start(mixing_time)
                self.activate_relay(self.mixer_ids[self.current_mixer], True)
                print(f"Started mixing with mixer {self.mixer_ids[self.current_mixer]} for {mixing_time / 1000} seconds")

        elif self.state == 'MIXING':
            if self.timer.is_expired():
                self.activate_relay(self.mixer_ids[self.current_mixer], False)
                print(f"Stopped mixing with mixer {self.mixer_ids[self.current_mixer]}")
                self.current_mixer += 1
                if self.current_mixer < len(self.mixer_ids):
                    mixing_time = self.calculate_mixing_time(self.current_schedule[f'fertilizer{self.current_mixer + 1}'])
                    self.timer.start(mixing_time)
                    self.activate_relay(self.mixer_ids[self.current_mixer], True)
                    print(f"Started mixing with mixer {self.mixer_ids[self.current_mixer]} for {mixing_time / 1000} seconds")
                else:
                    self.state = 'PUMP_IN'
                    watering_time = self.calculate_watering_time(self.current_schedule['water'])
                    self.timer.start(watering_time)
                    self.activate_relay(self.pump_in_relay_id, True)
                    print(f"Started pump-in with relay {self.pump_in_relay_id} for {watering_time / 1000} seconds")

        elif self.state == 'PUMP_IN':
            if self.timer.is_expired():
                self.activate_relay(self.pump_in_relay_id, False)
                print(f"Stopped pump-in with relay {self.pump_in_relay_id}")
                self.state = 'PUMP_OUT'
                watering_time = self.calculate_watering_time(self.current_schedule['water'])
                self.timer.start(watering_time)
                self.activate_relay(self.pump_out_relay_id, True)
                print(f"Started pump-out with relay {self.pump_out_relay_id} for {watering_time / 1000} seconds")

        elif self.state == 'PUMP_OUT':
            if self.timer.is_expired():
                self.activate_relay(self.pump_out_relay_id, False)
                print(f"Stopped pump-out with relay {self.pump_out_relay_id}")
                self.state = 'IDLE'
                self.current_schedule = None
                self.notification_func("Cycle complete")

def add_schedule_to_system(schedule):
    # Tạo instance của WaterManagementTask và thêm lịch tưới
    global watermanagement
    watermanagement.schedules.append(schedule)
    print(f"Schedule added to system: {schedule}")
