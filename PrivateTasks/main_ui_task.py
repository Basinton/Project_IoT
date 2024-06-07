class Main_UI:
    def __init__(self, watermonitoring):
        self.watermonitoring = watermonitoring

    def update_ui(self):
        print("UI is updated")

    def run(self):
        self.update_ui()

    def notification_func(self, message):
        print(f"Notification: {message}")