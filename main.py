rooms = [
    {"room_number": "101", "type": "Single", "price_per_night": 1200.0, "is_available": True},
    {"room_number": "102", "type": "Single", "price_per_night": 1200.0, "is_available": True},
    {"room_number": "103", "type": "Single", "price_per_night": 1200.0, "is_available": True},
    {"room_number": "201", "type": "Double", "price_per_night": 1800.0, "is_available": True},
    {"room_number": "202", "type": "Double", "price_per_night": 1800.0, "is_available": True},
    {"room_number": "203", "type": "Double", "price_per_night": 1800.0, "is_available": True},
    {"room_number": "301", "type": "Suite",  "price_per_night": 3500.0, "is_available": True},
    {"room_number": "302", "type": "Suite",  "price_per_night": 3500.0, "is_available": True},
    {"room_number": "401", "type": "Presidential Suite", "price_per_night": 7500.0, "is_available": True},
]

bookings = []
CURRENCY = "PHP "


def pause():
    input("\nPress [Enter] to return to the Main Menu...")


def print_divider(char="=", length=68):
    print(char * length)


def display_rooms():
    print_divider("=")
    print("                     HOTEL ROOM DIRECTORY")
    print_divider("=")
    print(f" {'Room No.':<10} | {'Room Type':<22} | {'Price / Night':<16} | {'Status':<12}")
    print_divider("-")

    available_count = 0
    occupied_count = 0

    for r in rooms:
        price_str = f"{CURRENCY}{r['price_per_night']:,.2f}"
        if r["is_available"]:
            status_str = "Available"
            available_count += 1
        else:
            status_str = "Occupied"
            occupied_count += 1

        print(f" {r['room_number']:<10} | {r['type']:<22} | {price_str:<16} | {status_str:<12}")

    print_divider("-")
    print(f" Summary: {available_count} Available  |  {occupied_count} Occupied  |  Total: {len(rooms)} Rooms")
    pause()


def book_room():
    print_divider("=")
    print("                      BOOK A ROOM")
    print_divider("=")

    has_available = any(r["is_available"] for r in rooms)
    if not has_available:
        print("\n [!] Sorry, all rooms are currently occupied!")
        pause()
        return

    print(" Available Rooms:")
    print(f" {'Room No.':<10} | {'Room Type':<22} | {'Price / Night':<16}")
    print_divider("-")
    for r in rooms:
        if r["is_available"]:
            price_str = f"{CURRENCY}{r['price_per_night']:,.2f}"
            print(f" {r['room_number']:<10} | {r['type']:<22} | {price_str:<16}")
    print_divider("-")
    print(" (Tip: Enter '0' at any prompt to cancel and return to menu)\n")

    while True:
        guest_name = input(" Enter your Name: ").strip()
        if guest_name == "0":
            print("\n Booking cancelled.")
            pause()
            return
        if not guest_name:
            print(" [!] Guest name cannot be empty. Please enter your name.")
            continue
        if any(char.isdigit() for char in guest_name):
            print(" [!] Error: Invalid Name! Guest name cannot contain numbers.")
            print("     Please fill it out correctly using letters only.")
            continue
        if not any(char.isalpha() for char in guest_name):
            print(" [!] Error: Invalid Name! Please enter a valid name with letters.")
            continue
        break

    selected_room = None
    while True:
        room_input = input(" Enter preferred Room Number: ").strip()
        if room_input == "0":
            print("\n Booking cancelled.")
            pause()
            return

        found_room = None
        for r in rooms:
            if r["room_number"].lower() == room_input.lower():
                found_room = r
                break

        if not found_room:
            print(f" [!] Error: Room '{room_input}' does not exist! Please choose a room from the list above.")
            continue

        if not found_room["is_available"]:
            print(f" [!] Error: Room {found_room['room_number']} is ALREADY OCCUPIED! Please choose another room.")
            continue

        selected_room = found_room
        break

    while True:
        nights_str = input(" Enter Number of Nights: ").strip()
        if nights_str == "0":
            print("\n Booking cancelled.")
            pause()
            return

        try:
            nights = int(nights_str)
            if nights <= 0:
                print(" [!] Number of nights must be at least 1.")
                continue
            break
        except ValueError:
            print(" [!] Invalid input! Please enter a valid whole number for nights (e.g., 1, 2, 3).")

    price_night = selected_room["price_per_night"]
    total_cost = price_night * nights

    selected_room["is_available"] = False

    new_booking = {
        "guest_name": guest_name,
        "room_number": selected_room["room_number"],
        "nights": nights,
        "total_cost": total_cost
    }
    bookings.append(new_booking)

    print("\n" + "=" * 68)
    print("                   BOOKING CONFIRMATION")
    print("=" * 68)
    print(f" Guest Name       : {guest_name}")
    print(f" Room Number      : {selected_room['room_number']} ({selected_room['type']})")
    print(f" Rate per Night   : {CURRENCY}{price_night:,.2f}")
    print(f" Number of Nights : {nights}")
    print(f" Total Price      : {CURRENCY}{total_cost:,.2f}")
    print("=" * 68)
    print(" [SUCCESS] Room successfully booked and status set to Occupied!")
    pause()


