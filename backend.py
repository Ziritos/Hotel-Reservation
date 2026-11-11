"""
Sugo Grand Palace Hotel - Backend Core & API Engine
Maintains rooms, bookings, customer profiles, persistence, and the Flask/PyWebView bridge.
Frontend templates & static assets are located in the 'views/' directory.
"""

import json
import os
import random
import re
import sys
import threading
import time
import webbrowser
from datetime import date, datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIEWS_DIR = os.path.join(BASE_DIR, "views")
ASSETS_DIR = os.path.join(VIEWS_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "hotel_data.json")

os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

CURRENCY = "PHP "
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "svg", "gif"}

# Default Room Inventory matching project scope with local asset illustrations
DEFAULT_ROOMS = [
    {
        "room_number": "101",
        "type": "Single",
        "price_per_night": 1200.0,
        "is_available": True,
        "capacity": 1,
        "bed_type": "1 Single Bed",
        "size": "20 sqm",
        "image_url": "/assets/room_single.jpg",
        "amenities": ["High-speed Wi-Fi", "Air Conditioning", "Hot & Cold Shower", "Flat-screen TV", "Work Desk"],
        "description": "Cozy and comfortable private room perfect for solo travelers, business trips, or students."
    },
    {
        "room_number": "102",
        "type": "Single",
        "price_per_night": 1200.0,
        "is_available": True,
        "capacity": 1,
        "bed_type": "1 Single Bed",
        "size": "20 sqm",
        "image_url": "/assets/room_single_2.jpg",
        "amenities": ["High-speed Wi-Fi", "Air Conditioning", "Hot & Cold Shower", "Flat-screen TV", "Work Desk"],
        "description": "Quiet inner-wing single room designed for maximum relaxation, privacy, and restful sleep."
    },
    {
        "room_number": "103",
        "type": "Single",
        "price_per_night": 1200.0,
        "is_available": True,
        "capacity": 1,
        "bed_type": "1 Single Bed",
        "size": "22 sqm",
        "image_url": "/assets/room_single.jpg",
        "amenities": ["High-speed Wi-Fi", "Air Conditioning", "Hot & Cold Shower", "Flat-screen TV", "Work Desk", "Window View"],
        "description": "Bright single room with natural sunlight, ergonomic desk, and fast optical internet."
    },
    {
        "room_number": "201",
        "type": "Double",
        "price_per_night": 1800.0,
        "is_available": True,
        "capacity": 2,
        "bed_type": "1 Queen Bed",
        "size": "32 sqm",
        "image_url": "/assets/room_double.jpg",
        "amenities": ["High-speed Wi-Fi", "Air Conditioning", "Hot & Cold Shower", "Smart TV", "Mini Refrigerator", "City View"],
        "description": "Spacious double bedroom featuring premium orthopedic mattress, city panorama, and mini fridge."
    },
    {
        "room_number": "202",
        "type": "Double",
        "price_per_night": 1800.0,
        "is_available": True,
        "capacity": 2,
        "bed_type": "2 Twin Beds",
        "size": "32 sqm",
        "image_url": "/assets/room_double_2.jpg",
        "amenities": ["High-speed Wi-Fi", "Air Conditioning", "Hot & Cold Shower", "Smart TV", "Mini Refrigerator", "Coffee Maker"],
        "description": "Modern twin bed setup ideal for companions, colleagues, or siblings visiting the city."
    },
    {
        "room_number": "203",
        "type": "Double",
        "price_per_night": 1800.0,
        "is_available": True,
        "capacity": 2,
        "bed_type": "1 Queen Bed",
        "size": "34 sqm",
        "image_url": "/assets/room_double.jpg",
        "amenities": ["High-speed Wi-Fi", "Air Conditioning", "Hot & Cold Shower", "Smart TV", "Mini Refrigerator", "Corner View"],
        "description": "Premium corner double room with dual windows, ambient warm lighting, and seating area."
    },
    {
        "room_number": "301",
        "type": "Suite",
        "price_per_night": 3500.0,
        "is_available": True,
        "capacity": 4,
        "bed_type": "1 King Bed + Sofa Bed",
        "size": "55 sqm",
        "image_url": "/assets/room_suite.jpg",
        "amenities": ["High-speed Wi-Fi", "Smart TV & Soundbar", "Private Balcony", "Kitchenette & Mini Bar", "Complimentary Breakfast", "Bathtub"],
        "description": "Luxurious executive suite with separated living room, deep soaking bathtub, and skyline balcony."
    },
    {
        "room_number": "302",
        "type": "Suite",
        "price_per_night": 3500.0,
        "is_available": True,
        "capacity": 4,
        "bed_type": "1 King Bed + Daybed",
        "size": "58 sqm",
        "image_url": "/assets/room_suite.jpg",
        "amenities": ["High-speed Wi-Fi", "Smart TV & Soundbar", "Private Balcony", "Kitchenette & Mini Bar", "Complimentary Breakfast", "Bathtub"],
        "description": "Grand family suite with dining corner, premium streaming entertainment, and complimentary breakfast."
    },
    {
        "room_number": "401",
        "type": "Presidential Suite",
        "price_per_night": 7500.0,
        "is_available": True,
        "capacity": 6,
        "bed_type": "2 Master King Beds",
        "size": "110 sqm",
        "image_url": "/assets/room_presidential.jpg",
        "amenities": ["Private Elevator Access", "Panoramic Skyline View", "Personal Butler Service", "Jacuzzi & Spa Bath", "Complimentary Gourmet Breakfast", "Private Bar & Lounge"],
        "description": "The pinnacle of luxury: penthouse floor, full jacuzzi spa bath, 360-degree city view, and VIP concierge."
    },
]

# ---------------------------------------------------------
# In-Memory Transaction Data Structure
# ---------------------------------------------------------

class Transaction:
    """Represents an atomic hotel financial and operational transaction record."""

    def __init__(
        self,
        transaction_id: str,
        transaction_type: str,  # 'BOOKING_RESERVATION', 'CHECKOUT_SETTLED', 'CANCELLATION_REFUND'
        booking_id: str,
        guest_name: str,
        room_number: str,
        amount: float,
        status: str = "Completed",
        payment_method: str = "Credit / Debit Card",
        notes: str = "",
        timestamp: str = None,
    ):
        self.transaction_id = transaction_id
        self.transaction_type = transaction_type
        self.booking_id = booking_id
        self.guest_name = guest_name
        self.room_number = str(room_number)
        self.amount = float(amount)
        self.status = status
        self.payment_method = payment_method
        self.notes = notes
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "transaction_type": self.transaction_type,
            "booking_id": self.booking_id,
            "guest_name": self.guest_name,
            "room_number": self.room_number,
            "amount": self.amount,
            "status": self.status,
            "payment_method": self.payment_method,
            "notes": self.notes,
            "timestamp": self.timestamp,
        }


