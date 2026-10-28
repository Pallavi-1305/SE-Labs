
"""Manage movie seat reservations and ticket codes."""

import hashlib
import json

# Global state
shows = {
    "SHOW-1": {"title": "Interstellar", "seats": 20, "booked": []},
    "SHOW-2": {"title": "Dangal", "seats": 10, "booked": []},
}


def reserve_seat(show_id, seat_number, system_logs=None):
    """Reserve a seat and record the result."""
    if system_logs is None:
        system_logs = []

    if show_id not in shows:
        system_logs.append(f"Unknown show: {show_id}")
        return False

    show = shows[show_id]

    if (
        not isinstance(seat_number, int)
        or isinstance(seat_number, bool)
        or not 1 <= seat_number <= show["seats"]
    ):
        system_logs.append(f"Invalid seat number: {seat_number}")
        return False

    if seat_number in show["booked"]:
        system_logs.append(
            f"Seat {seat_number} already taken for {show_id}"
        )
        return False

    show["booked"].append(seat_number)
    system_logs.append(f"Reserved seat {seat_number} for {show_id}")
    return True


def release_seat(show_id, seat_number):
    """Release a previously reserved seat."""
    if show_id not in shows:
        return False

    try:
        shows[show_id]["booked"].remove(seat_number)
    except ValueError:
        return False

    return True


def ticket_code(show_id, seat_number):
    """Generate a short ticket identifier."""
    ticket_data = f"{show_id}:{seat_number}".encode("utf-8")
    return hashlib.sha256(ticket_data).hexdigest()[:8]


def dump_reservations(file="seats.json"):
    """Save reservations to a JSON file."""
    with open(file, "w", encoding="utf-8") as reservation_file:
        json.dump(shows, reservation_file, indent=4)


def load_reservations(file="seats.json"):
    """Load reservations from a JSON file."""
    try:
        with open(file, "r", encoding="utf-8") as reservation_file:
            data = json.load(reservation_file)
        if isinstance(data, dict):
            shows.clear()
            shows.update(data)
    except (OSError, json.JSONDecodeError):
        print("Could not load reservation data.")


def print_seating_summary():
    """Display the available and booked seats for each show."""
    for show in shows.values():
        free = show["seats"] - len(show["booked"])
        print(
            f'{show["title"]}: {free} seats free, '
            f'booked = {show["booked"]}'
        )


def main():
    """Run a sample reservation workflow."""
    reserve_seat("SHOW-1", 5)
    reserve_seat("SHOW-1", 5)
    reserve_seat("SHOW-1", 25)
    reserve_seat("SHOW-2", -1)
    reserve_seat("SHOW-2", "A7")
    release_seat("SHOW-2", 3)

    print("Ticket code:", ticket_code("SHOW-1", 5))
    seat_input = input(
        "Seat number to book for SHOW-2 (Enter for 4): "
    ).strip()
    seat = int(seat_input) if seat_input.isdigit() else 4

    reserve_seat("SHOW-2", seat)
    dump_reservations()
    load_reservations()
    print_seating_summary()


if __name__ == "__main__":
    main()
