
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


class Transaction:
    """Represents an atomic hotel financial and operational transaction record."""

    def __init__(
        self,
        transaction_id: str,
        transaction_type: str,
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

        self._transactions.append(txn)

        self._by_id[txn.transaction_id] = txn

        b_key = txn.booking_id.strip().upper()
        self._by_booking.setdefault(b_key, []).append(txn)

        g_key = txn.guest_name.strip().lower()
        self._by_guest.setdefault(g_key, []).append(txn)
       
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


DEFAULT_STAFF_ACCOUNTS = [
    {
        "id": "STF-101",
        "staff_id": "STF-101",
        "username": "receptionist",
        "password": "frontdesk2026",
        "role": "receptionist",
        "name": "Front Desk Receptionist",
        "created_at": "2026-11-01 08:00:00"
    },
    {
        "id": "STF-102",
        "staff_id": "STF-102",
        "username": "admin",
        "password": "admin2026",
        "role": "admin",
        "name": "System Administrator",
        "created_at": "2026-11-01 08:00:00"
    },
    {
        "id": "STF-103",
        "staff_id": "STF-103",
        "username": "maintenance",
        "password": "clean2026",
        "role": "maintenance",
        "name": "Facilities & Maintenance Lead",
        "created_at": "2026-11-01 08:00:00"
    },
]

rooms = []
bookings = []
customers = []
staff_accounts = [dict(s) for s in DEFAULT_STAFF_ACCOUNTS]
customer_accounts = []
maintenance_tickets = []
notifications = []
payments = []
transaction_ledger = TransactionLedger()
hotel_settings = {
    "hotel_name": "Sugo Grand Palace Hotel",
    "logo_url": "/assets/logo.svg",
    "phone": "+63 (088) 888-7846",
    "email": "frontdesk@sugograndpalace.ph",
    "address": "Cagayan De Oro City, Philippines",
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
    room = get_room(r_target)
    if room and room.get("maintenance_status") in ("Under Maintenance", "Damaged", "Out of Order"):
        return False, f"Suite {room_number} is currently under maintenance and unavailable for booking.", None

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
    if room.get("maintenance_status") in ("Under Maintenance", "Damaged", "Out of Order"):
        return False, f"Suite {room_number} is currently under maintenance and cannot be reserved.", {}

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

    if check_in:
        parsed_in = parse_date_str(check_in)
        if not parsed_in:
            return False, f"Invalid check-in date '{check_in}'. Please use YYYY-MM-DD format.", {}
        new_in_date = parsed_in
    else:
        new_in_date = parse_date_str(booking.get("check_in")) or date.today()

    new_out_date = new_in_date + timedelta(days=parsed_nights)

    is_avail, clash_msg, _ = check_room_availability_for_dates(
        room_number=target_room_number,
        check_in_date=new_in_date,
        check_out_date=new_out_date,
        exclude_booking_id=booking_id,
    )
    if not is_avail:
        return False, clash_msg, {}

    booking["room_number"] = str(target_room["room_number"])
    booking["room_type"] = target_room.get("type", "Standard")
    booking["price_per_night"] = float(target_room["price_per_night"])
    booking["nights"] = parsed_nights
    booking["check_in"] = new_in_date.strftime("%Y-%m-%d")
    booking["check_out"] = new_out_date.strftime("%Y-%m-%d")

    rate = float(booking.get("price_per_night", 1200.0))
    booking["total_cost"] = round(rate * parsed_nights, 2)

    booking["guest_name"] = guest_name.strip()
    if phone is not None:
        booking["phone"] = phone.strip()
    if email is not None:
        booking["email"] = email.strip()
    if special_requests is not None:
        booking["special_requests"] = special_requests.strip()

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


def get_staff_account(username: str):
    u = (username or "").strip().lower()
    for s in staff_accounts:
        if s.get("username", "").strip().lower() == u:
            return s
    return None


def authenticate_staff_user(username: str, password: str, expected_role: str = None) -> tuple[bool, str, dict]:
    u = (username or "").strip().lower()
    p = (password or "").strip()
    staff = get_staff_account(u)
    if not staff:
        return False, "Access Denied: Invalid username or password.", {}
    if staff.get("password") != p:
        return False, "Access Denied: Invalid username or password.", {}
    if expected_role and staff.get("role") != expected_role:
        return False, f"Unauthorized: Account does not have '{expected_role}' privileges.", {}
    return True, f"Welcome, {staff.get('name')}!", staff


def add_or_update_staff_account(username: str, password: str, role: str, name: str, staff_id: str = "") -> tuple[bool, str, dict]:
    u = username.strip().lower()
    if not u or not password.strip():
        return False, "Username and password cannot be empty.", {}
    existing = get_staff_account(u)
    if existing:
        existing["password"] = password.strip()
        existing["role"] = role.strip()
        existing["name"] = name.strip() or existing.get("name", u)
        if "staff_id" not in existing:
            existing["staff_id"] = existing.get("id", f"STF-{random.randint(100, 999)}")
        save_data()
        return True, f"Staff account '{u}' updated.", existing
    sid = staff_id or f"STF-{random.randint(100, 999)}"
    new_staff = {
        "id": sid,
        "staff_id": sid,
        "username": u,
        "password": password.strip(),
        "role": role.strip(),
        "name": name.strip() or u.capitalize(),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    staff_accounts.append(new_staff)
    save_data()
    return True, f"Staff account '{u}' created.", new_staff


def delete_staff_account(staff_id: str) -> tuple[bool, str]:
    for i, s in enumerate(list(staff_accounts)):
        if s.get("id") == staff_id or s.get("staff_id") == staff_id:
            if s.get("username") in ("admin", "receptionist", "maintenance"):
                return False, f"Cannot delete default core account '{s.get('username')}'."
            uname = s.get("username")
            staff_accounts.pop(i)
            save_data()
            return True, f"Staff account '{uname}' deleted."
    return False, "Staff account not found."


def get_customer_account_by_identifier(identifier: str):
    target = (identifier or "").strip().lower()
    for c in customer_accounts:
        if c.get("username", "").strip().lower() == target or c.get("email", "").strip().lower() == target:
            return c
    return None


def register_customer_account(name: str, email: str, phone: str, password: str, username: str = "") -> tuple[bool, str, dict]:
    name_clean = name.strip()
    email_clean = email.strip().lower()
    phone_clean = phone.strip()
    user_clean = (username or email_clean.split("@")[0]).strip().lower()
    
    valid_name, err = validate_guest_name(name_clean)
    if not valid_name:
        return False, err, {}
    if not email_clean or "@" not in email_clean:
        return False, "Please enter a valid email address.", {}
    if not password or len(password) < 4:
        return False, "Password must be at least 4 characters long.", {}
    
    if get_customer_account_by_identifier(email_clean):
        return False, "An account with this email address already exists. Please log in.", {}
    if get_customer_account_by_identifier(user_clean):
        user_clean = f"{user_clean}{random.randint(10, 99)}"
        
    cust_id = f"CUST-{random.randint(1000, 9999)}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_acc = {
        "customer_id": cust_id,
        "username": user_clean,
        "name": name_clean,
        "email": email_clean,
        "phone": phone_clean,
        "password": password.strip(),
        "created_at": now_str,
        "bookings": [],
        "total_stays": 0,
        "total_spent": 0.0
    }
    customer_accounts.append(new_acc)
    update_or_create_customer(name=name_clean, email=email_clean, phone=phone_clean)
    save_data()
    return True, "Account registered successfully!", new_acc


def authenticate_customer_account(identifier: str, password: str) -> tuple[bool, str, dict]:
    acc = get_customer_account_by_identifier(identifier)
    if not acc:
        return False, "Invalid email/username or password.", {}
    if acc.get("password") != password.strip():
        return False, "Invalid email/username or password.", {}
    return True, f"Welcome back, {acc.get('name')}!", acc


def add_notification(target_role: str, title: str, message: str, room_number: str = ""):
    notif = {
        "id": f"NOTIF-{random.randint(1000, 9999)}",
        "target_role": target_role,
        "title": title,
        "message": message,
        "room_number": str(room_number),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "read": False
    }
    notifications.append(notif)
    save_data()
    return notif


def get_notifications_for_role(role: str, unread_only: bool = False):
    res = [n for n in notifications if n.get("target_role") in (role, "all")]
    if unread_only:
        res = [n for n in res if not n.get("read")]
    return list(reversed(res))


def dismiss_notification(notif_id: str):
    for n in notifications:
        if n.get("id") == notif_id:
            n["read"] = True
            save_data()
            return True
    return False


def create_maintenance_ticket(room_number: str, issue: str, priority: str = "Medium", reported_by: str = "Staff", technician: str = "", cost: float = 0.0, notes: str = "") -> tuple[bool, str, dict]:
    room = get_room(room_number)
    if not room:
        return False, f"Room '{room_number}' does not exist.", {}
    
    tkt_id = f"TKT-{random.randint(100, 999)}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ticket = {
        "ticket_id": tkt_id,
        "room_number": str(room_number),
        "issue": issue.strip(),
        "priority": priority.strip() or "Medium",
        "status": "In Progress",
        "reported_by": reported_by.strip() or "Staff",
        "reported_at": now_str,
        "created_at": now_str,
        "technician": technician.strip() or "Facilities Team",
        "cost": float(cost or 0.0),
        "notes": notes.strip(),
        "completed_at": None
    }
    maintenance_tickets.append(ticket)
    room["maintenance_status"] = "Under Maintenance"
    room["is_available"] = False
    
    add_notification(
        target_role="receptionist",
        title="Room Under Maintenance",
        message=f"Suite {room_number} flagged for maintenance: {issue} (Priority: {priority}).",
        room_number=str(room_number)
    )
    save_data()
    return True, f"Maintenance ticket {tkt_id} created for Suite {room_number}.", ticket


def update_maintenance_ticket(ticket_id: str, status: str = "", notes: str = "", cost: float = None, technician: str = "", mark_ready: bool = False) -> tuple[bool, str, dict]:
    target = None
    for t in maintenance_tickets:
        if t.get("ticket_id") == ticket_id:
            target = t
            break
    if not target:
        return False, f"Ticket '{ticket_id}' not found.", {}
    
    if status:
        target["status"] = status
    if notes:
        target["notes"] = notes
    if cost is not None:
        target["cost"] = float(cost)
    if technician:
        target["technician"] = technician
        
    if mark_ready or status == "Completed":
        target["status"] = "Completed"
        target["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        r = get_room(target.get("room_number"))
        if r:
            r["maintenance_status"] = "Clean & Ready"
            get_metrics()
            
        add_notification(
            target_role="receptionist",
            title="Room Repaired & Ready",
            message=f"Suite {target.get('room_number')} repairs completed! Room is clean and ready for check-in.",
            room_number=str(target.get("room_number"))
        )
    save_data()
    return True, f"Ticket {ticket_id} updated.", target


def set_room_repaired_and_ready(room_number: str) -> tuple[bool, str]:
    r = get_room(room_number)
    if not r:
        return False, f"Room '{room_number}' not found."
    r["maintenance_status"] = "Clean & Ready"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for t in maintenance_tickets:
        if str(t.get("room_number")) == str(room_number) and t.get("status") != "Completed":
            t["status"] = "Completed"
            t["completed_at"] = now_str
            t["notes"] = (t.get("notes", "") + " | Marked ready by Maintenance.").strip(" | ")
            
    add_notification(
        target_role="receptionist",
        title="Room Repaired & Ready",
        message=f"Suite {room_number} repairs completed! Room is clean and ready for guests.",
        room_number=str(room_number)
    )
    get_metrics()
    save_data()
    return True, f"Suite {room_number} is now marked Clean & Ready!"


def record_payment_entry(booking_id: str, amount: float, method: str = "Cash", status: str = "Paid", recorded_by: str = "Front Desk", notes: str = "") -> dict:
    b = get_booking_by_id(booking_id)
    guest_name = b.get("guest_name", "Walk-In Guest") if b else "Guest"
    room_number = b.get("room_number", "") if b else ""
    
    pay_id = f"PAY-{random.randint(1000, 9999)}"
    entry = {
        "payment_id": pay_id,
        "booking_id": booking_id,
        "guest_name": guest_name,
        "room_number": room_number,
        "amount": float(amount),
        "method": method,
        "status": status,
        "recorded_by": recorded_by,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "notes": notes
    }
    payments.append(entry)
    
    transaction_ledger.record(
        txn_type=f"PAYMENT_{method.upper().replace(' ', '_')}",
        booking_id=booking_id,
        guest_name=guest_name,
        room_number=room_number,
        amount=float(amount),
        status="Settled" if status == "Paid" else status,
        payment_method=method,
        notes=f"Payment recorded: {notes}" if notes else f"Payment recorded via {method}"
    )
    if b:
        b["payment_status"] = status
        b["payment_method"] = method
    save_data()
    return entry


def add_new_room(room_number: str, room_type: str, price: float, capacity: int, bed_type: str, size: str, description: str = "", amenities_str: str = "") -> tuple[bool, str, dict]:
    r_num = str(room_number).strip()
    if not r_num:
        return False, "Room number cannot be empty.", {}
    if get_room(r_num):
        return False, f"Room '{r_num}' already exists.", {}
    amenities = [a.strip() for a in amenities_str.split(",") if a.strip()] if amenities_str else ["High-speed Wi-Fi", "Air Conditioning", "Hot & Cold Shower", "Smart TV"]
    new_r = {
        "room_number": r_num,
        "type": room_type.strip(),
        "price_per_night": float(price),
        "capacity": int(capacity),
        "bed_type": bed_type.strip(),
        "size": size.strip(),
        "image_url": get_default_room_image(room_type),
        "amenities": amenities,
        "description": description.strip() or f"Well-appointed {room_type} room.",
        "is_available": True,
        "maintenance_status": "Clean & Ready"
    }
    rooms.append(new_r)
    save_data()
    return True, f"Suite {r_num} added to inventory.", new_r


def update_room_details(room_number: str, room_type: str, price: float, capacity: int, bed_type: str, size: str, description: str = "", amenities_str: str = "") -> tuple[bool, str, dict]:
    r = get_room(room_number)
    if not r:
        return False, f"Room '{room_number}' not found.", {}
    r["type"] = room_type.strip()
    r["price_per_night"] = float(price)
    r["capacity"] = int(capacity)
    r["bed_type"] = bed_type.strip()
    r["size"] = size.strip()
    if description.strip():
        r["description"] = description.strip()
    if amenities_str.strip():
        r["amenities"] = [a.strip() for a in amenities_str.split(",") if a.strip()]
    save_data()
    return True, f"Suite {room_number} details updated successfully.", r


def delete_room_from_inventory(room_number: str) -> tuple[bool, str]:
    global rooms
    r = get_room(room_number)
    if not r:
        return False, f"Room '{room_number}' not found."
    for b in bookings:
        if str(b.get("room_number")) == str(room_number) and b.get("status") in ("Confirmed", "Checked In"):
            return False, f"Cannot delete Room {room_number} because it has active reservations."
    rooms = [rm for rm in rooms if str(rm.get("room_number")) != str(room_number)]
    save_data()
    return True, f"Suite {room_number} removed from inventory."


def get_metrics() -> dict:
    total_rooms = len(rooms)
    today_dt = date.today()

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

        if b_in <= today_dt <= b_out:
            occupied_today_room_nos.add(str(b.get("room_number", "")).strip())
        elif b_in <= today_dt and b.get("status") in ("Confirmed", "Checked In"):
            occupied_today_room_nos.add(str(b.get("room_number", "")).strip())

    for r in rooms:
        r_num = str(r.get("room_number", "")).strip()
        is_maint = (r.get("maintenance_status") in ("Under Maintenance", "Damaged", "Out of Order"))
        r["is_available"] = (r_num not in occupied_today_room_nos and not is_maint)

    maintenance_count = sum(1 for r in rooms if r.get("maintenance_status") in ("Under Maintenance", "Damaged", "Out of Order"))
    occupied_count = len(occupied_today_room_nos)
    available_count = sum(1 for r in rooms if r.get("is_available"))
    total_revenue = sum(
        float(b.get("total_cost", 0.0))
        for b in bookings
        if b.get("status") not in ("Cancelled",)
    )
    occupancy_rate = (occupied_count / total_rooms * 100) if total_rooms > 0 else 0.0

    active_bookings_count = sum(
        1 for b in bookings if b.get("status") not in ("Checked Out", "Cancelled")
    )

    open_tickets = sum(1 for t in maintenance_tickets if t.get("status") != "Completed")

    return {
        "total_rooms": total_rooms,
        "available_rooms": available_count,
        "occupied_rooms": occupied_count,
        "maintenance_rooms": maintenance_count,
        "occupancy_rate": round(occupancy_rate, 1),
        "total_revenue": total_revenue,
        "active_bookings_count": active_bookings_count,
        "total_customers": len(customers),
        "total_staff": len(staff_accounts),
        "total_customer_accounts": len(customer_accounts),
        "open_tickets": open_tickets,
        "total_tickets": len(maintenance_tickets),
    }


def save_data():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        payload = {
            "rooms": rooms,
            "bookings": bookings,
            "customers": customers,
            "hotel_settings": hotel_settings,
            "staff_accounts": staff_accounts,
            "customer_accounts": customer_accounts,
            "maintenance_tickets": maintenance_tickets,
            "notifications": notifications,
            "payments": payments,
            "transactions": transaction_ledger.get_all(reverse=False),
            "last_updated": datetime.now().isoformat(),
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except Exception:
        pass


def reset_system_to_beginning(persist: bool = True):
    global rooms, bookings, customers, transaction_ledger, maintenance_tickets, notifications, payments, staff_accounts, customer_accounts
    rooms.clear()
    for r in DEFAULT_ROOMS:
        room_dict = dict(r)
        room_dict["is_available"] = True
        room_dict["maintenance_status"] = "Clean & Ready"
        rooms.append(room_dict)

    bookings.clear()
    customers.clear()
    transaction_ledger.clear()
    maintenance_tickets.clear()
    notifications.clear()
    payments.clear()
    customer_accounts.clear()
    staff_accounts.clear()
    staff_accounts.extend([dict(s) for s in DEFAULT_STAFF_ACCOUNTS])

    if persist:
        save_data()


def load_data():
    global hotel_settings, staff_accounts, customer_accounts, maintenance_tickets, notifications, payments

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("hotel_settings"):
                    hotel_settings.update(data["hotel_settings"])
                if data.get("staff_accounts"):
                    staff_accounts.clear()
                    staff_accounts.extend(data["staff_accounts"])
                if data.get("customer_accounts"):
                    customer_accounts.clear()
                    customer_accounts.extend(data["customer_accounts"])
                if data.get("maintenance_tickets"):
                    maintenance_tickets.clear()
                    maintenance_tickets.extend(data["maintenance_tickets"])
                if data.get("notifications"):
                    notifications.clear()
                    notifications.extend(data["notifications"])
                if data.get("payments"):
                    payments.clear()
                    payments.extend(data["payments"])
        except Exception:
            pass

    if not staff_accounts:
        staff_accounts.extend([dict(s) for s in DEFAULT_STAFF_ACCOUNTS])

    reset_system_to_beginning(persist=True)

load_data()


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
    
    customer_user = None
    customer_bookings = []
    if session.get("customer_logged_in"):
        c_id = session.get("customer_id")
        for c in customer_accounts:
            if c.get("customer_id") == c_id:
                customer_user = c
                break
        if customer_user:
            c_name = customer_user.get("name", "").lower()
            c_email = customer_user.get("email", "").lower()
            customer_bookings = [
                b for b in bookings
                if b.get("guest_name", "").lower() == c_name or (b.get("email") and b.get("email").lower() == c_email)
            ]

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
        customer_user=customer_user,
        customer_bookings=customer_bookings,
    )


@app.route("/customer/login", methods=["GET", "POST"])
@app.route("/login/customer", methods=["GET", "POST"])
def customer_login_page():
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "").strip()
        if not identifier or not password:
            flash("Please enter your email/username and password.", "danger")
            return redirect(url_for("customer_login_page"))
        ok, msg, acc = authenticate_customer_account(identifier, password)
        if ok:
            session["customer_logged_in"] = True
            session["customer_id"] = acc.get("customer_id")
            session["customer_name"] = acc.get("name")
            session["customer_email"] = acc.get("email")
            flash(f"Welcome back, {acc.get('name')}!", "success")
            return redirect(url_for("guest_page"))
        else:
            flash(msg, "danger")
            return redirect(url_for("customer_login_page"))
    return render_template("login_customer.html", mode="login")


@app.route("/customer/register", methods=["GET", "POST"])
@app.route("/register", methods=["GET", "POST"])
def customer_register_page():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "").strip()
        
        ok, msg, acc = register_customer_account(name=name, email=email, phone=phone, password=password)
        if ok:
            session["customer_logged_in"] = True
            session["customer_id"] = acc.get("customer_id")
            session["customer_name"] = acc.get("name")
            session["customer_email"] = acc.get("email")
            flash("Registration successful! Welcome to Sugo Grand Palace Hotel.", "success")
            return redirect(url_for("guest_page"))
        else:
            flash(msg, "danger")
            return redirect(url_for("customer_register_page"))
    return render_template("login_customer.html", mode="register")