class TransactionLedger:
    """
    High-Performance In-Memory Data Structure for Hotel Transactions.
    Maintains dual hashing indexes and chronological sequence for O(1) lookups:
      - Chronological list: self._transactions
      - Hash Map Index by Transaction ID (O(1) lookup): self._by_id
      - Hash Map Index by Booking Reference (O(1) lookup): self._by_booking
      - Hash Map Index by Guest Name (O(1) lookup): self._by_guest
      - Hash Map Index by Room Number (O(1) lookup): self._by_room
    """

    def __init__(self):
        self._transactions: list[Transaction] = []
        self._by_id: dict[str, Transaction] = {}
        self._by_booking: dict[str, list[Transaction]] = {}
        self._by_guest: dict[str, list[Transaction]] = {}
        self._by_room: dict[str, list[Transaction]] = {}

    def record(
        self,
        txn_type: str,
        booking_id: str,
        guest_name: str,
        room_number: str,
        amount: float,
        status: str = "Completed",
        payment_method: str = "Credit / Debit Card",
        notes: str = "",
        timestamp: str = None,
        txn_id: str = None,
    ) -> Transaction:
        if not txn_id:
            txn_id = f"TXN-{random.randint(100000, 999999)}"

        txn = Transaction(
            transaction_id=txn_id,
            transaction_type=txn_type,
            booking_id=booking_id,
            guest_name=guest_name,
            room_number=room_number,
            amount=amount,
            status=status,
            payment_method=payment_method,
            notes=notes,
            timestamp=timestamp,
        )

        # 1. Primary chronological storage
        self._transactions.append(txn)
        # 2. Hash map index by Transaction ID (O(1))
        self._by_id[txn.transaction_id] = txn
        # 3. Multi-index by Booking ID (O(1))
        b_key = txn.booking_id.strip().upper()
        self._by_booking.setdefault(b_key, []).append(txn)
        # 4. Multi-index by Guest Name (O(1))
        g_key = txn.guest_name.strip().lower()
        self._by_guest.setdefault(g_key, []).append(txn)
        # 5. Multi-index by Room Number (O(1))
        r_key = str(txn.room_number).strip()
        self._by_room.setdefault(r_key, []).append(txn)

        return txn

    def get_all(self, reverse: bool = True) -> list[dict]:
        txns = self._transactions[::-1] if reverse else self._transactions
        return [t.to_dict() for t in txns]

    def get_by_id(self, txn_id: str) -> dict | None:
        t = self._by_id.get(str(txn_id).strip().upper())
        return t.to_dict() if t else None

    def get_by_booking(self, booking_id: str) -> list[dict]:
        records = self._by_booking.get(str(booking_id).strip().upper(), [])
        return [t.to_dict() for t in records]

    def get_by_guest(self, guest_name: str) -> list[dict]:
        records = self._by_guest.get(str(guest_name).strip().lower(), [])
        return [t.to_dict() for t in records]

    def get_by_room(self, room_number: str) -> list[dict]:
        records = self._by_room.get(str(room_number).strip(), [])
        return [t.to_dict() for t in records]

    def get_metrics(self) -> dict:
        total_txns = len(self._transactions)
        total_credits = sum(t.amount for t in self._transactions if "REFUND" not in t.transaction_type)
        total_refunds = sum(t.amount for t in self._transactions if "REFUND" in t.transaction_type)
        net_revenue = total_credits - total_refunds

        breakdown = {}
        for t in self._transactions:
            breakdown[t.transaction_type] = breakdown.get(t.transaction_type, 0) + 1

        return {
            "total_count": total_txns,
            "gross_volume": total_credits,
            "total_refunds": total_refunds,
            "net_revenue": net_revenue,
            "breakdown": breakdown,
        }

    def load_from_list(self, raw_list: list[dict]):
        self.clear()
        for d in raw_list:
            self.record(
                txn_type=d.get("transaction_type", "BOOKING_RESERVATION"),
                booking_id=d.get("booking_id", ""),
                guest_name=d.get("guest_name", ""),
                room_number=d.get("room_number", ""),
                amount=float(d.get("amount", 0.0)),
                status=d.get("status", "Completed"),
                payment_method=d.get("payment_method", "Credit / Debit Card"),
                notes=d.get("notes", ""),
                timestamp=d.get("timestamp"),
                txn_id=d.get("transaction_id"),
            )

    def clear(self):
        self._transactions.clear()
        self._by_id.clear()
        self._by_booking.clear()
        self._by_guest.clear()
        self._by_room.clear()


# In-Memory Datastores
rooms = []
bookings = []
customers = []
transaction_ledger = TransactionLedger()
hotel_settings = {
    "hotel_name": "Sugo Grand Palace Hotel",
    "logo_url": "/assets/logo.svg",
}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_default_room_image(room_type: str) -> str:
    t = (room_type or "").lower()
    if "presidential" in t:
        return "/assets/room_presidential.svg"
    elif "suite" in t:
        return "/assets/room_suite.svg"
    elif "double" in t:
        return "/assets/room_double.svg"
    else:
        return "/assets/room_single.svg"


def generate_booking_id() -> str:
    return f"SH-{random.randint(1000, 9999)}"


def validate_guest_name(name: str) -> tuple[bool, str]:
    cleaned = (name or "").strip()
    if not cleaned:
        return False, "Guest name cannot be empty. Please enter your name."
    if any(char.isdigit() for char in cleaned):
        return False, "Invalid Name! Guest name cannot contain numbers (letters only)."
    if not any(char.isalpha() for char in cleaned):
        return False, "Invalid Name! Please enter a valid name containing letters."
    if len(cleaned) < 2:
        return False, "Guest name must be at least 2 characters long."
    return True, ""


def validate_nights(nights_val) -> tuple[bool, str, int]:
    try:
        n = int(nights_val)
        if n < 1:
            return False, "Number of nights must be at least 1.", 0
        if n > 90:
            return False, "Maximum stay duration is 90 nights per reservation.", 0
        return True, "", n
    except (ValueError, TypeError):
        return False, "Invalid nights input! Please enter a whole number (e.g., 1, 2, 3).", 0


