"""
SwiftTravel Bus Reservation System
-----------------------------------
A console-based bus reservation system built as a Python practice project.

Demonstrates: variables & data types, lists, dictionaries, tuples, sets,
conditions, loops, functions, string handling, built-in functions,
comprehensions, file handling, exception handling, and OOP.
"""

import json
import os

DATA_FILE = "swifttravel_data.json"


# ---------------------------------------------------------------------------
# OOP: Core classes
# ---------------------------------------------------------------------------

class Bus:
    """Represents a single bus journey/route."""

    def __init__(self, bus_id, source, destination, departure, arrival,
                 total_seats, fare):
        self.bus_id = bus_id
        self.route = (source, destination)          # tuple: fixed info
        self.departure = departure
        self.arrival = arrival
        self.total_seats = total_seats
        self.fare = fare
        # A set is used because a seat number can only ever appear once
        # in the "booked" collection - duplicate bookings are impossible.
        self.booked_seats = set()

    @property
    def available_seats(self):
        """Return a sorted list of seats that are not yet booked."""
        all_seats = set(range(1, self.total_seats + 1))
        return sorted(all_seats - self.booked_seats)

    def route_str(self):
        return f"{self.route[0]} -> {self.route[1]}"

    def to_dict(self):
        return {
            "bus_id": self.bus_id,
            "source": self.route[0],
            "destination": self.route[1],
            "departure": self.departure,
            "arrival": self.arrival,
            "total_seats": self.total_seats,
            "fare": self.fare,
            "booked_seats": sorted(self.booked_seats),
        }

    @classmethod
    def from_dict(cls, data):
        bus = cls(
            data["bus_id"], data["source"], data["destination"],
            data["departure"], data["arrival"],
            data["total_seats"], data["fare"],
        )
        bus.booked_seats = set(data.get("booked_seats", []))
        return bus


class Passenger:
    """Represents a passenger making a booking."""

    def __init__(self, name, age):
        self.name = name.strip().title()
        self.age = age

    def to_dict(self):
        return {"name": self.name, "age": self.age}

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["age"])


class Booking:
    """Represents a confirmed (or cancelled) ticket booking."""

    def __init__(self, booking_id, passenger, bus_id, seat, fare,
                 status="CONFIRMED"):
        self.booking_id = booking_id
        self.passenger = passenger          # Passenger object
        self.bus_id = bus_id
        self.seat = seat
        self.fare = fare
        self.status = status                # CONFIRMED / CANCELLED

    def to_dict(self):
        return {
            "booking_id": self.booking_id,
            "passenger": self.passenger.to_dict(),
            "bus_id": self.bus_id,
            "seat": self.seat,
            "fare": self.fare,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data):
        passenger = Passenger.from_dict(data["passenger"])
        return cls(
            data["booking_id"], passenger, data["bus_id"],
            data["seat"], data["fare"], data.get("status", "CONFIRMED"),
        )


class WaitingPassenger:
    """Represents a passenger waiting for a seat on a full bus."""

    def __init__(self, name, age, bus_id):
        self.name = name.strip().title()
        self.age = age
        self.bus_id = bus_id

    def to_dict(self):
        return {"name": self.name, "age": self.age, "bus_id": self.bus_id}

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["age"], data["bus_id"])


# ---------------------------------------------------------------------------
# Reservation system: holds all data + application logic
# ---------------------------------------------------------------------------

