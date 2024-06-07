import time

class softwaretimer:
    def __init__(self):
        self.start_time = 0
        self.duration = 0
        self.running = False

    def start(self, duration):
        self.duration = duration
        self.start_time = time.time() * 1000  # convert to milliseconds
        self.running = True

    def is_expired(self):
        if self.running and (time.time() * 1000 - self.start_time) >= self.duration:
            self.running = False
            return True
        return False

    def stop(self):
        self.running = False