def get_room(room_number: str):
    target = str(room_number).strip().lower()
    for r in rooms:
        if str(r["room_number"]).strip().lower() == target:
            return r
    return None


def get_booking_by_id(booking_id: str):
    target = str(booking_id).strip().upper()
    for b in bookings:
        if b.get("booking_id", "").strip().upper() == target:
            return b
    return None


def update_or_create_customer(name: str, email: str = "", phone: str = "", booking_cost: float = 0.0, booking_id: str = ""):
    name_clean = name.strip()
    customer = None

    for c in customers:
        if email and c.get("email") and c["email"].lower() == email.lower():
            customer = c
            break
        if phone and c.get("phone") and c["phone"] == phone:
            customer = c
            break
        if c["name"].lower() == name_clean.lower():
            customer = c
            break

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    if customer:
        if email and not customer.get("email"):
            customer["email"] = email
        if phone and not customer.get("phone"):
            customer["phone"] = phone
        if booking_id and booking_id not in customer.get("bookings", []):
            customer.setdefault("bookings", []).append(booking_id)
        customer["total_spent"] = customer.get("total_spent", 0.0) + booking_cost
        customer["total_stays"] = len(customer.get("bookings", []))
        customer["last_visit"] = now_str
    else:
        customer = {
            "customer_id": f"CUST-{random.randint(1000, 9999)}",
            "name": name_clean,
            "email": email.strip() if email else "",
            "phone": phone.strip() if phone else "",
            "bookings": [booking_id] if booking_id else [],
            "total_stays": 1 if booking_id else 0,
            "total_spent": booking_cost,
            "member_since": now_str,
            "last_visit": now_str,
        }
        customers.append(customer)

    spent = customer.get("total_spent", 0.0)
    if spent >= 15000:
        customer["tier"] = "VIP Platinum"
    elif spent >= 5000:
        customer["tier"] = "Gold Member"
    else:
        customer["tier"] = "Standard Guest"

    return customer


def parse_date_str(d_str: str) -> date | None:
    """Safely parse date from YYYY-MM-DD or ISO timestamp strings."""
    if not d_str:
        return None
    d_clean = str(d_str).strip()
    if len(d_clean) >= 10:
        d_clean = d_clean[:10]
    try:
        return datetime.strptime(d_clean, "%Y-%m-%d").date()
    except Exception:
        try:
            return datetime.fromisoformat(d_clean).date()
        except Exception:
            return None


def dates_overlap(start_a: date, end_a: date, start_b: date, end_b: date) -> bool:
    """
    Returns True if stay periods [start_a, end_a) and [start_b, end_b) overlap.
    Check-out day allows same-day check-in for the next arriving guest (half-open interval).
    """
    return max(start_a, start_b) < min(end_a, end_b)


def check_room_availability_for_dates(
    room_number: str,
    check_in_date: date,
    check_out_date: date,
    exclude_booking_id: str | None = None,
) -> tuple[bool, str, dict | None]:
    """
    Checks if the specified room is available for the date range [check_in_date, check_out_date).
    Returns (is_available, message, conflicting_booking).
    """
    r_target = str(room_number).strip()
    for b in bookings:
        if str(b.get("room_number", "")).strip() != r_target:
            continue
        if b.get("status") in ("Checked Out", "Cancelled"):
            continue
        if exclude_booking_id and str(b.get("booking_id", "")).strip() == str(exclude_booking_id).strip():
            continue

        b_in = parse_date_str(b.get("check_in"))
        b_out = parse_date_str(b.get("check_out"))
        if not b_in:
            continue
        if not b_out:
            b_out = b_in + timedelta(days=int(b.get("nights", 1)))

        if dates_overlap(check_in_date, check_out_date, b_in, b_out):
            msg = (
                f"Suite {room_number} is already booked from {b.get('check_in')} to {b.get('check_out')} "
                f"by {b.get('guest_name')} (Ref: {b.get('booking_id')}). "
                f"Please choose different dates or another suite."
            )
            return False, msg, b

    return True, f"Suite {room_number} is available for selected stay dates.", None


def book_room(
    guest_name: str,
    room_number: str,
    nights: int,
    email: str = "",
    phone: str = "",
    check_in: str = "",
    guests_count: int = 1,
    special_requests: str = "",
) -> tuple[bool, str, dict]:
    valid_name, err_name = validate_guest_name(guest_name)
    if not valid_name:
        return False, err_name, {}

    valid_nights_flag, err_nights, parsed_nights = validate_nights(nights)
    if not valid_nights_flag:
        return False, err_nights, {}

    room = get_room(room_number)
    if not room:
        return False, f"Room '{room_number}' does not exist! Please choose a valid room.", {}

    # Parse and validate requested check-in and check-out dates
    if not check_in:
        req_in_date = date.today()
        check_in_str = req_in_date.strftime("%Y-%m-%d")
    else:
        check_in_str = str(check_in).strip()
        parsed_in = parse_date_str(check_in_str)
        if not parsed_in:
            return False, f"Invalid check-in date '{check_in}'. Please enter a valid date in YYYY-MM-DD format.", {}
        req_in_date = parsed_in

    req_out_date = req_in_date + timedelta(days=parsed_nights)
    check_out_str = req_out_date.strftime("%Y-%m-%d")

    # Verify that the room has no overlapping confirmed reservations
    is_avail, clash_msg, _ = check_room_availability_for_dates(
        room_number=str(room["room_number"]),
        check_in_date=req_in_date,
        check_out_date=req_out_date,
    )
    if not is_avail:
        return False, clash_msg, {}

    price_night = float(room["price_per_night"])
    total_cost = price_night * parsed_nights

    booking_id = generate_booking_id()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    new_booking = {
        "booking_id": booking_id,
        "guest_name": guest_name.strip(),
        "email": email.strip(),
        "phone": phone.strip(),
        "room_number": str(room["room_number"]),
        "room_type": room.get("type", "Standard"),
        "nights": parsed_nights,
        "check_in": check_in_str,
        "check_out": check_out_str,
        "guests_count": int(guests_count) if guests_count else 1,
        "special_requests": (special_requests or "").strip(),
        "price_per_night": price_night,
        "total_cost": total_cost,
        "created_at": created_at,
        "status": "Confirmed",
    }

    bookings.append(new_booking)
    update_or_create_customer(
        name=guest_name,
        email=email,
        phone=phone,
        booking_cost=total_cost,
        booking_id=booking_id
    )

    # In-memory transaction data structure registration
    transaction_ledger.record(
        txn_type="BOOKING_RESERVATION",
        booking_id=booking_id,
        guest_name=guest_name.strip(),
        room_number=str(room["room_number"]),
        amount=total_cost,
        status="Completed",
        payment_method="Credit / Debit Card",
        notes=f"Stay: {parsed_nights} night(s) ({check_in_str} to {check_out_str})",
        timestamp=created_at,
    )

    get_metrics()
    save_data()
    return True, "Booking confirmed successfully!", new_booking