@app.route("/customer/logout")
@app.route("/logout/customer")
def customer_logout():
    session.pop("customer_logged_in", None)
    session.pop("customer_id", None)
    session.pop("customer_name", None)
    session.pop("customer_email", None)
    flash("You have safely signed out of your customer account.", "info")
    return redirect(url_for("guest_page"))


@app.route("/login")
def login_page():
    if request.args.get("role") == "receptionist":
        return redirect(url_for("receptionist_login_page"))
    if request.args.get("role") == "admin":
        return redirect(url_for("admin_login_page"))
    if request.args.get("role") == "maintenance":
        return redirect(url_for("maintenance_login_page"))
    if request.args.get("role") == "customer":
        return redirect(url_for("customer_login_page"))
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

        AUTHORIZED_STAFF = {
            "receptionist": "frontdesk2026",
            "frontdesk": "frontdesk2026",
        }

        staff = get_staff_account(username)
        if staff and staff.get("password") == password and staff.get("role") in ("receptionist", "admin"):
            session["receptionist_logged_in"] = True
            session["receptionist_user"] = staff.get("username")
            flash(f"Welcome, {staff.get('name', username)}! Front Desk Console ready.", "success")
            return redirect(url_for("receptionist_dashboard"))
        elif username.lower() in AUTHORIZED_STAFF and AUTHORIZED_STAFF[username.lower()] == password:
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
    flash("You have signed out of the Front Desk Console.", "info")
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


