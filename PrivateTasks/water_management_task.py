import time
import Utilities.modbus485 as modbus485

class WaterManagementTask:
    def __init__(self, modbus, notification_func):
        self.modbus = modbus
        self.notification_func = notification_func
        self.state = 'IDLE'
        self.start_time = None
        self.current_mixer = 0
        self.mixer_ids = [1, 2, 3]
        self.area_selector_ids = [4, 5, 6]  # Representing 3 relays for 3 areas
        self.pump_in_relay_id = 7
        self.pump_out_relay_id = 8
        self.sonar_check_interval = 5  # Interval to check sonar sensor (in seconds)
        self.sonar_timer = time.time()

    def activate_relay(self, relay_id, state):
        self.modbus.setDevice(relay_id, state)

    def run(self):
        if self.state == 'IDLE':
            self.state = 'SELECTING_AREA'
            self.start_time = time.time()
            self.current_area_selector = 0
            self.activate_relay(self.area_selector_ids[self.current_area_selector], True)
            print(f"Started selecting area with selector {self.area_selector_ids[self.current_area_selector]}")

        elif self.state == 'SELECTING_AREA':
            if time.time() - self.start_time > 10:  # Selection time is 10 seconds
                self.activate_relay(self.area_selector_ids[self.current_area_selector], False)
                print(f"Stopped selecting area with selector {self.area_selector_ids[self.current_area_selector]}")
                self.state = 'MIXING'
                self.start_time = time.time()
                self.activate_relay(self.mixer_ids[self.current_mixer], True)
                print(f"Started mixing with mixer {self.mixer_ids[self.current_mixer]}")

        elif self.state == 'MIXING':
            if time.time() - self.start_time > 10:  # Mixing time is 10 seconds
                self.activate_relay(self.mixer_ids[self.current_mixer], False)
                print(f"Stopped mixing with mixer {self.mixer_ids[self.current_mixer]}")
                self.current_mixer = (self.current_mixer + 1) % len(self.mixer_ids)
                self.state = 'PUMP_IN'
                self.start_time = time.time()
                self.activate_relay(self.pump_in_relay_id, True)
                print(f"Started pump-in with relay {self.pump_in_relay_id}")

        elif self.state == 'PUMP_IN':
            if time.time() - self.start_time > 20:  # Pump-in time is 20 seconds
                self.activate_relay(self.pump_in_relay_id, False)
                print(f"Stopped pump-in with relay {self.pump_in_relay_id}")
                self.state = 'PUMP_OUT'
                self.start_time = time.time()
                self.activate_relay(self.pump_out_relay_id, True)
                print(f"Started pump-out with relay {self.pump_out_relay_id}")

        elif self.state == 'PUMP_OUT':
            if time.time() - self.start_time > 20:  # Pump-out time is 20 seconds
                self.activate_relay(self.pump_out_relay_id, False)
                print(f"Stopped pump-out with relay {self.pump_out_relay_id}")
                self.state = 'IDLE'
                self.notification_func("Cycle complete")
