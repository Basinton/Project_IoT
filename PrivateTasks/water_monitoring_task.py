from Adafruit_IO import Client, Feed, RequestError
import json
import Ultilities.modbus485 as modbus485

class WaterMonitoringTask:
    def __init__(self, timer, serial_port, aio_username, aio_key, aio_sensor_feed):
        self.timer = timer
        self.serial_port = serial_port
        self.aio = Client(aio_username, aio_key)

        # Initialize feeds
        self.feeds = {
            'sensor-data': self.init_feed(aio_sensor_feed)
        }

        # Maintain previous states to detect changes
        self.previous_states = {
            'sensor-data': None
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
            if self.previous_states[feed_name] != json_value:
                self.aio.send_data(self.feeds[feed_name], json_value)  # Use feed key to send data
                self.previous_states[feed_name] = json_value  # Update the previous state

    def read_temperature(self):
        return modbus485.readTemperature()

    def read_humidity(self):
        return modbus485.readMoisture()

    def read_water_amount(self):
        # Placeholder function to simulate reading water amount
        return 1000  # Replace with actual reading in ml

    def monitor_sensors(self):
        temperature = self.read_temperature()
        humidity = self.read_humidity()
        water_amount = self.read_water_amount()

        sensor_data = {
            'temperature': temperature,
            'humidity': humidity,
            'water_amount': water_amount
        }

        self.update_feed('sensor-data', sensor_data)

    def run(self):
        self.monitor_sensors()
        # Add additional monitoring and updates as needed