@app.route("/cancel", methods=["POST"])
@app.route("/my-booking/cancel", methods=["POST"])
def cancel_my_booking_route():
    booking_id = request.form.get("booking_id", "").strip()
    guest_name = request.form.get("guest_name", "").strip()
    if not booking_id or not guest_name:
        flash("Missing cancellation details.", "danger")
        return redirect(url_for("guest_page", tab="lookup"))

    success, msg = cancel_booking_by_customer(booking_id, guest_name)
    flash(msg, "success" if success else "danger")
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
    unread_notifs = get_notifications_for_role("receptionist", unread_only=True)
    return render_template(
        "receptionist.html",
        metrics=metrics,
        rooms=rooms,
        bookings=bookings,
        customers=customers,
        transactions=all_transactions,
        txn_metrics=txn_metrics,
        today_str=today_str,
        notifications=unread_notifs,
        payments=payments,
    )


@app.route("/receptionist/payment/record", methods=["POST"])
def receptionist_record_payment_route():
    if not session.get("receptionist_logged_in") and not session.get("admin_logged_in"):
        flash("Please sign in as authorized staff to record payments.", "danger")
        return redirect(url_for("receptionist_login_page"))
    booking_id = request.form.get("booking_id", "").strip()
    amount = request.form.get("amount", 0.0)
    method = request.form.get("method", "Cash").strip()
    status = request.form.get("status", "Paid").strip()
    notes = request.form.get("notes", "").strip()
    
    rec = record_payment_entry(
        booking_id=booking_id,
        amount=float(amount or 0.0),
        method=method,
        status=status,
        recorded_by=session.get("receptionist_user", "Receptionist"),
        notes=notes
    )
    flash(f"Payment of ₱{rec['amount']:,.2f} recorded via {method}.", "success")
    return redirect(request.referrer or url_for("receptionist_dashboard"))


