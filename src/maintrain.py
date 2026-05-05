import threading
import random
import time


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

class OperatorPanel:
    def update(self, event_type, data):
        print(f"OPERATOR PANEL: [{event_type}] {data}")



###########
#passanger movement behavior

class NormalMovement:
    label = "normal"
    def move(self):
        time.sleep(random.uniform(0.8, 1.5))

class RushHourMovement:
    label = "rush-hour"
    def move(self):
        time.sleep(random.uniform(0.3, 0.6))

class EmergencyEvacuation:
    label = "emergency"
    def move(self):
        time.sleep(random.uniform(0.1, 0.3))


###########
#train states

class ArrivingState:
    def handle(self, train):
        print(f"Train {train.train_id} ARRIVING at {train.station.name}")
        time.sleep(0.5)
        train.state = BoardingState()

class BoardingState:
    def handle(self, train):
        print(f"Train {train.train_id} BOARDING passengers...")
        time.sleep(random.uniform(1.0, 2.0))
        if random.random() < 0.25:
            train.state = DelayedState()
        else:
            train.state = DepartingState()

class DelayedState:
    def handle(self, train):
        minutes = random.randint(3, 10)
        print(f"Train {train.train_id} DELAYED by {minutes} minutes!")
        train.event_center.notify("TRAIN_DELAY", {"id": train.train_id, "minutes": minutes})
        time.sleep(1.5)
        train.state = DepartingState()

class DepartingState:
    def handle(self, train):
        print(f"Train {train.train_id} DEPARTING from {train.station.name}")
        train.event_center.notify("TRAIN_DEPARTURE", {"id": train.train_id})



###########
#metro station
class MetroStation:
    def __init__(self, name):
        self.name = name
        self.platform_lock = threading.Lock()

###########
#train threads

class Train(threading.Thread):
    def __init__(self, train_id, event_center, station):
        super().__init__(daemon=True)
        self.train_id = train_id
        self.event_center = event_center
        self.station = station
        self.state = ArrivingState()

    def run(self):
        with self.station.platform_lock:
            while not isinstance(self.state, DepartingState):
                self.state.handle(self)
            self.state.handle(self)  # execute DepartingState

##########
#pasanger threads

class Passenger(threading.Thread):
    _ticket_lock = threading.Lock()

    def __init__(self, passenger_id, strategy, event_center):
        super().__init__(daemon=True)
        self.passenger_id = passenger_id
        self.strategy = strategy
        self.event_center = event_center

    def run(self):
        name = f"Passenger-{self.passenger_id}"
        with Passenger._ticket_lock:
            print(f"{name} buying ticket [{self.strategy.label}]...")
            time.sleep(random.uniform(0.3, 0.6))
        self.strategy.move()
        platform = random.randint(1, 4)
        print(f"{name} reached Platform {platform} and boarded the train")




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