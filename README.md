# Hotel Reservation System (1st Year BSIT Python Project)

A complete **Hotel Reservation System** built strictly in Python featuring both a **Modern Graphical User Interface (GUI)** and an interactive **Terminal / CLI interface**. It strictly follows the **Project Concept & Scope**, **Data Structure Plan** (memory-based, no external database required), and **Step-by-Step Development Plan** guidelines.

---

## 🎨 Graphical User Interface (GUI) Overview

The modern desktop GUI is built with Python's standard library **Tkinter** and **ttk** (zero external dependencies needed):

1. 📊 **Dashboard Overview**:
   - 4 Live Metric Cards: **Total Rooms**, **Available Rooms**, **Occupied Rooms**, and **Total Revenue (PHP)**.
   - Recent Reservations table and one-click quick action shortcuts.
2. 🛏️ **Room Directory & Inventory**:
   - Complete room catalogue with live status badges (🟢 **Available** / 🔴 **Occupied**) and occupant names.
   - Filter dropdowns: filter by status (*Available Only*, *Occupied Only*) or by tier (*Single*, *Double*, *Suite*, *Presidential Suite*).
   - One-click **"Book Selected Room"** and double-click shortcuts.
3. 📝 **Interactive Room Booking**:
   - **Guest Name Validation**: Rejects numbers and special symbols (letters only) in real time.
   - **Dynamic Room Picker**: Shows available rooms with prices.
   - **Nights Stepper**: Increment (`+`) and decrement (`-`) buttons with numeric validation.
   - **Live Price Preview**: Automatically computes rate per night, duration, and grand total in Philippine Peso (`PHP`).
   - **Pop-up Receipt**: Displays an official modal confirmation receipt upon booking.
4. 📋 **Active Bookings & Search**:
   - Live search filter: instantly filter reservations by **Guest Name** or **Room Number** as you type.
   - Detailed Treeview table with sorting and aligned columns.
   - **View Receipt**: Re-inspect formatted receipts for any existing reservation.
5. 🚪 **Checkout & Room Clearing**:
   - Displays full billing and stay breakdown.
   - Confirmation dialog preventing accidental cancellations.
   - Immediately restores room status to **Available** and updates metrics across all screens.

---

## 📌 1. Project Concept & Scope

The application provides both GUI and Terminal interfaces sharing the exact same in-memory data:

1. **Main Menu**: Clean loop keeping the program running until the user exits.
2. **View Rooms**: Displays rooms showing number, type, price per night (PHP), and status (`Available` or `Occupied`).
3. **Book a Room**: Asks for guest name (letters only, no numbers allowed), room number, and number of nights. Calculates total price (`price_night * nights`), sets room status to occupied (`False`), and records the booking.
4. **View Bookings**: Displays a summary of all active reservations.
5. **Checkout / Cancel Reservation**: Clears a booking and resets the room's availability back to `True`.
6. **GUI / CLI Interoperability**: Seamlessly switch between GUI and Terminal modes.

---

## 🗂️ 2. Data Structure Plan (No Database Required)

Stored purely in memory while the program runs:

| Data Type | Variable Name | Description & Keys |
| :--- | :--- | :--- |
| **List of Dictionaries** | `rooms` | Stores: `room_number`, `type`, `price_per_night`, and `is_available` (`True` / `False`). |
| **List of Dictionaries** | `bookings` | Stores: `guest_name`, `room_number`, `nights`, and `total_cost`. |

### Room Inventory & Rates (Philippine Peso - PHP):
- **Single Rooms** (`101`, `102`, `103`): `PHP 1,200.00` / night
- **Double Rooms** (`201`, `202`, `203`): `PHP 1,800.00` / night
- **Suite Rooms** (`301`, `302`): `PHP 3,500.00` / night
- **Presidential Suite** (`401`): `PHP 7,500.00` / night

---

## 🛠️ 3. Step-by-Step Development Plan Alignment

### Phase 1: Initialize Data and Setup the Main Loop
- Initialized sample room inventory in `rooms` using a list of dictionaries.
- Implemented `while True` loop and event-driven Tkinter window loop.
- Uses `if-elif-else` control flow to direct user selections.

### Phase 2: Build the Core Functions & GUI Views
- **`display_rooms()`** & **GUI Room Directory**: Formatted text & responsive Treeview showing room availability.
- **`book_room()`** & **GUI Booking Form**:
  - Validates guest name contains **letters only** (no numbers allowed).
  - Checks if the room exists and is currently available.
  - Asks for number of nights and calculates total price (`price_night * nights`).
  - Sets room status to occupied (`is_available = False`) and saves transaction to `bookings`.
- **`view_bookings()`** & **GUI Active Bookings**: Formatted listing & searchable reservation table.
- **`checkout_room()`** & **GUI Checkout Page**: Clears reservation from `bookings` and restores room status to `is_available = True`.

### Phase 3: Testing and Validation (Edge Cases Handled)
- **Names containing numbers**: Automatically rejected if the user inputs any numbers/digits (e.g., `John123`, `Gabriel 2`); prompts the user to enter letters only until filled out correctly.
- **Non-existent room number**: Checks if room number exists; if not, alerts the user without crashing and allows them to pick again.
- **Already taken room**: Checks `if not room["is_available"]`; informs the user the room is already occupied.
- **Typing letters instead of numbers**: Protected with `try-except ValueError` blocks for menu choices and nights inputs so the program never crashes.


## 🚀 How to Run the Program

### Option A: Launch Modern GUI (Recommended)
Double-click [**`run_gui.bat`**](file:///c:/Users/Gabriel/OneDrive/Documents/Hotel-Reservation/run_gui.bat) or run:
```bash
python gui.py
```
*(Or double-click [**`run.bat`**](file:///c:/Users/Gabriel/OneDrive/Documents/Hotel-Reservation/run.bat), which launches the GUI by default)*

### Option B: Launch Terminal / CLI Mode
Double-click [**`run_cli.bat`**](file:///c:/Users/Gabriel/OneDrive/Documents/Hotel-Reservation/run_cli.bat) or run:
```bash
python main.py --cli


