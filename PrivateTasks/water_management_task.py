import requests
import json
import time
from datetime import datetime, timezone
import Ultilities.modbus485 as modbus485
from Ultilities.softwaretimer import softwaretimer
from Adafruit_IO import Client, Feed, RequestError

class WaterManagementTask:
    IDLE = 'IDLE'
    FERTILIZING = 'FERTILIZING'
    MIXING = 'MIXING'
    PUMP_IN = 'PUMP_IN'
    SELECTING_AREA = 'SELECTING_AREA'
    PUMP_OUT = 'PUMP_OUT'

    def __init__(self, modbus, notification_func, aio_username, aio_key, aio_schedule_feed, aio_management_feed):
        self.modbus = modbus
        self.notification_func = notification_func
        self.aio = Client(aio_username, aio_key)
        self.aio_username = aio_username
        self.aio_key = aio_key
        self.aio_schedule_feed = aio_schedule_feed
        self.aio_management_feed = aio_management_feed
        self.state = self.IDLE
        self.current_mixer = 0
        self.mixer_ids = [1, 2, 3]
        self.area_selector_ids = [4, 5, 6]
        self.pump_in_relay_id = 7
        self.pump_out_relay_id = 8
        self.timer = softwaretimer()
        self.schedules = []
        self.current_schedule = None
        self.last_fetched_time = datetime.min.replace(tzinfo=timezone.utc)
        self.last_completed_schedule_name = None

        # Initialize feeds
        self.feeds = {
            'management': self.init_feed(aio_management_feed)
        }

    def init_feed(self, feed_name):
        try:
            feed = self.aio.feeds(feed_name)
        except RequestError:
            feed = self.aio.create_feed(Feed(name=feed_name))
        return feed.key  # Return the feed key

    def update_feed(self, feed_name, value):
        if feed_name in self.feeds:
            json_value = json.dumps(value)
            self.aio.send_data(self.feeds[feed_name], json_value)  # Use feed key to send data

    def activate_relay(self, relay_id, state):
        self.modbus.setDevice(self.modbus.ser, relay_id, state)

    def calculate_time(self, ml):
        return ml * 0.01 * 1000  # Convert to milliseconds

    def fetch_schedules(self):
        url = f"https://io.adafruit.com/api/v2/{self.aio_username}/feeds/{self.aio_schedule_feed}/data"
        headers = {
            'X-AIO-Key': self.aio_key
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            feed_data = response.json()
            for item in feed_data:
                created_at = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
                if created_at > self.last_fetched_time:
                    schedule = json.loads(item['value'])
                    if schedule['name'] != self.last_completed_schedule_name:
                        self.schedules.append(schedule)
                        self.last_fetched_time = created_at
            print("Fetched new schedules from Adafruit IO")
        else:
            print("Failed to fetch schedules from Adafruit IO")

    def run(self):
        if self.state == self.IDLE:
            if not self.schedules:
                self.fetch_schedules()
            if self.schedules:
                self.current_schedule = self.schedules.pop(0)
                # Gửi xác nhận lịch tưới
                confirmation_data = {
                    'schedule_name': self.current_schedule['name'],
                    'status': 'confirmed'
                }
                self.update_feed('management', confirmation_data)

                self.state = self.FERTILIZING
                self.current_mixer = 0
                fertilizer_ml = int(self.current_schedule[f'fertilizer{self.current_mixer + 1}'])
                self.timer.start(self.calculate_time(fertilizer_ml))
                self.activate_relay(self.mixer_ids[self.current_mixer], True)
                print(f"Started fertilizing with mixer {self.mixer_ids[self.current_mixer]} for {fertilizer_ml} ml")

        elif self.state == self.FERTILIZING:
            if self.timer.is_expired():
                self.activate_relay(self.mixer_ids[self.current_mixer], False)
                self.current_mixer += 1
                if self.current_mixer < len(self.mixer_ids):
                    fertilizer_ml = int(self.current_schedule[f'fertilizer{self.current_mixer + 1}'])
                    self.timer.start(self.calculate_time(fertilizer_ml))
                    self.activate_relay(self.mixer_ids[self.current_mixer], True)
                    print(f"Started fertilizing with mixer {self.mixer_ids[self.current_mixer]} for {fertilizer_ml} ml")
                else:
                    self.state = self.MIXING
                    self.timer.start(10000)
                    print("Started mixing for 10 seconds")

        elif self.state == self.MIXING:
            if self.timer.is_expired():
                self.state = self.PUMP_IN
                water_ml = int(self.current_schedule['waterAmount'])
                self.timer.start(self.calculate_time(water_ml))
                self.activate_relay(self.pump_in_relay_id, True)
                print(f"Started pump-in with relay {self.pump_in_relay_id} for {water_ml} ml")

        elif self.state == self.PUMP_IN:
            if self.timer.is_expired():
                self.activate_relay(self.pump_in_relay_id, False)
                self.state = self.SELECTING_AREA
                area = int(self.current_schedule['area']) - 1
                self.timer.start(1000)
                self.activate_relay(self.area_selector_ids[area], True)
                print(f"Started selecting area {area + 1}")

        elif self.state == self.SELECTING_AREA:
            if self.timer.is_expired():
                area = int(self.current_schedule['area']) - 1
                self.activate_relay(self.area_selector_ids[area], False)
                self.state = self.PUMP_OUT
                water_ml = int(self.current_schedule['waterAmount'])
                self.timer.start(self.calculate_time(water_ml))
                self.activate_relay(self.pump_out_relay_id, True)
                print(f"Started pump-out with relay {self.pump_out_relay_id} for {water_ml} ml")

        elif self.state == self.PUMP_OUT:
            if self.timer.is_expired():
                self.activate_relay(self.pump_out_relay_id, False)
                self.state = self.IDLE
                self.notification_func("Cycle complete")
                print("Watering cycle complete")
                self.last_completed_schedule_name = self.current_schedule['name']
                self.current_schedule = None

    def cleanup(self):
        self.modbus.close_modbus()
