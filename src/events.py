import threading
import random
import time

class RandomEventSystem(threading.Thread):
    def __init__(self, event_center):
        super().__init__()
        self.event_center = event_center
        self.running = True

    def run(self):
        while self.running:
            time.sleep(random.randint(5, 10))
            event = random.choice(["EMERGENCY", "CONGESTION"])

            if event == "EMERGENCY":
                print("Emergency event triggered")
                self.event_center.notify("EMERGENCY", {"location": "Platform A"})
            elif event == "CONGESTION":
                print("Congestion event triggered")

    def stop(self):
        self.running = False