def checkout_booking(booking_or_id_or_room: str) -> tuple[bool, str, dict]:
    query = str(booking_or_id_or_room).strip()
    target_booking = None

    for b in bookings:
        if b.get("booking_id", "").strip().upper() == query.upper():
            target_booking = b
            break

    if not target_booking:
        for b in bookings:
            if str(b.get("room_number", "")).strip().lower() == query.lower():
                target_booking = b
                break

    if not target_booking:
        for b in bookings:
            if b.get("guest_name", "").strip().lower() == query.lower():
                target_booking = b
                break

    if not target_booking:
        return False, f"No active reservation found matching '{query}'.", {}

    room = get_room(target_booking["room_number"])
    if room:
        room["is_available"] = True

    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target_booking["status"] = "Checked Out"
    target_booking["checked_out_at"] = now_ts

    # In-memory transaction registration for check-out settlement
    transaction_ledger.record(
        txn_type="CHECKOUT_SETTLED",
        booking_id=target_booking.get("booking_id", ""),
        guest_name=target_booking.get("guest_name", ""),
        room_number=target_booking.get("room_number", ""),
        amount=float(target_booking.get("total_cost", 0.0)),
        status="Settled",
        payment_method="Booking Settlement",
        notes=f"Checked out from Suite {target_booking.get('room_number')}. Room cleared.",
        timestamp=now_ts,
    )

    bookings.remove(target_booking)
    get_metrics()
    save_data()
    return True, f"Guest '{target_booking['guest_name']}' checked out. Room {target_booking['room_number']} is now Available.", target_booking


def cancel_booking_by_customer(booking_id: str, guest_name: str) -> tuple[bool, str]:
    booking = get_booking_by_id(booking_id)
    if not booking:
        return False, f"Reservation with reference ID '{booking_id}' was not found."

    if booking["guest_name"].strip().lower() != guest_name.strip().lower():
        return False, "Verification failed: Name does not match the reservation record."

    room = get_room(booking["room_number"])
    if room:
        room["is_available"] = True

    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # In-memory transaction registration for cancellation refund
    transaction_ledger.record(
        txn_type="CANCELLATION_REFUND",
        booking_id=booking.get("booking_id", ""),
        guest_name=booking.get("guest_name", ""),
        room_number=booking.get("room_number", ""),
        amount=float(booking.get("total_cost", 0.0)),
        status="Refunded",
        payment_method="Refund to Source",
        notes=f"Guest cancellation. Suite {booking.get('room_number')} returned to inventory.",
        timestamp=now_ts,
    )

    bookings.remove(booking)
    get_metrics()
    save_data()
    return True, f"Reservation {booking_id} has been successfully cancelled."


def cancel_booking_by_staff(booking_id: str, reason: str = "") -> tuple[bool, str]:
    booking = get_booking_by_id(booking_id)
    if not booking:
        return False, f"Reservation with reference ID '{booking_id}' was not found."

    room = get_room(booking["room_number"])
    if room:
        room["is_available"] = True

    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # In-memory transaction registration for front desk cancellation
    transaction_ledger.record(
        txn_type="CANCELLATION_REFUND",
        booking_id=booking.get("booking_id", ""),
        guest_name=booking.get("guest_name", ""),
        room_number=booking.get("room_number", ""),
        amount=float(booking.get("total_cost", 0.0)),
        status="Refunded",
        payment_method="Front Desk Void / Refund",
        notes=f"Staff cancellation: {reason or 'Cancelled by Front Desk'}. Suite {booking.get('room_number')} returned to inventory.",
        timestamp=now_ts,
    )

    bookings.remove(booking)
    get_metrics()
    save_data()
    return True, f"Reservation {booking_id} for '{booking['guest_name']}' was successfully cancelled. Room {booking['room_number']} is now available clean."


def update_booking_by_staff(
    booking_id: str,
    guest_name: str,
    nights: int,
    check_in: str = "",
    room_number: str = "",
    phone: str = "",
    email: str = "",
    special_requests: str = "",
) -> tuple[bool, str, dict]:
    booking = get_booking_by_id(booking_id)
    if not booking:
        return False, f"Reservation with reference ID '{booking_id}' was not found.", {}

    valid_name, err_name = validate_guest_name(guest_name)
    if not valid_name:
        return False, err_name, {}

    valid_nights_flag, err_nights, parsed_nights = validate_nights(nights)
    if not valid_nights_flag:
        return False, err_nights, {}

    target_room_number = str(room_number).strip() if room_number else str(booking["room_number"])
    target_room = get_room(target_room_number)
    if not target_room:
        return False, f"Room '{target_room_number}' does not exist.", {}

    # Determine updated stay dates
    if check_in:
        parsed_in = parse_date_str(check_in)
        if not parsed_in:
            return False, f"Invalid check-in date '{check_in}'. Please use YYYY-MM-DD format.", {}
        new_in_date = parsed_in
    else:
        new_in_date = parse_date_str(booking.get("check_in")) or date.today()

    new_out_date = new_in_date + timedelta(days=parsed_nights)

    # Check date overlap for target room (excluding this booking itself)
    is_avail, clash_msg, _ = check_room_availability_for_dates(
        room_number=target_room_number,
        check_in_date=new_in_date,
        check_out_date=new_out_date,
        exclude_booking_id=booking_id,
    )
    if not is_avail:
        return False, clash_msg, {}

    # Apply changes
    booking["room_number"] = str(target_room["room_number"])
    booking["room_type"] = target_room.get("type", "Standard")
    booking["price_per_night"] = float(target_room["price_per_night"])
    booking["nights"] = parsed_nights
    booking["check_in"] = new_in_date.strftime("%Y-%m-%d")
    booking["check_out"] = new_out_date.strftime("%Y-%m-%d")

    # Recalculate cost
    rate = float(booking.get("price_per_night", 1200.0))
    booking["total_cost"] = round(rate * parsed_nights, 2)

    # Update guest contact information
    booking["guest_name"] = guest_name.strip()
    if phone is not None:
        booking["phone"] = phone.strip()
    if email is not None:
        booking["email"] = email.strip()
    if special_requests is not None:
        booking["special_requests"] = special_requests.strip()

    # Update customer profile in CRM
    update_or_create_customer(
        name=booking["guest_name"],
        email=booking.get("email", ""),
        phone=booking.get("phone", ""),
        booking_cost=booking["total_cost"],
        booking_id=booking_id,
    )

    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transaction_ledger.record(
        txn_type="BOOKING_UPDATED",
        booking_id=booking_id,
        guest_name=booking["guest_name"],
        room_number=booking["room_number"],
        amount=booking["total_cost"],
        status="Completed",
        payment_method="Front Desk Modification",
        notes=f"Updated by Front Desk: Suite {booking['room_number']}, {parsed_nights} night(s), Total: ₱{booking['total_cost']:,.2f}",
        timestamp=now_ts,
    )

    get_metrics()
    save_data()
    return True, f"Reservation {booking_id} for '{booking['guest_name']}' has been updated successfully!", booking


