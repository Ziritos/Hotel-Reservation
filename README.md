# Sugo Grand Palace Hotel - Reservation & Front Desk System

A full-stack **Hotel Reservation and Front Desk Hospitality System** built with **Python** as the core backend engine, **HTML5/CSS3** for luxury styling, and **PyWebView** for a native desktop application experience.

Designed specifically around the two authentic hotel roles: **Guest** and **Receptionist**.

---

## 🗂️ Project File Structure

Arranged cleanly to match the requested modular layout:

```
Hotel-Reservation/
├── views/
│   ├── assets/
│   │   ├── login-bg.jpg            # Luxury hotel background image
│   │   ├── logo_transparent.png    # Transparent PNG hotel crest
│   │   ├── logo.jpg                # Hotel crest (JPG)
│   │   ├── logo.png                # Hotel crest (PNG)
│   │   ├── logo.svg                # Vector logo crest
│   │   ├── room_single.svg         # Single Suite illustration
│   │   ├── room_double.svg         # Double Suite illustration
│   │   ├── room_suite.svg          # Executive Suite illustration
│   │   └── room_presidential.svg   # Presidential Penthouse illustration
│   ├── guest.html                  # Guest Accommodations & Self-Service Portal
│   ├── receptionist.html           # Front Desk Operations & Room Rack Console
│   ├── login.html                  # Hospitality Portal Sign-In (Guest & Receptionist)
│   └── styles.css                  # Unified Modern Stylesheet
├── data/
│   └── hotel_data.json             # Persistent JSON Database
├── .gitignore                      # Git ignored files
├── backend.py                      # Core Python backend, data models, & Flask API
├── main.py                         # Application entrypoint (launches PyWebView desktop window)
└── run.bat                         # Windows 1-click batch launcher
```

---

## 🌟 Key Features

1. 🪟 **PyWebView Desktop Window**:
   - Double-clicking [`run.bat`](file:///c:/Users/Gabriel/OneDrive/Documents/Hotel-Reservation/run.bat) or running `python main.py` opens a standalone desktop application window rendering HTML5 and CSS3 directly.

2. 🏨 **Guest Portal ([`views/guest.html`](file:///c:/Users/Gabriel/OneDrive/Documents/Hotel-Reservation/views/guest.html))**:
   - **Browse & Filter Suites**: Categorize by *Single*, *Double*, *Executive Suite*, or *Presidential Penthouse*, with "Available Only" filter and real-time text search.
   - **Live Suite Reservation**: Interactive modal with dynamic stay pricing in Philippine Peso (`₱`), auto check-out calculation, and strict **letters-only guest name validation** (rejects numbers and digits).
   - **Retrieve Guest Folio**: Search reservations instantly by Confirmation Code (e.g. `SH-1024`) or registered guest name.
   - **Official Confirmation Voucher**: View and print official hotel booking vouchers with 1-click.
   - **Self-Service Cancellation**: Release reservations back to inventory.

3. 🛎️ **Front Desk Console ([`views/receptionist.html`](file:///c:/Users/Gabriel/OneDrive/Documents/Hotel-Reservation/views/receptionist.html))**:
   - **Property KPIs**: Live metrics for Total Rooms, Available Clean, Occupied, Current Occupancy %, Gross Revenue, and Registered Guests.
   - **Room Rack & Housekeeping**: Real-time room cards showing occupant details, walk-in quick check-in, 1-click check-out, and a **"Change Photo"** tool to upload custom room photos directly into `views/assets/`.
   - **Master Reservations Ledger**: Searchable reservation log with folio receipts and check-out capabilities.
   - **Guest CRM & Loyalty Directory**: Guest profiles categorized into loyalty tiers (*VIP Platinum*, *Gold*, *Silver*, *Standard*).
   - **Property Branding**: Upload custom hotel emblems or specify web image URLs.

4. 📊 **In-Memory Transaction Data Structure (`TransactionLedger`)**:
   - High-performance in-memory datastore maintaining an immutable audit log of all financial and operational hotel events (`BOOKING_RESERVATION`, `CHECKOUT_SETTLED`, `CANCELLATION_REFUND`).
   - Uses multi-hash indexing for $O(1)$ search complexity:
     - Hash Map by **Transaction ID** (`TXN-XXXXXX`)
     - Multi-index Hash Map by **Booking Folio** (`SH-XXXX`)
     - Multi-index Hash Map by **Guest Name**
     - Multi-index Hash Map by **Suite Number**
   - Live audit ledger tab with real-time text filtering and financial summary chips (Gross Invoiced, Refunds, Net Revenue).
   - Dedicated REST APIs: `/api/transactions` and `/api/transactions/<txn_id>`.

5. 🔑 **Unified Sign-In ([`views/login.html`](file:///c:/Users/Gabriel/OneDrive/Documents/Hotel-Reservation/views/login.html))**:
   - Clean tabs for Guest Services and Reception Desk (`receptionist` / `frontdesk2026`).

---

## 🚀 How to Run

### Option 1: Double-Click Launcher
Double-click [`run.bat`](file:///c:/Users/Gabriel/OneDrive/Documents/Hotel-Reservation/run.bat) in the project folder.

### Option 2: Python Command Line
```powershell
# Native PyWebView Desktop Window (Default)
python main.py

# Or launch in your default web browser:
python main.py --browser

# Or launch Terminal / CLI mode:
python main.py --cli
```