@app.route("/receptionist/notification/<notif_id>/dismiss", methods=["POST"])
def receptionist_dismiss_notification_route(notif_id):
    dismiss_notification(notif_id)
    return redirect(request.referrer or url_for("receptionist_dashboard"))


@app.route("/admin/login", methods=["GET", "POST"])
@app.route("/login/admin", methods=["GET", "POST"])
def admin_login_page():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return redirect(url_for("admin_login_page"))
        
        if username.lower() == "admin" and password == "admin2026":
            session["admin_logged_in"] = True
            session["admin_user"] = "admin"
            flash("Welcome, Administrator! Management Console ready.", "success")
            return redirect(url_for("admin_dashboard"))
        
        ok, msg, staff = authenticate_staff_user(username, password, expected_role="admin")
        if ok:
            session["admin_logged_in"] = True
            session["admin_user"] = staff.get("username")
            flash(f"Welcome, {staff.get('name')}! Management Console ready.", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Access Denied: Invalid administrator credentials.", "danger")
            return redirect(url_for("admin_login_page"))
    return render_template("login_admin.html")


@app.route("/admin/logout")
@app.route("/logout/admin")
def admin_logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_user", None)
    flash("You have signed out of the Administrator Console.", "info")
    return redirect(url_for("admin_login_page"))


@app.route("/admin")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        flash("Please sign in as Administrator to access the Management Console.", "danger")
        return redirect(url_for("admin_login_page"))
    
    metrics = get_metrics()
    today_str = date.today().strftime("%Y-%m-%d")
    
    revenue_by_type = {}
    for b in bookings:
        if b.get("status") != "Cancelled":
            rtype = b.get("room_type", "Standard")
            revenue_by_type[rtype] = revenue_by_type.get(rtype, 0.0) + float(b.get("total_cost", 0.0))
            
    return render_template(
        "admin.html",
        metrics=metrics,
        rooms=rooms,
        bookings=bookings,
        customers=customers,
        customer_accounts=customer_accounts,
        staff_accounts=staff_accounts,
        maintenance_tickets=maintenance_tickets,
        payments=payments,
        transactions=transaction_ledger.get_all(reverse=True),
        hotel_settings=hotel_settings,
        revenue_by_type=revenue_by_type,
        today_str=today_str,
    )


@app.route("/admin/staff/add", methods=["POST"])
def admin_add_staff_route():
    if not session.get("admin_logged_in"):
        flash("Unauthorized access.", "danger")
        return redirect(url_for("admin_login_page"))
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    role = request.form.get("role", "receptionist").strip()
    name = request.form.get("name", "").strip()
    ok, msg, _ = add_or_update_staff_account(username, password, role, name)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/staff/delete/<staff_id>", methods=["POST"])
def admin_delete_staff_route(staff_id):
    if not session.get("admin_logged_in"):
        flash("Unauthorized access.", "danger")
        return redirect(url_for("admin_login_page"))
    ok, msg = delete_staff_account(staff_id)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/room/update", methods=["POST"])
def admin_update_room_route():
    if not session.get("admin_logged_in"):
        flash("Unauthorized access.", "danger")
        return redirect(url_for("admin_login_page"))
    room_number = request.form.get("room_number", "").strip()
    room_type = (request.form.get("room_type") or request.form.get("type", "")).strip()
    price = request.form.get("price") or request.form.get("price_per_night", 0)
    capacity = request.form.get("capacity", 2)
    bed_type = request.form.get("bed_type", "").strip()
    size = request.form.get("size", "").strip()
    description = request.form.get("description", "").strip()
    amenities = request.form.get("amenities", "").strip()
    
    ok, msg, _ = update_room_details(room_number, room_type, price, capacity, bed_type, size, description, amenities)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/room/add", methods=["POST"])
def admin_add_room_route():
    if not session.get("admin_logged_in"):
        flash("Unauthorized access.", "danger")
        return redirect(url_for("admin_login_page"))
    room_number = request.form.get("room_number", "").strip()
    room_type = (request.form.get("room_type") or request.form.get("type", "")).strip()
    price = request.form.get("price") or request.form.get("price_per_night", 0)
    capacity = request.form.get("capacity", 2)
    bed_type = request.form.get("bed_type", "").strip()
    size = request.form.get("size", "").strip()
    description = request.form.get("description", "").strip()
    amenities = request.form.get("amenities", "").strip()
    
    ok, msg, _ = add_new_room(room_number, room_type, price, capacity, bed_type, size, description, amenities)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/settings/update", methods=["POST"])
def admin_update_settings_route():
    if not session.get("admin_logged_in"):
        flash("Unauthorized access.", "danger")
        return redirect(url_for("admin_login_page"))
    hotel_name = request.form.get("hotel_name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    address = request.form.get("address", "").strip()
    if hotel_name:
        hotel_settings["hotel_name"] = hotel_name
    if phone:
        hotel_settings["phone"] = phone
    if email:
        hotel_settings["email"] = email
    if address:
        hotel_settings["address"] = address
    save_data()
    flash("Hotel settings updated successfully.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/reset-system", methods=["POST"])
def admin_reset_system_route():
    if not session.get("admin_logged_in"):
        flash("Unauthorized access.", "danger")
        return redirect(url_for("admin_login_page"))
    admin_pass = request.form.get("admin_password", "").strip()
    if admin_pass not in ("admin2026", "frontdesk2026"):
        flash("Invalid administrator confirmation password.", "danger")
        return redirect(url_for("admin_dashboard"))
    reset_system_to_beginning(persist=True)
    flash("System refreshed to Day 1: 0 guests, ₱0.00 revenue, all suites available clean.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/maintenance/login", methods=["GET", "POST"])
@app.route("/login/maintenance", methods=["GET", "POST"])
def maintenance_login_page():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return redirect(url_for("maintenance_login_page"))
            
        if username.lower() == "maintenance" and password == "clean2026":
            session["maintenance_logged_in"] = True
            session["maintenance_user"] = "maintenance"
            flash("Welcome! Facilities & Maintenance Console ready.", "success")
            return redirect(url_for("maintenance_dashboard"))
            
        ok, msg, staff = authenticate_staff_user(username, password, expected_role="maintenance")
        if ok:
            session["maintenance_logged_in"] = True
            session["maintenance_user"] = staff.get("username")
            flash(f"Welcome, {staff.get('name')}! Facilities & Maintenance Console ready.", "success")
            return redirect(url_for("maintenance_dashboard"))
        else:
            flash("Access Denied: Invalid maintenance credentials.", "danger")
            return redirect(url_for("maintenance_login_page"))
    return render_template("login_maintenance.html")


@app.route("/maintenance/logout")
@app.route("/logout/maintenance")
def maintenance_logout():
    session.pop("maintenance_logged_in", None)
    session.pop("maintenance_user", None)
    flash("You have signed out of the Facilities & Maintenance Console.", "info")
    return redirect(url_for("maintenance_login_page"))


@app.route("/maintenance")
def maintenance_dashboard():
    if not session.get("maintenance_logged_in"):
        flash("Please sign in to access the Facilities & Maintenance Console.", "danger")
        return redirect(url_for("maintenance_login_page"))
    metrics = get_metrics()
    today_str = date.today().strftime("%Y-%m-%d")
    return render_template(
        "maintenance.html",
        rooms=rooms,
        metrics=metrics,
        maintenance_tickets=maintenance_tickets,
        today_str=today_str,
    )


@app.route("/maintenance/ticket/create", methods=["POST"])
def maintenance_create_ticket_route():
    if not session.get("maintenance_logged_in") and not session.get("receptionist_logged_in") and not session.get("admin_logged_in"):
        flash("Please sign in to report maintenance requests.", "danger")
        return redirect(url_for("maintenance_login_page"))
    room_number = request.form.get("room_number", "").strip()
    issue = request.form.get("issue", "").strip()
    priority = request.form.get("priority", "Medium").strip()
    technician = request.form.get("technician", "").strip()
    cost = request.form.get("cost", 0.0)
    notes = request.form.get("notes", "").strip()
    
    ok, msg, _ = create_maintenance_ticket(
        room_number=room_number,
        issue=issue,
        priority=priority,
        reported_by=session.get("maintenance_user") or session.get("receptionist_user") or "Staff",
        technician=technician,
        cost=float(cost or 0.0),
        notes=notes
    )
    flash(msg, "success" if ok else "danger")
    return redirect(request.referrer or url_for("maintenance_dashboard"))


@app.route("/maintenance/ticket/update", methods=["POST"])
def maintenance_update_ticket_route():
    if not session.get("maintenance_logged_in") and not session.get("admin_logged_in"):
        flash("Unauthorized.", "danger")
        return redirect(url_for("maintenance_login_page"))
    ticket_id = request.form.get("ticket_id", "").strip()
    status = request.form.get("status", "").strip()
    notes = request.form.get("notes", "").strip()
    cost = request.form.get("cost")
    technician = request.form.get("technician", "").strip()
    mark_ready = str(request.form.get("mark_ready", "")).strip().lower() in ("1", "yes", "on", "true")
    
    cost_val = float(cost) if cost else None
    ok, msg, _ = update_maintenance_ticket(ticket_id, status=status, notes=notes, cost=cost_val, technician=technician, mark_ready=mark_ready)
    flash(msg, "success" if ok else "danger")
    return redirect(request.referrer or url_for("maintenance_dashboard"))


@app.route("/maintenance/room/mark-ready", methods=["POST"])
def maintenance_mark_ready_route():
    if not session.get("maintenance_logged_in") and not session.get("admin_logged_in"):
        flash("Unauthorized.", "danger")
        return redirect(url_for("maintenance_login_page"))
    room_number = request.form.get("room_number", "").strip()
    ok, msg = set_room_repaired_and_ready(room_number)
    flash(msg, "success" if ok else "danger")
    return redirect(request.referrer or url_for("maintenance_dashboard"))


@app.route("/receptionist/reset-system", methods=["POST"])
def receptionist_reset_system_route():
    if not session.get("receptionist_logged_in"):
        flash("Please sign in as authorized staff to reset the system.", "danger")
        return redirect(url_for("receptionist_login_page"))

    reset_system_to_beginning(persist=True)
    flash("System refreshed to Day 1: All 9 suites are available clean, zero in-house guests, and ₱0.00 revenue.", "success")
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
    flash(msg, "success" if success else "danger")
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
        flash(f"New Reservation confirmed: Booking {new_b.get('booking_id')} for {new_b.get('guest_name')} in Suite {new_b.get('room_number')}.", "success")
    else:
        flash(f"Booking Failed: {msg}", "danger")

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

    flash(msg, "success" if success else "danger")
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
    flash(msg, "success" if success else "danger")
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
        flash(f"Suite {room_number} photo updated successfully!", "success")
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
        flash("Property logo updated successfully!", "success")
    else:
        flash("Please select a logo file or enter a valid logo URL.", "warning")

    return redirect(request.referrer or url_for("receptionist_dashboard"))


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

