import threading
import random
import time
import csv
import os
from datetime import datetime


###########
#CSV logger
class SimulationLogger:
    def __init__(self, filepath="simulation_log.csv"):
        self.filepath = filepath
        self._lock = threading.Lock()

        #file and write header
        with open(self.filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "category", "event", "detail"])

    def log(self, category, event, detail=""):
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        with self._lock:
            with open(self.filepath, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([ts, category, event, detail])

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
        train.logger.log("TRAIN", "ARRIVING", train.train_id)
        time.sleep(0.5)
        train.state = BoardingState()

class BoardingState:
    def handle(self, train):
        print(f"Train {train.train_id} BOARDING passengers...")
        train.logger.log("TRAIN", "BOARDING", train.train_id)
        time.sleep(random.uniform(1.0, 2.0))
        if random.random() < 0.25:
            train.state = DelayedState()
        else:
            train.state = DepartingState()

class DelayedState:
    def handle(self, train):
        minutes = random.randint(3, 10)
        print(f"Train {train.train_id} DELAYED by {minutes} minutes!")
        train.logger.log("TRAIN", "DELAYED", f"{train.train_id} — {minutes} min")
        train.event_center.notify("TRAIN_DELAY", {"id": train.train_id, "minutes": minutes})
        time.sleep(1.5)
        train.state = DepartingState()

class DepartingState:
    def handle(self, train):
        print(f"Train {train.train_id} DEPARTING from {train.station.name}")
        train.logger.log("TRAIN", "DEPARTED", train.train_id)
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
    def __init__(self, train_id, event_center, station, logger):
        super().__init__(daemon=True)
        self.train_id = train_id
        self.event_center = event_center
        self.station = station
        self.logger = logger
        self.state = ArrivingState()

    def run(self):
        with self.station.platform_lock:
            while not isinstance(self.state, DepartingState):
                self.state.handle(self)
            self.state.handle(self)

##########
#pasanger threads

class Passenger(threading.Thread):
    _ticket_lock = threading.Lock()

    def __init__(self, passenger_id, strategy, event_center, logger):
        super().__init__(daemon=True)
        self.passenger_id = passenger_id
        self.strategy = strategy
        self.event_center = event_center
        self.logger = logger

    def run(self):
        name = f"Passenger-{self.passenger_id}"
        with Passenger._ticket_lock:
            print(f"{name} buying ticket [{self.strategy.label}]...")
            self.logger.log("PASSENGER", "TICKET_BOUGHT", f"{name} [{self.strategy.label}]")
            time.sleep(random.uniform(0.3, 0.6))
        self.strategy.move()
        platform = random.randint(1, 4)
        print(f"{name} reached Platform {platform} and boarded the train")
        self.logger.log("PASSENGER", "BOARDED", f"{name} — Platform {platform}")
########
#ticket machine thread

class TicketMachine(threading.Thread):
    def __init__(self, machine_id, event_center, logger,cycles=3):
        super().__init__(daemon=True)
        self.machine_id = machine_id
        self.event_center = event_center
        self.cycles = cycles
        self.logger = logger

    def run(self):
        for i in range(self.cycles):
            time.sleep(random.uniform(0.5, 1.0))
            if random.random() < 0.15:
                print(f"Ticket Machine {self.machine_id} OUT OF SERVICE!")
                self.logger.log("MACHINE", "FAILURE", f"Machine {self.machine_id}")
                self.event_center.notify("EMERGENCY", {
                    "location": f"Ticket Machine {self.machine_id}"
                })
                time.sleep(1.5)
            else:
                print(f"Ticket Machine {self.machine_id} dispensed a card (cycle {i+1})")
                self.logger.log("MACHINE", "CARD_DISPENSED", f"Machine {self.machine_id} cycle {i + 1}")

############
#random event threads


class RandomEventSystem(threading.Thread):
    EVENTS = [
        {"type": "EMERGENCY", "location": "Entrance B — suspicious package"},
        {"type": "EMERGENCY", "location": "Platform 2 — medical emergency"},
        {"type": "EMERGENCY", "location": "South entrance — flooding"},
    ]

    def __init__(self, event_center, logger, num_events=2):
        super().__init__(daemon=True)
        self.event_center = event_center
        self.logger = logger
        self.num_events = num_events

    def run(self):
        chosen = random.sample(self.EVENTS, min(self.num_events, len(self.EVENTS)))
        for event in chosen:
            time.sleep(random.uniform(3.0, 6.0))
            print(f"\nRANDOM EVENT at {event['location']}")
            self.logger.log("EMERGENCY", "RANDOM_EVENT", event["location"])
            self.event_center.notify(event["type"], {"location": event["location"]})
            print()

#############
# MAIN


if __name__ == "__main__":
    logger = SimulationLogger("simulation-log.csv")

    center = StationEventCenter()

    center.subscribe(AnnouncementSystem())
    center.subscribe(SecurityOffice())
    center.subscribe(OperatorPanel())

    sol_station = MetroStation("Sol")
    strategies = [NormalMovement(), RushHourMovement(), EmergencyEvacuation()]

    threads = []
    threads.append(Train("Line-10-A", center, sol_station, logger))
    threads.append(Train("Line-10-B", center, sol_station, logger))
    threads.append(TicketMachine(1, center, logger))
    threads.append(TicketMachine(2, center, logger))
    for i in range(1, 7):
        threads.append(Passenger(i, random.choice(strategies), center, logger))
    threads.append(RandomEventSystem(center, logger, num_events=2))

    print("=" * 50)
    print("   MADRID METRO STATION SIMULATION")
    print("=" * 50)

    for t in threads:
        t.start()
        time.sleep(0.05)

    for t in threads:
        if isinstance(t, Train):
            t.join()

    time.sleep(4)
    print("\n" + "=" * 50)
    print("   SIMULATION COMPLETE")
    print(f"   Results saved to: simulation_log.csv")
    print("=" * 50)