class ReservationSystem:
    def __init__(self):
        self.buses = {}          # bus_id -> Bus
        self.bookings = {}       # booking_id -> Booking
        self.waiting_list = []   # list of WaitingPassenger, in arrival order
        self.next_booking_number = 1001

    # -- setup ---------------------------------------------------------
    def seed_default_buses(self):
        """Create the default SwiftTravel buses if none were loaded."""
        self.buses["B101"] = Bus("B101", "Pune", "Mumbai",
                                  "08:00 AM", "12:00 PM", 10, 450)
        self.buses["B102"] = Bus("B102", "Pune", "Nashik",
                                  "09:30 AM", "01:00 PM", 12, 350)

    # -- file handling ---------------------------------------------------
    def save_data(self, filename=DATA_FILE):
        """Save all buses, bookings and the waiting list to a JSON file."""
        data = {
            "buses": [bus.to_dict() for bus in self.buses.values()],
            "bookings": [b.to_dict() for b in self.bookings.values()],
            "waiting_list": [w.to_dict() for w in self.waiting_list],
            "next_booking_number": self.next_booking_number,
        }
        try:
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Data saved to '{filename}'.")
        except (IOError, OSError) as e:
            print(f"Could not save data: {e}")

    def load_data(self, filename=DATA_FILE):
        """Load buses, bookings and waiting list from a JSON file.

        Returns True if existing data was loaded, False otherwise
        (e.g. first run, no file yet).
        """
        if not os.path.exists(filename):
            return False

        try:
            with open(filename, "r") as f:
                data = json.load(f)

            self.buses = {
                b["bus_id"]: Bus.from_dict(b) for b in data.get("buses", [])
            }
            self.bookings = {
                b["booking_id"]: Booking.from_dict(b)
                for b in data.get("bookings", [])
            }
            self.waiting_list = [
                WaitingPassenger.from_dict(w)
                for w in data.get("waiting_list", [])
            ]
            self.next_booking_number = data.get("next_booking_number", 1001)
            return True
        except (IOError, OSError, json.JSONDecodeError) as e:
            print(f"Could not load saved data ({e}). Starting fresh.")
            return False

    # -- helpers -----------------------------------------------------
    def generate_booking_id(self):
        booking_id = f"ST{self.next_booking_number}"
        self.next_booking_number += 1
        return booking_id

    def calculate_fare(self, base_fare, age):
        """Apply simple age-based discount rules to the base fare."""
        if age < 12:
            return round(base_fare * 0.5, 2)
        elif age >= 60:
            return round(base_fare * 0.7, 2)
        else:
            return base_fare

    def get_bus(self, bus_id):
        return self.buses.get(bus_id.strip().upper())

    # -- core features -------------------------------------------------
    def view_buses(self):
        print("\n" + "-" * 65)
        print(f"{'ID':<6}{'ROUTE':<20}{'TIME':<12}{'FARE':<10}{'SEATS':<6}")
        print("-" * 65)
        for bus in self.buses.values():
            seats_left = len(bus.available_seats)
            print(f"{bus.bus_id:<6}{bus.route_str():<20}{bus.departure:<12}"
                  f"{'Rs.' + str(bus.fare):<10}{seats_left:<6}")
        print("-" * 65)

    def view_seats(self, bus_id):
        bus = self.get_bus(bus_id)
        if not bus:
            print(f"No bus found with ID '{bus_id}'.")
            return

        print(f"\n BUS {bus.bus_id} ({bus.route_str()})")
        for seat in range(1, bus.total_seats + 1):
            marker = f"[{seat:02}]"
            end = "\n" if seat % 2 == 0 else " "
            print(marker, end=end)

        available = bus.available_seats
        booked = sorted(bus.booked_seats)
        avail_str = " ".join(f"{s:02}" for s in available) or "None"
        booked_str = " ".join(f"{s:02}" for s in booked) or "None"
        print(f"Available: {avail_str}")
        print(f"Booked: {booked_str}")

    def book_ticket(self, name, age, bus_id, seat):
        bus = self.get_bus(bus_id)
        if not bus:
            print(f"Journey '{bus_id}' does not exist.")
            return None

        if seat < 1 or seat > bus.total_seats:
            print(f"Seat {seat} is out of range for bus {bus.bus_id} "
                  f"(1-{bus.total_seats}).")
            return None

        if seat in bus.booked_seats:
            print(f"Seat {seat} is already booked. Please choose another.")
            return None

        passenger = Passenger(name, age)
        fare = self.calculate_fare(bus.fare, age)
        booking_id = self.generate_booking_id()
        booking = Booking(booking_id, passenger, bus.bus_id, seat, fare)

        bus.booked_seats.add(seat)
        self.bookings[booking_id] = booking

        print("\n" + "=" * 40)
        print(" BOOKING CONFIRMED")
        print("=" * 40)
        print(f"Booking ID : {booking.booking_id}")
        print(f"Passenger  : {passenger.name}")
        print(f"Journey    : {bus.bus_id}")
        print(f"Route      : {bus.route_str()}")
        print(f"Seat       : {seat:02}")
        print(f"Fare       : Rs.{fare}")
        print(f"Status     : {booking.status}")
        print("=" * 40)
        return booking

    def cancel_ticket(self, booking_id):
        booking = self.bookings.get(booking_id.strip().upper())
        if not booking:
            print(f"No booking found with ID '{booking_id}'.")
            return

        if booking.status == "CANCELLED":
            print(f"Booking {booking_id} is already cancelled.")
            return

        print("Booking found.")
        print(f"Passenger: {booking.passenger.name}")
        print(f"Seat: {booking.seat:02}")
        confirm = input("Cancel booking? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Cancellation aborted.")
            return

        booking.status = "CANCELLED"
        bus = self.get_bus(booking.bus_id)
        if bus and booking.seat in bus.booked_seats:
            bus.booked_seats.discard(booking.seat)

        print("Booking cancelled successfully.")
        print(f"Seat {booking.seat:02} is now available.")

        # --- Final Challenge: fill the freed seat from the waiting list ---
        self._assign_waiting_passengers(booking.bus_id)

    def _assign_waiting_passengers(self, bus_id):
        """
        When a seat frees up on a bus, pull the earliest matching waiting
        passenger(s) into confirmed bookings, in their original order,
        without disturbing passengers waiting for other buses.
        """
        bus = self.get_bus(bus_id)
        if not bus:
            return

        still_waiting = []
        for waiting_passenger in self.waiting_list:
            available = bus.available_seats
            if waiting_passenger.bus_id == bus_id and available:
                seat = available[0]
                print(f"\nAssigning waiting passenger "
                      f"'{waiting_passenger.name}' to freed seat "
                      f"{seat:02} on {bus_id}.")
                self.book_ticket(waiting_passenger.name,
                                  waiting_passenger.age, bus_id, seat)
            else:
                still_waiting.append(waiting_passenger)
        self.waiting_list = still_waiting

    def view_booking(self, booking_id):
        booking = self.bookings.get(booking_id.strip().upper())
        if not booking:
            print(f"No booking found with ID '{booking_id}'.")
            return

        bus = self.get_bus(booking.bus_id)
        route = bus.route_str() if bus else "Unknown"

        print("\n" + "=" * 40)
        print(" BOOKING DETAILS")
        print("=" * 40)
        print(f"Booking ID : {booking.booking_id}")
        print(f"Passenger  : {booking.passenger.name}")
        print(f"Journey    : {booking.bus_id}")
        print(f"Route      : {route}")
        print(f"Seat       : {booking.seat:02}")
        print(f"Fare       : Rs.{booking.fare}")
        print(f"Status     : {booking.status}")
        print("=" * 40)

    def search(self, query):
        """Search bookings by booking ID (exact) or passenger name
        (partial, case-insensitive)."""
        query = query.strip()
        exact = self.bookings.get(query.upper())
        if exact:
            results = [exact]
        else:
            q = query.lower()
            results = [
                b for b in self.bookings.values()
                if q in b.passenger.name.lower()
            ]

        if not results:
            print(f"No bookings found matching '{query}'.")
            return

        print("\nSearch Results")
        print("-" * 41)
        for b in results:
            print(f"Booking ID : {b.booking_id}")
            print(f"Passenger  : {b.passenger.name}")
            print(f"Journey    : {b.bus_id}")
            print(f"Seat       : {b.seat:02}")
            print(f"Status     : {b.status}")
            print("-" * 41)

    def join_waiting_list(self, name, age, bus_id):
        bus = self.get_bus(bus_id)
        if not bus:
            print(f"Journey '{bus_id}' does not exist.")
            return
        self.waiting_list.append(WaitingPassenger(name, age, bus.bus_id))
        position = sum(1 for w in self.waiting_list if w.bus_id == bus.bus_id)
        print(f"Bus {bus.bus_id} is full. Added to the waiting list "
              f"(position {position}).")


