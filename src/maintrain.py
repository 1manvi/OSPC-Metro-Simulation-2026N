import threading
import random
import time
import numpy as np
import matplotlib.pyplot as plt

class StationEventCenter:
    def __init__(self):
        self._subscribers = []
        self._lock = threading.Lock()

    def subscribe(self, observer):
        with self._lock:
            self._subscribers.append(observer)

    def notify(self, event_type, data):
        with self._lock:
            for subscriber in self._subscribers:
                subscriber.update(event_type, data)


class AnnouncementSystem:
    def update(self, event_type, data):
        if event_type == "TRAIN_DELAY":
            print(f"PA SYSTEM: Attention! Train {data['id']} is delayed by {data['minutes']} mins.")
        elif event_type == "EMERGENCY":
            print(f"PA SYSTEM: EMERGENCY! Please follow evacuation procedures.")

class SecurityOffice:
    def update(self, event_type, data):
        if event_type == "EMERGENCY":
            print(f"SECURITY: Dispatching officers to {data['location']} immediately!")


class Train(threading.Thread):
    def __init__(self, train_id, event_center, station):
        super().__init__()
        self.train_id = train_id
        self.event_center = event_center
        self.station = station
        self.capacity = 50
        self.current_passengers = []
        self.is_delayed = False

    def run(self):
        while True:
            travel_time = random.randint(3, 7)
            if self.is_delayed:
                travel_time += 10
            time.sleep(travel_time)

            print(f"Train {self.train_id} requesting platform at {self.station.name}...")

            with self.station.platform_lock:
                self.event_center.notify("TRAIN_ARRIVAL", {"id": self.train_id, "station": self.station.name})
                print(f"Train {self.train_id} is boarding at {self.station.name}.")
                time.sleep(3)

                self.event_center.notify("TRAIN_DEPARTURE", {"id": self.train_id})
            if random.random() < 0.1:
                self.trigger_random_delay()

    def trigger_random_delay(self):
        self.is_delayed = True
        self.event_center.notify("TRAIN_DELAY", {"id": self.train_id, "minutes": 15})
        time.sleep(5)
        self.is_delayed = False


if __name__ == "__main__":
    center = StationEventCenter()
    pa_system = AnnouncementSystem()
    security = SecurityOffice()
    center.subscribe(pa_system)
    center.subscribe(security)
    class MetroStation:
        def __init__(self, name):
            self.name = name
            self.platform_lock = threading.Lock()

    sol_station = MetroStation("Sol")
    train0 = Train("Line-10-A", center, sol_station)
    train1 = Train("Line-10-B", center, sol_station)

    print("Metro simulation starting")
    train0.start()
    train1.start()