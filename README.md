# OSPC-Metro-Simulation-2026N

## Overview
This project is a multi-threaded Python simulation of a high-traffic metro station ecosystem. It leverages Parallel Computing to model the concurrent interactions between autonomous trains, passengers, station facilities, and random emergency events.
The system specifically simulates the "fragility" of complex infrastructure, demonstrating how a single failure (like those seen on Madrid Metro Line 10) ripples through parallel subsystems.

## System Architecture & Design Patterns
To meet high-level software engineering standards, we implemented three core design patterns:
Observer Pattern: Managed by the StationEventCenter, allowing the AnnouncementSystem and SecurityOffice to react to events (delays/emergencies) without being tightly coupled to the Train class.
### State Pattern: Trains transition through Arriving, Boarding, Delayed, and Departing states, changing their behavior dynamically.
### Strategy Pattern: Passengers utilize different movement strategies (Normal, RushHour, Emergency) depending on the station environment.

## Parallelism & Synchronization
As a core requirement, the simulation handles concurrency using the following primitives:
### Mutex Locks (threading.Lock): Used for "Critical Sections" such as docking at the MetroStation platform and accessing the shared SimulationDBLogger.
### Atomic Transactions: The database uses WAL (Write-Ahead Logging) mode to ensure that multiple parallel threads can log events to SQLite simultaneously without data corruption.

## Data Analysis & Persistence
This version features a persistent data layer:
### SQLite Integration: Every event across multiple simulation runs is stored in metro_simulation.db for historical analysis.
### Automated Analytics: At the end of the simulation, the system uses Pandas and Matplotlib to generate 5 distinct visual reports:
_delays_per_run.png_ - Tracking system reliability over 20 iterations.
_passenger_throughput.png_ - Measuring station efficiency.
_delay_distribution.pn_g - Statistical spread of delay times.
_risk_analysis.png_ - Correlating machine failures with emergencies.
_throughput_vs_delays.png_ - Scatter plot analyzing the impact of delays on capacity.

## How to Run
### Install Dependencies:
pip install pandas numpy matplotlib

### Execute Simulation:
python main.py

### Simulation Parameters
**Runs**: 20 independent simulations.
**Threads per run**: 2 Trains, 2 Ticket Machines, 6+ Passengers, 1 Random Event System.
**Total Concurrent Threads**: 220 threads.