def search_customer_reservations(lookup: str) -> list[dict]:
    clean_q = lookup.strip().lower()
    if not clean_q:
        return []

    results = []
    for b in bookings:
        if (
            clean_q in b.get("booking_id", "").lower()
            or clean_q in b.get("guest_name", "").lower()
            or clean_q in b.get("phone", "").lower()
            or clean_q in b.get("email", "").lower()
            or clean_q == str(b.get("room_number", "")).lower()
        ):
            results.append(b)
    return results


def update_room_image(room_number: str, image_url: str) -> bool:
    room = get_room(room_number)
    if room:
        room["image_url"] = image_url.strip()
        save_data()
        return True
    return False


def set_hotel_logo(logo_url: str):
    hotel_settings["logo_url"] = logo_url.strip()
    save_data()


def get_metrics() -> dict:
    total_rooms = len(rooms)
    today_dt = date.today()

    # Rooms currently occupied by in-house guests today
    occupied_today_room_nos = set()
    for b in bookings:
        if b.get("status") in ("Checked Out", "Cancelled"):
            continue
        b_in = parse_date_str(b.get("check_in"))
        b_out = parse_date_str(b.get("check_out"))
        if not b_in:
            continue
        if not b_out:
            b_out = b_in + timedelta(days=int(b.get("nights", 1)))

        # In-house: guest stay covers today until checkout is processed
        if b_in <= today_dt <= b_out:
            occupied_today_room_nos.add(str(b.get("room_number", "")).strip())
        elif b_in <= today_dt and b.get("status") in ("Confirmed", "Checked In"):
            occupied_today_room_nos.add(str(b.get("room_number", "")).strip())

    # Set real-time daily availability for rooms catalog
    for r in rooms:
        r_num = str(r.get("room_number", "")).strip()
        r["is_available"] = (r_num not in occupied_today_room_nos)

    occupied_count = len(occupied_today_room_nos)
    available_count = total_rooms - occupied_count
    total_revenue = sum(
        float(b.get("total_cost", 0.0))
        for b in bookings
        if b.get("status") not in ("Cancelled",)
    )
    occupancy_rate = (occupied_count / total_rooms * 100) if total_rooms > 0 else 0.0

    active_bookings_count = sum(
        1 for b in bookings if b.get("status") not in ("Checked Out", "Cancelled")
    )

    return {
        "total_rooms": total_rooms,
        "available_rooms": available_count,
        "occupied_rooms": occupied_count,
        "occupancy_rate": round(occupancy_rate, 1),
        "total_revenue": total_revenue,
        "active_bookings_count": active_bookings_count,
        "total_customers": len(customers),
    }