# ---------------------------------------------------------------------------
# Input helpers (exception handling around user input)
# ---------------------------------------------------------------------------

def read_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty. Please try again.")


def read_age(prompt="Enter age: "):
    while True:
        raw = input(prompt).strip()
        try:
            age = int(raw)
            if age <= 0 or age > 120:
                raise ValueError("out of range")
            return age
        except ValueError:
            print("Invalid input.")
            print("Age must be a number.")
            print("Please try again.")


def read_seat(prompt="Select seat: "):
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Invalid input. Seat number must be a whole number.")


# ---------------------------------------------------------------------------
# Menu / application flow
# ---------------------------------------------------------------------------

def display_menu():
    print("\n=====================================")
    print(" BUS RESERVATION SYSTEM - SwiftTravel")
    print("=====================================")
    print("1. View Buses")
    print("2. View Available Seats")
    print("3. Book Ticket")
    print("4. Cancel Ticket")
    print("5. View Booking")
    print("6. Search Passenger / Booking")
    print("7. Exit")


def handle_book_ticket(system):
    system.view_buses()
    name = read_nonempty("Enter passenger name: ")
    age = read_age()
    bus_id = read_nonempty("Enter journey ID: ").upper()

    bus = system.get_bus(bus_id)
    if not bus:
        print(f"Journey '{bus_id}' does not exist.")
        return

    if not bus.available_seats:
        print(f"Bus {bus_id} is fully booked.")
        choice = input("Join the waiting list instead? (yes/no): ").strip().lower()
        if choice == "yes":
            system.join_waiting_list(name, age, bus_id)
        return

    system.view_seats(bus_id)
    seat = read_seat()
    print("Processing booking...")
    system.book_ticket(name, age, bus_id, seat)