def view_bookings():
    print_divider("=")
    print("                    ACTIVE RESERVATIONS")
    print_divider("=")

    if not bookings:
        print("\n  There are no active bookings at the moment.")
    else:
        print(f" {'#':<4} | {'Guest Name':<20} | {'Room #':<8} | {'Nights':<8} | {'Total Cost':<16}")
        print_divider("-")
        for index, b in enumerate(bookings, start=1):
            total_str = f"{CURRENCY}{b['total_cost']:,.2f}"
            print(f" {index:<4} | {b['guest_name']:<20} | {b['room_number']:<8} | {b['nights']:<8} | {total_str:<16}")
        print_divider("-")
        print(f" Total Active Bookings: {len(bookings)}")

    pause()


def checkout_room():
    print_divider("=")
    print("             CHECKOUT / CANCEL RESERVATION")
    print_divider("=")

    if not bookings:
        print("\n  No active reservations to checkout or cancel.")
        pause()
        return

    print(" Current Active Bookings:")
    print(f" {'#':<4} | {'Guest Name':<20} | {'Room #':<8} | {'Total Cost':<16}")
    print_divider("-")
    for index, b in enumerate(bookings, start=1):
        total_str = f"{CURRENCY}{b['total_cost']:,.2f}"
        print(f" {index:<4} | {b['guest_name']:<20} | {b['room_number']:<8} | {total_str:<16}")
    print_divider("-")
    print(" (Enter '0' to cancel and return to menu)\n")

    target_booking = None
    while True:
        lookup = input(" Enter Room Number or Guest Name to clear: ").strip()
        if lookup == "0":
            print("\n Operation cancelled.")
            pause()
            return

        matched = [
            b for b in bookings
            if b["room_number"].lower() == lookup.lower()
            or b["guest_name"].lower() == lookup.lower()
        ]

        if not matched:
            print(f" [!] No reservation found for '{lookup}'. Please try again.")
            continue

        target_booking = matched[0]
        break

    print("\n Selected Reservation:")
    print(f"   Guest Name  : {target_booking['guest_name']}")
    print(f"   Room Number : {target_booking['room_number']}")
    print(f"   Nights      : {target_booking['nights']}")
    print(f"   Total Cost  : {CURRENCY}{target_booking['total_cost']:,.2f}")

    confirm = input("\n Confirm checkout/cancellation? (y/n): ").strip().lower()
    if confirm not in ("y", "yes"):
        print("\n Checkout cancelled. No changes made.")
        pause()
        return

    for r in rooms:
        if r["room_number"] == target_booking["room_number"]:
            r["is_available"] = True
            break

    bookings.remove(target_booking)

    print("\n" + "=" * 68)
    print("                 CHECKOUT SUCCESSFUL")
    print("=" * 68)
    print(f" Room {target_booking['room_number']} is now AVAILABLE.")
    print(f" Reservation for '{target_booking['guest_name']}' has been cleared.")
    print("=" * 68)
    pause()


def main():
    while True:
        print("\n" + "=" * 68)
        print("          HOTEL RESERVATION SYSTEM - MAIN MENU")
        print("=" * 68)
        print("  1. View Rooms (Available & Occupied)")
        print("  2. Book a Room")
        print("  3. View Bookings")
        print("  4. Checkout / Cancel Reservation")
        print("  5. Exit")
        print("  6. Launch Modern GUI Window")
        print("=" * 68)

        raw_choice = input(" Enter your choice (1-6): ").strip()

        try:
            choice = int(raw_choice)
        except ValueError:
            print("\n [!] Error: Invalid input! You entered letters or symbols.")
            print("     Please enter a valid number (1-6).")
            pause()
            continue

        if choice == 1:
            display_rooms()
        elif choice == 2:
            book_room()
        elif choice == 3:
            view_bookings()
        elif choice == 4:
            checkout_room()
        elif choice == 5:
            print("\n" + "=" * 68)
            print("   Thank you for using the Hotel Reservation System!")
            print("                     Goodbye!")
            print("=" * 68 + "\n")
            break
        elif choice == 6:
            print("\n Launching Modern Graphical User Interface (GUI)...")
            try:
                from gui import launch_gui
                launch_gui()
            except Exception as e:
                print(f" [!] Error launching GUI: {e}")
                pause()
        else:
            print(f"\n [!] Choice {choice} is out of range! Please choose between 1 and 6.")
            pause()


if __name__ == "__main__":
    import sys
    if "--cli" in sys.argv:
        main()
    else:
        try:
            from gui import launch_gui
            launch_gui()
        except Exception as err:
            print(f"Notice: Could not start GUI ({err}). Launching terminal interface...\n")
            main()

