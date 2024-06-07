import platform
import time

if platform.system() == 'Linux':
    from gpiozero import LED
else:
    class MockLED:
        def __init__(self, pin):
            self.pin = pin
            self.state = False

        def on(self):
            self.state = True
            print(f"Mock LED on pin {self.pin} is now ON")

        def off(self):
            self.state = False
            print(f"Mock LED on pin {self.pin} is now OFF")

    LED = MockLED

class LedBlinkyTask:
    def __init__(self, led_pin=17):
        self.led = LED(led_pin)

    def blink(self):
        self.led.on()
        time.sleep(0.5)
        self.led.off()
        time.sleep(0.5)