def handle_view_seats(system):
    bus_id = read_nonempty("Enter journey ID: ")
    system.view_seats(bus_id)


def handle_cancel_ticket(system):
    booking_id = read_nonempty("Enter Booking ID: ")
    system.cancel_ticket(booking_id)


def handle_view_booking(system):
    booking_id = read_nonempty("Enter Booking ID: ")
    system.view_booking(booking_id)


def handle_search(system):
    query = read_nonempty("Enter passenger name or booking ID: ")
    system.search(query)


def main():
    system = ReservationSystem()
    loaded = system.load_data()
    if not loaded:
        system.seed_default_buses()
        print("Welcome to SwiftTravel! Starting with default buses.")
    else:
        print("Welcome back to SwiftTravel! Loaded your saved data.")

    menu_actions = {
        "1": system.view_buses,
        "2": lambda: handle_view_seats(system),
        "3": lambda: handle_book_ticket(system),
        "4": lambda: handle_cancel_ticket(system),
        "5": lambda: handle_view_booking(system),
        "6": lambda: handle_search(system),
    }

    while True:
        display_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "7":
            system.save_data()
            print("Thank you for choosing SwiftTravel. Goodbye!")
            break
        elif choice in menu_actions:
            try:
                menu_actions[choice]()
            except Exception as e:
                # Catch-all so unexpected errors never crash the program
                print(f"Something went wrong: {e}")
        else:
            print("Invalid choice. Please select an option from 1 to 7.")


if __name__ == "__main__":
    main()
    
    