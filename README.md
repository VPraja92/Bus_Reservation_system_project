# Bus_Reservation_system_project
# Bus Reservation System

A console-based bus reservation system built in Python, demonstrating object-oriented design, thoughtful data structure choices, and file persistence.

## Overview

This project simulates a real-world bus booking workflow — viewing buses and seats, booking and cancelling tickets, searching bookings, and managing a waiting list — all through a simple menu-driven console interface, with bookings persisted to disk between sessions.

## Architecture

The system is built around four core classes, coordinated by a central `ReservationSystem` class that holds all application logic and state:

- **`Bus`** — represents a bus, its route, and seat availability
- **`Passenger`** — represents a passenger's details
- **`Booking`** — represents a confirmed ticket, linking a passenger to a bus and seat
- **`WaitingPassenger`** — represents a passenger queued for a seat on a full bus
- **`ReservationSystem`** — orchestrates the menu, bookings, cancellations, search, and waitlist logic

## Features

- **Menu-driven flow**: view buses, view seats, book a ticket, cancel a booking, view booking details, search, exit
- **Fare rules**: automatic discounts based on age
  - Under 12 → 50% off
  - 12–59 → full fare
  - 60+ → 30% off
- **Auto-generated booking IDs**: sequential format (`ST1001`, `ST1002`, ...)
- **Search**: look up by exact booking ID or partial passenger name match
- **Persistent storage**: bookings are saved to and loaded from JSON, so data survives a restart
- **Input validation**: age and seat inputs are validated with retry loops, and a catch-all exception handler wraps menu actions so invalid input never crashes the program

## Data Structures

Each structure was chosen to match how the data is actually accessed:

| Structure | Used for | Why |
|---|---|---|
| Tuple | Route data | Fixed, unchanging values |
| Set | Booked seats | Fast membership checks |
| Dict | Bookings, buses | Fast key-based lookup |
| List | Waiting queue | Preserves insertion order |

## Highlight: Automatic Waitlist Promotion

The core challenge tackled in this project: when a booking is cancelled, the freed seat is automatically offered to the earliest matching passenger on the waiting list, in order — no manual intervention required.

This was tested directly by filling a bus to capacity, cancelling two seats, and confirming the correct waiting passengers were pulled in the right order. The logic was run through several additional test scenarios, all of which passed.

## Tech Stack

- Python (standard library only — no external dependencies)
- JSON for data persistence

## Getting Started

```bash
# Clone the repository
git clone <your-repo-url>
cd <repo-folder>

# Run the program
python main.py
```

> Update `main.py` above with the actual entry-point filename for your project.

## Usage

On launch, you'll be presented with a menu:

```
1. View Buses
2. View Seats
3. Book a Ticket
4. Cancel a Booking
5. View Booking
6. Search
7. Exit
```

Bookings are automatically saved to a JSON file after each change, so your data will be there the next time you run the program.

## Project Status

Actively developed as a learning project focused on OOP principles, data structure selection, and file handling in Python.

## License

Add your preferred license here (e.g. MIT).
