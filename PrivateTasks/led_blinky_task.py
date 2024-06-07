import RPi.GPIO as GPIO
import time

class LedBlinkyTask:
    def __init__(self, pin=17):
        self.led_pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.led_pin, GPIO.OUT)
        self.led_state = False

    def toggle_led(self):
        self.led_state = not self.led_state
        GPIO.output(self.led_pin, self.led_state)
        print(f"LED on pin {self.led_pin} is now {'ON' if self.led_state else 'OFF'}")

    def run(self):
        self.toggle_led()

    def cleanup(self):
        GPIO.cleanup()