def save_data():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        payload = {
            "rooms": rooms,
            "bookings": bookings,
            "customers": customers,
            "hotel_settings": hotel_settings,
            "transactions": transaction_ledger.get_all(reverse=False),
            "last_updated": datetime.now().isoformat(),
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except Exception:
        pass


def reset_system_to_beginning(persist: bool = True):
    """
    Resets the hotel reservation system to Day 1:
      - All 9 suites are Available Clean and ready for check-in
      - 0 in-house guests / active stays
      - 0 CRM customer records
      - ₱0.00 revenue
      - Empty transaction ledger
    """
    global rooms, bookings, customers, transaction_ledger
    rooms.clear()
    for r in DEFAULT_ROOMS:
        room_dict = dict(r)
        room_dict["is_available"] = True
        rooms.append(room_dict)

    bookings.clear()
    customers.clear()
    transaction_ledger.clear()

    if persist:
        save_data()


def load_data():
    """
    Called when running the system:
    Starts fresh at the beginning with zero guests, zero revenue, and all 9 rooms available clean.
    Preserves custom hotel branding/logo settings if present.
    """
    global hotel_settings

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("hotel_settings"):
                    hotel_settings.update(data["hotel_settings"])
        except Exception:
            pass

    # Start fresh from the beginning with zero guests and zero revenue
    reset_system_to_beginning(persist=True)


# Initialize data on startup (Fresh start: 0 guests, zero revenue)
load_data()


# ---------------------------------------------------------
# Flask Web Engine (Configured for 'views/' folder)
# ---------------------------------------------------------

app = Flask(
    __name__,
    template_folder=VIEWS_DIR,
    static_folder=VIEWS_DIR,
    static_url_path="",
)
app.secret_key = os.environ.get("SECRET_KEY", "sugo-grand-palace-front-desk-key-2026")


@app.context_processor
def inject_global_context():
    return {
        "currency": CURRENCY,
        "today_str": date.today().strftime("%Y-%m-%d"),
        "all_rooms": rooms,
        "hotel_settings": hotel_settings,
    }


@app.route("/")
def root_index():
    """Default entry point: start on the login portal."""
    return redirect(url_for("login_page"))


@app.route("/rooms")
@app.route("/customer")
@app.route("/guest")
def guest_page():
    query = request.args.get("query", "").strip()
    tab = request.args.get("tab", "").strip()
    results = []
    if query:
        results = search_customer_reservations(query)
        tab = "lookup"
    elif not tab:
        tab = "rooms"

    metrics = get_metrics()
    today_str = date.today().strftime("%Y-%m-%d")
    return render_template(
        "guest.html",
        active_tab=tab,
        query=query,
        results=results,
        metrics=metrics,
        rooms=rooms,
        bookings=bookings,
        today_str=today_str,
    )


@app.route("/login")
def login_page():
    if request.args.get("role") == "receptionist":
        return redirect(url_for("receptionist_login_page"))
    return render_template("login.html")


@app.route("/receptionist/login", methods=["GET", "POST"])
@app.route("/login/receptionist", methods=["GET", "POST"])
def receptionist_login_page():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please enter both your username and password.", "danger")
            return redirect(url_for("receptionist_login_page"))

        # Strict Front Desk credential authentication
        AUTHORIZED_STAFF = {
            "receptionist": "frontdesk2026",
            "frontdesk": "frontdesk2026",
        }

        if username.lower() in AUTHORIZED_STAFF and AUTHORIZED_STAFF[username.lower()] == password:
            session["receptionist_logged_in"] = True
            session["receptionist_user"] = username
            flash(f"Welcome, {username}! Front Desk Console ready.", "success")
            return redirect(url_for("receptionist_dashboard"))
        else:
            flash("Access Denied: Invalid username or password.", "danger")
            return redirect(url_for("receptionist_login_page"))

    return render_template("login_receptionist.html")


@app.route("/receptionist/logout")
@app.route("/logout/receptionist")
def receptionist_logout():
    session.pop("receptionist_logged_in", None)
    session.pop("receptionist_user", None)
    flash("✔ You have signed out of the Front Desk Console.", "info")
    return redirect(url_for("receptionist_login_page"))


@app.route("/book", methods=["POST"])
def book_room_route():
    guest_name = request.form.get("guest_name", "").strip()
    room_number = request.form.get("room_number", "").strip()
    nights_raw = request.form.get("nights", "1").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    check_in = request.form.get("check_in", "").strip()
    guests_count = request.form.get("guests_count", "1").strip()
    special_requests = request.form.get("special_requests", "").strip()

    try:
        nights = int(nights_raw)
    except ValueError:
        flash("Invalid number of nights! Please enter a whole number.", "danger")
        return redirect(url_for("guest_page"))

    success, message, new_booking = book_room(
        guest_name=guest_name,
        room_number=room_number,
        nights=nights,
        email=email,
        phone=phone,
        check_in=check_in,
        guests_count=guests_count,
        special_requests=special_requests,
    )

    if not success:
        flash(f"Booking Failed: {message}", "danger")
        return redirect(url_for("guest_page"))

    flash(f"Success! Suite {room_number} reserved for {guest_name}. Confirmation Code: {new_booking['booking_id']}", "success")
    return redirect(url_for("guest_page", tab="lookup", query=new_booking["booking_id"]))


@app.route("/my-booking")
def my_booking_page():
    query = request.args.get("query", "").strip()
    if query:
        return redirect(url_for("guest_page", tab="lookup", query=query))
    return redirect(url_for("guest_page", tab="lookup"))


@app.route("/my-booking/cancel", methods=["POST"])
def cancel_my_booking_route():
    booking_id = request.form.get("booking_id", "").strip()
    guest_name = request.form.get("guest_name", "").strip()
    if not booking_id or not guest_name:
        flash("Missing cancellation details.", "danger")
        return redirect(url_for("guest_page", tab="lookup"))

    success, msg = cancel_booking_by_customer(booking_id, guest_name)
    flash(f"✔ {msg}" if success else f"[!] {msg}", "success" if success else "danger")
    return redirect(url_for("guest_page", tab="lookup", query=booking_id))


@app.route("/confirmation/<booking_id>")
def confirmation_page(booking_id):
    booking = get_booking_by_id(booking_id)
    if not booking:
        flash(f"Reservation '{booking_id}' not found.", "warning")
        return redirect(url_for("guest_page", tab="lookup"))
    return redirect(url_for("guest_page", tab="lookup", query=booking_id))


@app.route("/receptionist")
def receptionist_dashboard():
    if not session.get("receptionist_logged_in"):
        flash("Please sign in to access the Front Desk Receptionist Console.", "danger")
        return redirect(url_for("receptionist_login_page"))

    metrics = get_metrics()
    all_transactions = transaction_ledger.get_all(reverse=True)
    txn_metrics = transaction_ledger.get_metrics()
    today_str = date.today().strftime("%Y-%m-%d")
    return render_template(
        "receptionist.html",
        metrics=metrics,
        rooms=rooms,
        bookings=bookings,
        customers=customers,
        transactions=all_transactions,
        txn_metrics=txn_metrics,
        today_str=today_str,
    )


@app.route("/receptionist/reset-system", methods=["POST"])
def receptionist_reset_system_route():
    if not session.get("receptionist_logged_in"):
        flash("Please sign in as authorized staff to reset the system.", "danger")
        return redirect(url_for("receptionist_login_page"))

    reset_system_to_beginning(persist=True)
    flash("✔ System refreshed to Day 1: All 9 suites are available clean, zero in-house guests, and ₱0.00 revenue.", "success")
    return redirect(url_for("receptionist_dashboard"))


@app.route("/receptionist/checkout", methods=["POST"])
def receptionist_checkout_route():
    if not session.get("receptionist_logged_in"):
        flash("Please sign in as authorized staff to process check-outs.", "danger")
        return redirect(url_for("receptionist_login_page"))

    booking_id = request.form.get("booking_id", "").strip()
    if not booking_id:
        flash("No reservation specified for checkout.", "danger")
        return redirect(url_for("receptionist_dashboard"))

    success, msg, _ = checkout_booking(booking_id)
    flash(f"✔ {msg}" if success else f"[!] {msg}", "success" if success else "danger")
    return redirect(request.referrer or url_for("receptionist_dashboard"))


@app.route("/receptionist/booking/add", methods=["POST"])
def receptionist_add_booking_route():
    """Allows authorized staff to add new reservations directly from the console."""
    if not session.get("receptionist_logged_in"):
        flash("Please sign in as authorized staff to create reservations.", "danger")
        return redirect(url_for("receptionist_login_page"))

    guest_name = request.form.get("guest_name", "").strip()
    room_number = request.form.get("room_number", "").strip()
    nights_raw = request.form.get("nights", "1").strip()
    check_in = request.form.get("check_in", "").strip()
    guests_count = request.form.get("guests_count", "1").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    special_requests = request.form.get("special_requests", "").strip()

    try:
        nights = int(nights_raw)
    except ValueError:
        flash("Invalid number of nights! Please enter a whole number.", "danger")
        return redirect(url_for("receptionist_dashboard"))

    success, msg, new_b = book_room(
        guest_name=guest_name,
        room_number=room_number,
        nights=nights,
        email=email,
        phone=phone,
        check_in=check_in,
        guests_count=guests_count,
        special_requests=special_requests,
    )

    if success:
        flash(f"✔ New Reservation confirmed: Booking {new_b.get('booking_id')} for {new_b.get('guest_name')} in Suite {new_b.get('room_number')}.", "success")
    else:
        flash(f"[!] Booking Failed: {msg}", "danger")

    return redirect(url_for("receptionist_dashboard"))


@app.route("/receptionist/booking/update", methods=["POST"])
def receptionist_update_booking_route():
    """Allows authorized staff to edit and update existing reservations."""
    if not session.get("receptionist_logged_in"):
        flash("Please sign in as authorized staff to update reservations.", "danger")
        return redirect(url_for("receptionist_login_page"))

    booking_id = request.form.get("booking_id", "").strip()
    guest_name = request.form.get("guest_name", "").strip()
    room_number = request.form.get("room_number", "").strip()
    nights_raw = request.form.get("nights", "1").strip()
    check_in = request.form.get("check_in", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    special_requests = request.form.get("special_requests", "").strip()

    try:
        nights = int(nights_raw)
    except ValueError:
        flash("Invalid number of nights! Please enter a whole number.", "danger")
        return redirect(url_for("receptionist_dashboard"))

    success, msg, _ = update_booking_by_staff(
        booking_id=booking_id,
        guest_name=guest_name,
        nights=nights,
        check_in=check_in,
        room_number=room_number,
        phone=phone,
        email=email,
        special_requests=special_requests,
    )

    flash(f"✔ {msg}" if success else f"[!] {msg}", "success" if success else "danger")
    return redirect(url_for("receptionist_dashboard"))


@app.route("/receptionist/booking/cancel", methods=["POST"])
def receptionist_cancel_booking_route():
    """Allows authorized staff to cancel reservations and return rooms to clean inventory."""
    if not session.get("receptionist_logged_in"):
        flash("Please sign in as authorized staff to cancel reservations.", "danger")
        return redirect(url_for("receptionist_login_page"))

    booking_id = request.form.get("booking_id", "").strip()
    reason = request.form.get("reason", "").strip()

    if not booking_id:
        flash("No reservation reference provided for cancellation.", "danger")
        return redirect(url_for("receptionist_dashboard"))

    success, msg = cancel_booking_by_staff(booking_id, reason)
    flash(f"✔ {msg}" if success else f"[!] {msg}", "success" if success else "danger")
    return redirect(url_for("receptionist_dashboard"))


@app.route("/receptionist/booking/<booking_id>/details", methods=["GET"])
def receptionist_get_booking_json_route(booking_id):
    """API endpoint for fetching booking details for receptionist modal dialogs."""
    if not session.get("receptionist_logged_in"):
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    b = get_booking_by_id(booking_id)
    if not b:
        return jsonify({"success": False, "error": "Booking not found"}), 404

    return jsonify({"success": True, "booking": b})


@app.route("/receptionist/room/<room_number>/update-image", methods=["POST"])
def update_room_image_route(room_number):
    uploaded_file = request.files.get("room_image_file")
    image_url_input = request.form.get("room_image_url", "").strip()

    final_image_url = None

    if uploaded_file and uploaded_file.filename:
        if allowed_file(uploaded_file.filename):
            ext = uploaded_file.filename.rsplit(".", 1)[1].lower()
            safe_name = f"room_{room_number}_{int(datetime.now().timestamp())}.{ext}"
            save_path = os.path.join(ASSETS_DIR, safe_name)
            uploaded_file.save(save_path)
            final_image_url = f"/assets/{safe_name}"
        else:
            flash(f"Invalid image format! Allowed types: {', '.join(ALLOWED_EXTENSIONS)}", "danger")
            return redirect(request.referrer or url_for("receptionist_dashboard"))
    elif image_url_input:
        final_image_url = image_url_input

    if final_image_url:
        update_room_image(room_number, final_image_url)
        flash(f"✔ Suite {room_number} photo updated successfully!", "success")
    else:
        flash("Please upload an image file or provide a valid image URL.", "warning")

    return redirect(request.referrer or url_for("receptionist_dashboard"))


@app.route("/receptionist/upload-logo", methods=["POST"])
def upload_logo_route():
    uploaded_file = request.files.get("logo_file")
    logo_url_input = request.form.get("logo_url", "").strip()

    final_logo_url = None

    if uploaded_file and uploaded_file.filename:
        if allowed_file(uploaded_file.filename):
            ext = uploaded_file.filename.rsplit(".", 1)[1].lower()
            safe_name = f"logo_{int(datetime.now().timestamp())}.{ext}"
            save_path = os.path.join(ASSETS_DIR, safe_name)
            uploaded_file.save(save_path)
            final_logo_url = f"/assets/{safe_name}"
        else:
            flash(f"Invalid logo file format! Allowed: {', '.join(ALLOWED_EXTENSIONS)}", "danger")
            return redirect(request.referrer or url_for("receptionist_dashboard"))
    elif logo_url_input:
        final_logo_url = logo_url_input

    if final_logo_url:
        set_hotel_logo(final_logo_url)
        flash("✔ Property logo updated successfully!", "success")
    else:
        flash("Please select a logo file or enter a valid logo URL.", "warning")

    return redirect(request.referrer or url_for("receptionist_dashboard"))


# REST API endpoints
@app.route("/api/rooms", methods=["GET"])
def api_get_rooms():
    return jsonify({"status": "success", "rooms": rooms})


@app.route("/api/metrics", methods=["GET"])
def api_get_metrics():
    return jsonify({"status": "success", "metrics": get_metrics()})


@app.route("/api/book", methods=["POST"])
def api_book():
    data = request.get_json() or {}
    success, message, new_b = book_room(
        guest_name=data.get("guest_name", ""),
        room_number=data.get("room_number", ""),
        nights=data.get("nights", 1),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        check_in=data.get("check_in", ""),
        guests_count=data.get("guests_count", 1),
        special_requests=data.get("special_requests", ""),
    )
    if not success:
        return jsonify({"status": "error", "message": message}), 400
    return jsonify({"status": "success", "booking": new_b})


@app.route("/api/checkout", methods=["POST"])
def api_checkout():
    data = request.get_json() or {}
    target = data.get("booking_id") or data.get("room_number") or ""
    success, message, b = checkout_booking(target)
    if not success:
        return jsonify({"status": "error", "message": message}), 400
    return jsonify({"status": "success", "message": message, "booking": b})


@app.route("/api/transactions", methods=["GET"])
def api_get_transactions():
    booking_id = request.args.get("booking_id")
    guest_name = request.args.get("guest_name")
    room_number = request.args.get("room_number")

    if booking_id:
        txns = transaction_ledger.get_by_booking(booking_id)
    elif guest_name:
        txns = transaction_ledger.get_by_guest(guest_name)
    elif room_number:
        txns = transaction_ledger.get_by_room(room_number)
    else:
        txns = transaction_ledger.get_all(reverse=True)

    return jsonify({
        "status": "success",
        "count": len(txns),
        "transactions": txns,
        "metrics": transaction_ledger.get_metrics(),
    })


@app.route("/api/transactions/<txn_id>", methods=["GET"])
def api_get_transaction_by_id(txn_id):
    txn = transaction_ledger.get_by_id(txn_id)
    if not txn:
        return jsonify({"status": "error", "message": f"Transaction '{txn_id}' not found."}), 404
    return jsonify({"status": "success", "transaction": txn})


@app.route("/api/reset", methods=["POST"])
def api_reset_system():
    reset_system_to_beginning(persist=True)
    return jsonify({
        "status": "success",
        "message": "Hotel system reset to Day 1: 0 guests, ₱0.00 revenue, 9 suites available clean.",
        "metrics": get_metrics(),
    })


# ---------------------------------------------------------
# PyWebView Bridge API Class
# ---------------------------------------------------------

class HotelBackendAPI:
    """Python API exposed directly to JavaScript via pywebview."""

    def get_rooms(self):
        return rooms

    def get_metrics(self):
        return get_metrics()

    def get_bookings(self):
        return bookings

    def get_customers(self):
        return customers

    def get_transactions(self):
        return transaction_ledger.get_all()

    def get_transaction_metrics(self):
        return transaction_ledger.get_metrics()

    def book_room(self, guest_name, room_number, nights, email="", phone=""):
        success, message, b = book_room(
            guest_name=guest_name,
            room_number=room_number,
            nights=nights,
            email=email,
            phone=phone,
        )
        return {"success": success, "message": message, "booking": b}

    def checkout(self, target):
        success, message, b = checkout_booking(target)
        return {"success": success, "message": message, "booking": b}

    def reset_system(self):
        reset_system_to_beginning(persist=True)
        return {"success": True, "message": "System reset to Day 1: 0 guests, zero revenue, 9 suites available."}


# ---------------------------------------------------------
# Launchers
# ---------------------------------------------------------

def launch_webview(host="127.0.0.1", port=5000):
    """Starts the Flask server and opens inside a native pywebview desktop window."""
    try:
        import webview
    except ImportError:
        print("[!] pywebview is not installed. Launching in default browser...")
        launch_web(host=host, port=port, open_browser=True)
        return

    url = f"http://{host}:{port}"
    print(f"\n" + "=" * 68)
    print(f"  Sugo Grand Palace Hotel - PyWebView Desktop Window")
    print(f"  Structure: views/ (HTML/CSS/Assets) + backend.py")
    print(f"  URL: {url}")
    print("=" * 68 + "\n")

    api = HotelBackendAPI()

    server_thread = threading.Thread(
        target=lambda: app.run(host=host, port=port, debug=False, use_reloader=False),
        daemon=True,
    )
    server_thread.start()
    threading.Event().wait(0.6)

    window = webview.create_window(
        title="Sugo Grand Palace Hotel - Reservation System",
        url=url,
        js_api=api,
        width=1240,
        height=820,
        min_size=(1000, 680),
        confirm_close=True,
    )
    webview.start()


def launch_web(host="127.0.0.1", port=5000, open_browser=True):
    """Starts the Flask server and opens the browser."""
    url = f"http://{host}:{port}"
    print(f"\n" + "=" * 68)
    print(f"  Sugo Grand Palace Hotel - Web Application Started!")
    print(f"  Views Folder: {VIEWS_DIR}")
    print(f"  Access Portal: {url}")
    print("=" * 68 + "\n")

    if open_browser:
        def _open():
            webbrowser.open(url)
        threading.Timer(0.8, _open).start()

    app.run(host=host, port=port, debug=False)


def launch_cli():
    """Terminal CLI Menu."""
    while True:
        print("\n" + "=" * 72)
        print("          SUGO GRAND PALACE HOTEL - TERMINAL SYSTEM")
        print("=" * 72)
        print("  1. View Rooms")
        print("  2. Book a Room")
        print("  3. View Active Bookings")
        print("  4. View Customer Directory")
        print("  5. Checkout / Cancel Reservation")
        print("  6. Launch Desktop PyWebView Window")
        print("  7. Exit")
        print("=" * 72)
        c = input(" Enter choice (1-7): ").strip()
        if c == "1":
            print(f"\n {'Room No.':<10} | {'Type':<18} | {'Price':<14} | {'Status':<12}")
            print("-" * 60)
            for r in rooms:
                st = "Available" if r["is_available"] else "Occupied"
                print(f" {r['room_number']:<10} | {r['type']:<18} | PHP {r['price_per_night']:<10,.2f} | {st:<12}")
            input("\nPress Enter to continue...")
        elif c == "2":
            g_name = input(" Guest Name: ").strip()
            r_no = input(" Room Number: ").strip()
            n_val = input(" Nights: ").strip()
            try:
                n_int = int(n_val)
                ok, msg, nb = book_room(g_name, r_no, n_int)
                print(f" Result: {msg}")
            except Exception as e:
                print(f" Error: {e}")
            input("\nPress Enter to continue...")
        elif c == "3":
            print(f"\n {'Ref #':<10} | {'Guest Name':<18} | {'Room #':<8} | {'Total Cost':<15}")
            print("-" * 60)
            for b in bookings:
                print(f" {b.get('booking_id', 'N/A'):<10} | {b['guest_name']:<18} | {b['room_number']:<8} | PHP {b['total_cost']:<11,.2f}")
            input("\nPress Enter to continue...")
        elif c == "4":
            print(f"\n {'ID':<10} | {'Name':<18} | {'Tier':<14} | {'Spent':<14}")
            print("-" * 60)
            for cust in customers:
                print(f" {cust['customer_id']:<10} | {cust['name']:<18} | {cust['tier']:<14} | PHP {cust['total_spent']:<10,.2f}")
            input("\nPress Enter to continue...")
        elif c == "5":
            target = input(" Enter Booking Ref, Room Number, or Guest Name: ").strip()
            ok, msg, _ = checkout_booking(target)
            print(f" Result: {msg}")
            input("\nPress Enter to continue...")
        elif c == "6":
            launch_webview()
            break
        elif c == "7":
            print(" Goodbye!")
            break

