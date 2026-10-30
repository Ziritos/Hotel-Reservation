import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import sys

try:
    import main
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import main

THEME = {
    "sidebar_bg": "#0F172A",
    "sidebar_active": "#1E293B",
    "sidebar_hover": "#26354A",
    "sidebar_text": "#F8FAFC",
    "sidebar_subtext": "#94A3B8",
    "topbar_bg": "#FFFFFF",
    "content_bg": "#F1F5F9",
    "card_bg": "#FFFFFF",
    "card_border": "#E2E8F0",
    "primary": "#1E293B",
    "primary_hover": "#334155",
    "accent": "#D97706",
    "accent_hover": "#B45309",
    "accent_light": "#FEF3C7",
    "success": "#059669",
    "success_bg": "#DCFCE7",
    "success_text": "#166534",
    "danger": "#DC2626",
    "danger_bg": "#FEE2E2",
    "danger_text": "#991B1B",
    "info": "#2563EB",
    "info_bg": "#DBEAFE",
    "text_main": "#0F172A",
    "text_muted": "#64748B",
    "input_bg": "#F8FAFC",
    "input_border": "#CBD5E1",
}

FONT_FAMILY = "Segoe UI"


def format_php(amount: float) -> str:
    return f"{main.CURRENCY}{amount:,.2f}"


def get_room(room_number: str):
    for r in main.rooms:
        if str(r["room_number"]).strip().lower() == str(room_number).strip().lower():
            return r
    return None


def validate_guest_name(name: str):
    cleaned = name.strip()
    if not cleaned:
        return False, "Guest name cannot be empty. Please enter your name."
    if any(char.isdigit() for char in cleaned):
        return False, "Invalid Name! Guest name cannot contain numbers (letters only)."
    if not any(char.isalpha() for char in cleaned):
        return False, "Invalid Name! Please enter a valid name containing letters."
    return True, ""


def validate_nights(nights_val):
    try:
        n = int(nights_val)
        if n < 1:
            return False, "Number of nights must be at least 1.", 0
        return True, "", n
    except (ValueError, TypeError):
        return False, "Invalid nights input! Please enter a valid whole number (e.g. 1, 2, 3).", 0


class HotelReservationGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Grand Palace Hotel - Reservation Management System")
        self.geometry("1140x730")
        self.minsize(1000, 650)
        self.configure(bg=THEME["content_bg"])

        self.setup_styles()

        self.current_page = None
        self.nav_buttons = {}
        self.pages = {}

        self.create_layout()
        self.build_pages()
        self.navigate_to("dashboard")

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Custom.Treeview",
            background="#FFFFFF",
            foreground=THEME["text_main"],
            fieldbackground="#FFFFFF",
            rowheight=32,
            font=(FONT_FAMILY, 10),
            borderwidth=0,
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#F1F5F9",
            foreground=THEME["text_main"],
            font=(FONT_FAMILY, 10, "bold"),
            relief="flat",
            padding=(8, 8),
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", "#E2E8F0")],
            foreground=[("selected", THEME["text_main"])],
        )
        style.map(
            "Custom.Treeview.Heading",
            background=[("active", "#E2E8F0")],
        )

        style.configure(
            "Custom.TCombobox",
            fieldbackground=THEME["input_bg"],
            background="#FFFFFF",
            foreground=THEME["text_main"],
            padding=6,
            font=(FONT_FAMILY, 10),
        )

    def create_layout(self):
        self.sidebar = tk.Frame(self, bg=THEME["sidebar_bg"], width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand_frame = tk.Frame(self.sidebar, bg=THEME["sidebar_bg"], pady=24, padx=16)
        brand_frame.pack(fill="x")

        logo_icon = tk.Label(
            brand_frame,
            text="🏨",
            font=(FONT_FAMILY, 28),
            bg=THEME["sidebar_bg"],
            fg=THEME["accent"],
        )
        logo_icon.pack(anchor="w")

        title_lbl = tk.Label(
            brand_frame,
            text="SUGO HOTEL",
            font=(FONT_FAMILY, 14, "bold"),
            bg=THEME["sidebar_bg"],
            fg=THEME["sidebar_text"],
        )
        title_lbl.pack(anchor="w", pady=(4, 0))

        sub_lbl = tk.Label(
            brand_frame,
            text="Hotel Reservation System",
            font=(FONT_FAMILY, 9),
            bg=THEME["sidebar_bg"],
            fg=THEME["sidebar_subtext"],
        )
        sub_lbl.pack(anchor="w")

        div = tk.Frame(self.sidebar, bg=THEME["sidebar_active"], height=1)
        div.pack(fill="x", padx=16, pady=(0, 16))

        self.nav_container = tk.Frame(self.sidebar, bg=THEME["sidebar_bg"], padx=10)
        self.nav_container.pack(fill="x")

        nav_items = [
            ("dashboard", "📊  Dashboard"),
            ("rooms", "🛏️  Room Directory"),
            ("book", "📝  Book a Room"),
            ("bookings", "📋  Active Bookings"),
            ("checkout", "🚪  Checkout / Clear"),
        ]

        for key, text in nav_items:
            btn = tk.Button(
                self.nav_container,
                text=text,
                font=(FONT_FAMILY, 10, "bold"),
                bg=THEME["sidebar_bg"],
                fg=THEME["sidebar_text"],
                activebackground=THEME["sidebar_hover"],
                activeforeground="#FFFFFF",
                bd=0,
                padx=16,
                pady=11,
                anchor="w",
                cursor="hand2",
                command=lambda k=key: self.navigate_to(k),
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[key] = btn

        footer_frame = tk.Frame(self.sidebar, bg=THEME["sidebar_bg"], padx=16, pady=16)
        footer_frame.pack(side="bottom", fill="x")

        bsit_lbl = tk.Label(
            footer_frame,
            text="@Sugo Hotel 2026",
            font=(FONT_FAMILY, 8),
            bg=THEME["sidebar_bg"],
            fg=THEME["sidebar_subtext"],
            justify="left",
        )
        bsit_lbl.pack(anchor="w")

        self.main_area = tk.Frame(self, bg=THEME["content_bg"])
        self.main_area.pack(side="right", fill="both", expand=True)

        self.topbar = tk.Frame(self.main_area, bg=THEME["topbar_bg"], height=64, padx=28)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)

        self.page_title_lbl = tk.Label(
            self.topbar,
            text="Dashboard",
            font=(FONT_FAMILY, 15, "bold"),
            bg=THEME["topbar_bg"],
            fg=THEME["text_main"],
        )
        self.page_title_lbl.pack(side="left", pady=18)

        self.topbar_chips_frame = tk.Frame(self.topbar, bg=THEME["topbar_bg"])
        self.topbar_chips_frame.pack(side="right", pady=16)

        self.topbar_avail_chip = tk.Label(
            self.topbar_chips_frame,
            text="Available: 9",
            font=(FONT_FAMILY, 9, "bold"),
            bg=THEME["success_bg"],
            fg=THEME["success_text"],
            padx=10,
            pady=4,
        )
        self.topbar_avail_chip.pack(side="left", padx=4)

        self.topbar_occ_chip = tk.Label(
            self.topbar_chips_frame,
            text="Occupied: 0",
            font=(FONT_FAMILY, 9, "bold"),
            bg=THEME["danger_bg"],
            fg=THEME["danger_text"],
            padx=10,
            pady=4,
        )
        self.topbar_occ_chip.pack(side="left", padx=4)

        top_div = tk.Frame(self.main_area, bg=THEME["card_border"], height=1)
        top_div.pack(fill="x")

        self.content_container = tk.Frame(self.main_area, bg=THEME["content_bg"], padx=28, pady=20)
        self.content_container.pack(fill="both", expand=True)

    def build_pages(self):
        self.pages["dashboard"] = self.create_dashboard_page()
        self.pages["rooms"] = self.create_rooms_page()
        self.pages["book"] = self.create_book_page()
        self.pages["bookings"] = self.create_bookings_page()
        self.pages["checkout"] = self.create_checkout_page()

    def navigate_to(self, page_key: str):
        if self.current_page:
            self.pages[self.current_page].pack_forget()
            self.nav_buttons[self.current_page].configure(
                bg=THEME["sidebar_bg"],
                fg=THEME["sidebar_text"]
            )

        self.current_page = page_key
        page = self.pages[page_key]
        page.pack(fill="both", expand=True)

        self.nav_buttons[page_key].configure(
            bg=THEME["sidebar_active"],
            fg="#FFFFFF"
        )

        titles = {
            "dashboard": "System Overview & Dashboard",
            "rooms": "Hotel Room Directory & Inventory",
            "book": "New Room Reservation",
            "bookings": "Active Guest Reservations",
            "checkout": "Guest Checkout & Reservation Management",
        }
        self.page_title_lbl.config(text=titles.get(page_key, "Hotel System"))
        self.refresh_all_data()

    def refresh_all_data(self):
        total_rooms = len(main.rooms)
        occupied_count = sum(1 for r in main.rooms if not r["is_available"])
        available_count = total_rooms - occupied_count
        total_revenue = sum(b["total_cost"] for b in main.bookings)

        self.topbar_avail_chip.config(text=f"Available: {available_count}")
        self.topbar_occ_chip.config(text=f"Occupied: {occupied_count}")

        if hasattr(self, "dash_avail_lbl"):
            self.dash_total_lbl.config(text=str(total_rooms))
            self.dash_avail_lbl.config(text=str(available_count))
            self.dash_occ_lbl.config(text=str(occupied_count))
            self.dash_rev_lbl.config(text=format_php(total_revenue))
            self.refresh_dashboard_table()

        if hasattr(self, "refresh_rooms_table"):
            self.refresh_rooms_table()

        if hasattr(self, "refresh_booking_form_rooms"):
            self.refresh_booking_form_rooms()

        if hasattr(self, "refresh_bookings_table"):
            self.refresh_bookings_table()

        if hasattr(self, "refresh_checkout_table"):
            self.refresh_checkout_table()

    def create_dashboard_page(self):
        page = tk.Frame(self.content_container, bg=THEME["content_bg"])

        metrics_frame = tk.Frame(page, bg=THEME["content_bg"])
        metrics_frame.pack(fill="x", pady=(0, 16))

        for col in range(4):
            metrics_frame.columnconfigure(col, weight=1, uniform="metric_group")

        def make_stat_card(parent, col, icon, label_text, color_accent, bg_color):
            card = tk.Frame(parent, bg=THEME["card_bg"], bd=1, relief="solid")
            card.configure(highlightbackground=THEME["card_border"], highlightthickness=1)
            card.grid(row=0, column=col, padx=6, sticky="nsew")

            content = tk.Frame(card, bg=THEME["card_bg"], padx=16, pady=14)
            content.pack(fill="both", expand=True)

            top_row = tk.Frame(content, bg=THEME["card_bg"])
            top_row.pack(fill="x")

            lbl = tk.Label(top_row, text=label_text, font=(FONT_FAMILY, 9, "bold"), fg=THEME["text_muted"], bg=THEME["card_bg"])
            lbl.pack(side="left")

            badge = tk.Label(top_row, text=icon, font=(FONT_FAMILY, 14), fg=color_accent, bg=bg_color, padx=6, pady=2)
            badge.pack(side="right")

            val_lbl = tk.Label(content, text="0", font=(FONT_FAMILY, 18, "bold"), fg=THEME["text_main"], bg=THEME["card_bg"])
            val_lbl.pack(anchor="w", pady=(8, 0))
            return val_lbl

        self.dash_total_lbl = make_stat_card(metrics_frame, 0, "🏨", "TOTAL ROOMS", THEME["primary"], "#F1F5F9")
        self.dash_avail_lbl = make_stat_card(metrics_frame, 1, "🟢", "AVAILABLE", THEME["success"], THEME["success_bg"])
        self.dash_occ_lbl = make_stat_card(metrics_frame, 2, "🔴", "OCCUPIED", THEME["danger"], THEME["danger_bg"])
        self.dash_rev_lbl = make_stat_card(metrics_frame, 3, "💰", "TOTAL REVENUE", THEME["accent"], THEME["accent_light"])

        split_frame = tk.Frame(page, bg=THEME["content_bg"])
        split_frame.pack(fill="both", expand=True)
        split_frame.columnconfigure(0, weight=3)
        split_frame.columnconfigure(1, weight=1)
        split_frame.rowconfigure(0, weight=1)

        recent_card = tk.Frame(split_frame, bg=THEME["card_bg"], padx=16, pady=14, bd=1, relief="solid")
        recent_card.configure(highlightbackground=THEME["card_border"], highlightthickness=1)
        recent_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        rec_header = tk.Frame(recent_card, bg=THEME["card_bg"])
        rec_header.pack(fill="x", pady=(0, 10))

        tk.Label(rec_header, text="Active Reservations Overview", font=(FONT_FAMILY, 11, "bold"), bg=THEME["card_bg"], fg=THEME["text_main"]).pack(side="left")

        view_all_btn = tk.Button(
            rec_header,
            text="View All →",
            font=(FONT_FAMILY, 9, "bold"),
            bg=THEME["card_bg"],
            fg=THEME["accent"],
            bd=0,
            cursor="hand2",
            command=lambda: self.navigate_to("bookings")
        )
        view_all_btn.pack(side="right")

        dash_cols = ("guest", "room", "nights", "total")
        self.dash_tree = ttk.Treeview(recent_card, columns=dash_cols, show="headings", style="Custom.Treeview", height=7)
        self.dash_tree.heading("guest", text="Guest Name")
        self.dash_tree.heading("room", text="Room No.")
        self.dash_tree.heading("nights", text="Nights")
        self.dash_tree.heading("total", text="Total Paid")

        self.dash_tree.column("guest", width=180, anchor="w")
        self.dash_tree.column("room", width=90, anchor="center")
        self.dash_tree.column("nights", width=80, anchor="center")
        self.dash_tree.column("total", width=120, anchor="e")

        self.dash_tree.pack(fill="both", expand=True)

        actions_card = tk.Frame(split_frame, bg=THEME["card_bg"], padx=16, pady=14, bd=1, relief="solid")
        actions_card.configure(highlightbackground=THEME["card_border"], highlightthickness=1)
        actions_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(actions_card, text="Quick Shortcuts", font=(FONT_FAMILY, 11, "bold"), bg=THEME["card_bg"], fg=THEME["text_main"]).pack(anchor="w", pady=(0, 12))

        def make_action_btn(text, subtext, icon, bg_color, cmd):
            btn_frame = tk.Frame(actions_card, bg=bg_color, padx=12, pady=10, cursor="hand2")
            btn_frame.pack(fill="x", pady=6)
            
            icon_lbl = tk.Label(btn_frame, text=icon, font=(FONT_FAMILY, 14), bg=bg_color)
            icon_lbl.pack(side="left", padx=(0, 10))

            t_box = tk.Frame(btn_frame, bg=bg_color)
            t_box.pack(side="left", fill="both")
            tk.Label(t_box, text=text, font=(FONT_FAMILY, 10, "bold"), bg=bg_color, fg=THEME["text_main"]).pack(anchor="w")
            tk.Label(t_box, text=subtext, font=(FONT_FAMILY, 8), bg=bg_color, fg=THEME["text_muted"]).pack(anchor="w")

            for widget in (btn_frame, icon_lbl, t_box):
                widget.bind("<Button-1>", lambda e, c=cmd: c())
            for child in t_box.winfo_children():
                child.bind("<Button-1>", lambda e, c=cmd: c())

        make_action_btn("New Booking", "Reserve room for guest", "➕", THEME["accent_light"], lambda: self.navigate_to("book"))
        make_action_btn("Room Directory", "Check availability & rates", "🛏️", "#F1F5F9", lambda: self.navigate_to("rooms"))
        make_action_btn("Clear / Checkout", "Free up occupied room", "🚪", THEME["danger_bg"], lambda: self.navigate_to("checkout"))

        return page

    def refresh_dashboard_table(self):
        for item in self.dash_tree.get_children():
            self.dash_tree.delete(item)

        if not main.bookings:
            self.dash_tree.insert("", "end", values=("No active reservations found", "-", "-", "-"))
            return

        for b in main.bookings:
            room = get_room(b["room_number"])
            type_str = f" ({room['type']})" if room else ""
            self.dash_tree.insert(
                "",
                "end",
                values=(
                    b["guest_name"],
                    f"{b['room_number']}{type_str}",
                    b["nights"],
                    format_php(b["total_cost"]),
                ),
            )

    def create_rooms_page(self):
        page = tk.Frame(self.content_container, bg=THEME["content_bg"])

        control_card = tk.Frame(page, bg=THEME["card_bg"], padx=16, pady=12, bd=1, relief="solid")
        control_card.configure(highlightbackground=THEME["card_border"], highlightthickness=1)
        control_card.pack(fill="x", pady=(0, 14))

        tk.Label(control_card, text="Filter Rooms:", font=(FONT_FAMILY, 10, "bold"), bg=THEME["card_bg"], fg=THEME["text_main"]).pack(side="left", padx=(0, 8))

        self.room_status_filter_var = tk.StringVar(value="All Statuses")
        status_dropdown = ttk.Combobox(
            control_card,
            textvariable=self.room_status_filter_var,
            values=["All Statuses", "Available Only", "Occupied Only"],
            state="readonly",
            width=16,
            style="Custom.TCombobox",
        )
        status_dropdown.pack(side="left", padx=4)
        status_dropdown.bind("<<ComboboxSelected>>", lambda e: self.refresh_rooms_table())

        self.room_type_filter_var = tk.StringVar(value="All Room Types")
        type_dropdown = ttk.Combobox(
            control_card,
            textvariable=self.room_type_filter_var,
            values=["All Room Types", "Single", "Double", "Suite", "Presidential Suite"],
            state="readonly",
            width=18,
            style="Custom.TCombobox",
        )
        type_dropdown.pack(side="left", padx=6)
        type_dropdown.bind("<<ComboboxSelected>>", lambda e: self.refresh_rooms_table())

        reset_btn = tk.Button(
            control_card,
            text="Reset Filters",
            font=(FONT_FAMILY, 9),
            bg="#F1F5F9",
            fg=THEME["text_muted"],
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.reset_room_filters,
        )
        reset_btn.pack(side="left", padx=6)

        book_selected_btn = tk.Button(
            control_card,
            text="➕ Book Selected Room",
            font=(FONT_FAMILY, 9, "bold"),
            bg=THEME["accent"],
            fg="#FFFFFF",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.book_selected_from_directory,
        )
        book_selected_btn.pack(side="right")

        table_card = tk.Frame(page, bg=THEME["card_bg"], padx=16, pady=16, bd=1, relief="solid")
        table_card.configure(highlightbackground=THEME["card_border"], highlightthickness=1)
        table_card.pack(fill="both", expand=True)

        cols = ("room_no", "room_type", "price", "status", "guest")
        self.rooms_tree = ttk.Treeview(table_card, columns=cols, show="headings", style="Custom.Treeview")

        self.rooms_tree.heading("room_no", text="Room Number")
        self.rooms_tree.heading("room_type", text="Room Type & Tier")
        self.rooms_tree.heading("price", text="Rate per Night")
        self.rooms_tree.heading("status", text="Current Status")
        self.rooms_tree.heading("guest", text="Occupied By")

        self.rooms_tree.column("room_no", width=120, anchor="center")
        self.rooms_tree.column("room_type", width=220, anchor="w")
        self.rooms_tree.column("price", width=160, anchor="e")
        self.rooms_tree.column("status", width=140, anchor="center")
        self.rooms_tree.column("guest", width=220, anchor="w")

        scroll = ttk.Scrollbar(table_card, orient="vertical", command=self.rooms_tree.yview)
        self.rooms_tree.configure(yscrollcommand=scroll.set)

        self.rooms_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.rooms_tree.bind("<Double-1>", lambda e: self.book_selected_from_directory())

        return page

    def reset_room_filters(self):
        self.room_status_filter_var.set("All Statuses")
        self.room_type_filter_var.set("All Room Types")
        self.refresh_rooms_table()

    def refresh_rooms_table(self):
        for item in self.rooms_tree.get_children():
            self.rooms_tree.delete(item)

        status_filter = self.room_status_filter_var.get()
        type_filter = self.room_type_filter_var.get()

        occupied_guests = {b["room_number"]: b["guest_name"] for b in main.bookings}

        for r in main.rooms:
            if status_filter == "Available Only" and not r["is_available"]:
                continue
            if status_filter == "Occupied Only" and r["is_available"]:
                continue

            if type_filter != "All Room Types" and r["type"] != type_filter:
                continue

            status_text = "🟢 Available" if r["is_available"] else "🔴 Occupied"
            guest_text = occupied_guests.get(r["room_number"], "—")

            self.rooms_tree.insert(
                "",
                "end",
                values=(
                    r["room_number"],
                    r["type"],
                    format_php(r["price_per_night"]),
                    status_text,
                    guest_text,
                ),
            )

    def book_selected_from_directory(self):
        selected = self.rooms_tree.selection()
        if not selected:
            messagebox.showinfo("Select Room", "Please click on a room row to select it, or click 'Book a Room' from the sidebar.")
            return

        item = self.rooms_tree.item(selected[0])
        room_no = str(item["values"][0])
        room = get_room(room_no)

        if not room:
            return

        if not room["is_available"]:
            messagebox.showwarning(
                "Room Already Occupied",
                f"Room {room_no} ({room['type']}) is currently OCCUPIED!\nPlease select an available room."
            )
            return

        self.navigate_to("book")
        self.select_room_in_booking_form(room_no)

    def create_book_page(self):
        page = tk.Frame(self.content_container, bg=THEME["content_bg"])

        split = tk.Frame(page, bg=THEME["content_bg"])
        split.pack(fill="both", expand=True)
        split.columnconfigure(0, weight=3)
        split.columnconfigure(1, weight=2)
        split.rowconfigure(0, weight=1)

        form_card = tk.Frame(split, bg=THEME["card_bg"], padx=24, pady=20, bd=1, relief="solid")
        form_card.configure(highlightbackground=THEME["card_border"], highlightthickness=1)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(form_card, text="Guest & Room Details", font=(FONT_FAMILY, 13, "bold"), bg=THEME["card_bg"], fg=THEME["text_main"]).pack(anchor="w", pady=(0, 4))
        tk.Label(form_card, text="Fill out guest information and select preferred room tier.", font=(FONT_FAMILY, 9), bg=THEME["card_bg"], fg=THEME["text_muted"]).pack(anchor="w", pady=(0, 16))

        self.book_error_banner = tk.Label(
            form_card,
            text="",
            font=(FONT_FAMILY, 9, "bold"),
            bg=THEME["danger_bg"],
            fg=THEME["danger_text"],
            padx=12,
            pady=8,
            anchor="w",
            wraplength=400,
        )

        tk.Label(form_card, text="Guest Full Name *", font=(FONT_FAMILY, 10, "bold"), bg=THEME["card_bg"], fg=THEME["text_main"]).pack(anchor="w", pady=(8, 2))
        tk.Label(form_card, text="(Letters only, no numbers allowed - e.g., Juan Dela Cruz)", font=(FONT_FAMILY, 8), bg=THEME["card_bg"], fg=THEME["text_muted"]).pack(anchor="w", pady=(0, 4))

        self.guest_name_entry = tk.Entry(form_card, font=(FONT_FAMILY, 11), bg=THEME["input_bg"], relief="solid", bd=1)
        self.guest_name_entry.pack(fill="x", ipady=6, pady=(0, 12))
        self.guest_name_entry.bind("<KeyRelease>", lambda e: self.update_cost_preview())

        tk.Label(form_card, text="Select Preferred Room *", font=(FONT_FAMILY, 10, "bold"), bg=THEME["card_bg"], fg=THEME["text_main"]).pack(anchor="w", pady=(4, 2))
        
        self.book_room_var = tk.StringVar()
        self.book_room_dropdown = ttk.Combobox(
            form_card,
            textvariable=self.book_room_var,
            state="readonly",
            font=(FONT_FAMILY, 10),
            style="Custom.TCombobox",
        )
        self.book_room_dropdown.pack(fill="x", pady=(0, 12))
        self.book_room_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_cost_preview())

        tk.Label(form_card, text="Number of Nights *", font=(FONT_FAMILY, 10, "bold"), bg=THEME["card_bg"], fg=THEME["text_main"]).pack(anchor="w", pady=(4, 2))
        tk.Label(form_card, text="(Must be at least 1 whole night)", font=(FONT_FAMILY, 8), bg=THEME["card_bg"], fg=THEME["text_muted"]).pack(anchor="w", pady=(0, 4))

        nights_stepper_frame = tk.Frame(form_card, bg=THEME["card_bg"])
        nights_stepper_frame.pack(fill="x", pady=(0, 20))

        self.nights_var = tk.StringVar(value="1")
        self.nights_entry = tk.Entry(nights_stepper_frame, textvariable=self.nights_var, font=(FONT_FAMILY, 11, "bold"), justify="center", width=8, bg=THEME["input_bg"], relief="solid", bd=1)
        self.nights_entry.pack(side="left", ipady=6, padx=(0, 8))
        self.nights_entry.bind("<KeyRelease>", lambda e: self.update_cost_preview())

        minus_btn = tk.Button(nights_stepper_frame, text="−", font=(FONT_FAMILY, 11, "bold"), width=3, bg="#E2E8F0", fg=THEME["text_main"], bd=0, cursor="hand2", command=self.decrement_nights)
        minus_btn.pack(side="left", padx=2, ipady=3)

        plus_btn = tk.Button(nights_stepper_frame, text="+", font=(FONT_FAMILY, 11, "bold"), width=3, bg="#E2E8F0", fg=THEME["text_main"], bd=0, cursor="hand2", command=self.increment_nights)
        plus_btn.pack(side="left", padx=2, ipady=3)

        submit_btn = tk.Button(
            form_card,
            text="✔ Confirm & Complete Booking",
            font=(FONT_FAMILY, 11, "bold"),
            bg=THEME["accent"],
            fg="#FFFFFF",
            bd=0,
            pady=12,
            cursor="hand2",
            activebackground=THEME["accent_hover"],
            activeforeground="#FFFFFF",
            command=self.process_booking,
        )
        submit_btn.pack(fill="x", pady=(10, 0))

        clear_btn = tk.Button(
            form_card,
            text="Clear Form",
            font=(FONT_FAMILY, 9),
            bg=THEME["card_bg"],
            fg=THEME["text_muted"],
            bd=0,
            cursor="hand2",
            command=self.clear_booking_form,
        )
        clear_btn.pack(anchor="center", pady=(8, 0))

        summary_card = tk.Frame(split, bg=THEME["card_bg"], padx=24, pady=20, bd=1, relief="solid")
        summary_card.configure(highlightbackground=THEME["card_border"], highlightthickness=1)
        summary_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        tk.Label(summary_card, text="Reservation Preview", font=(FONT_FAMILY, 13, "bold"), bg=THEME["card_bg"], fg=THEME["text_main"]).pack(anchor="w", pady=(0, 4))
        tk.Label(summary_card, text="Real-time estimated pricing & details.", font=(FONT_FAMILY, 9), bg=THEME["card_bg"], fg=THEME["text_muted"]).pack(anchor="w", pady=(0, 16))

        preview_box = tk.Frame(summary_card, bg="#F8FAFC", padx=16, pady=16, bd=1, relief="solid")
        preview_box.configure(highlightbackground=THEME["card_border"], highlightthickness=1)
        preview_box.pack(fill="x", pady=(0, 16))

        def make_preview_row(parent, label_text):
            row = tk.Frame(parent, bg="#F8FAFC")
            row.pack(fill="x", pady=4)
            lbl = tk.Label(row, text=label_text, font=(FONT_FAMILY, 9), bg="#F8FAFC", fg=THEME["text_muted"])
            lbl.pack(side="left")
            val = tk.Label(row, text="—", font=(FONT_FAMILY, 9, "bold"), bg="#F8FAFC", fg=THEME["text_main"])
            val.pack(side="right")
            return val

        self.prev_guest_lbl = make_preview_row(preview_box, "Guest Name:")
        self.prev_room_lbl = make_preview_row(preview_box, "Room Selected:")
        self.prev_tier_lbl = make_preview_row(preview_box, "Room Tier:")
        self.prev_rate_lbl = make_preview_row(preview_box, "Rate / Night:")
        self.prev_nights_lbl = make_preview_row(preview_box, "Nights:")

        tk.Frame(preview_box, bg=THEME["card_border"], height=1).pack(fill="x", pady=8)

        total_row = tk.Frame(preview_box, bg="#F8FAFC")
        total_row.pack(fill="x", pady=2)
        tk.Label(total_row, text="Total Amount:", font=(FONT_FAMILY, 11, "bold"), bg="#F8FAFC", fg=THEME["text_main"]).pack(side="left")
        self.prev_total_lbl = tk.Label(total_row, text="PHP 0.00", font=(FONT_FAMILY, 14, "bold"), bg="#F8FAFC", fg=THEME["accent"])
        self.prev_total_lbl.pack(side="right")

        info_frame = tk.Frame(summary_card, bg=THEME["info_bg"], padx=14, pady=12)
        info_frame.pack(fill="x", pady=(10, 0))

        tk.Label(
            info_frame,
            text="ℹ️ Rate Information (PHP):\n"
                 "• Single Rooms: PHP 1,200.00 / night\n"
                 "• Double Rooms: PHP 1,800.00 / night\n"
                 "• Suites: PHP 3,500.00 / night\n"
                 "• Presidential Suite: PHP 7,500.00 / night",
            font=(FONT_FAMILY, 8),
            bg=THEME["info_bg"],
            fg="#1E3A8A",
            justify="left",
        ).pack(anchor="w")

        return page

    def increment_nights(self):
        try:
            val = int(self.nights_var.get())
            self.nights_var.set(str(val + 1))
        except ValueError:
            self.nights_var.set("1")
        self.update_cost_preview()

    def decrement_nights(self):
        try:
            val = int(self.nights_var.get())
            if val > 1:
                self.nights_var.set(str(val - 1))
        except ValueError:
            self.nights_var.set("1")
        self.update_cost_preview()

    def refresh_booking_form_rooms(self):
        available_rooms = [r for r in main.rooms if r["is_available"]]
        options = [f"Room {r['room_number']} — {r['type']} ({format_php(r['price_per_night'])}/night)" for r in available_rooms]

        self.book_room_dropdown["values"] = options

        current = self.book_room_var.get()
        if options:
            if not current or not any(current.startswith(f"Room {r['room_number']} ") for r in available_rooms):
                self.book_room_dropdown.current(0)
        else:
            self.book_room_var.set("No Rooms Available (Full)")

        self.update_cost_preview()

    def select_room_in_booking_form(self, room_number: str):
        options = list(self.book_room_dropdown["values"])
        for idx, opt in enumerate(options):
            if opt.startswith(f"Room {room_number} "):
                self.book_room_dropdown.current(idx)
                break
        self.update_cost_preview()

    def get_selected_room_from_form(self):
        val = self.book_room_var.get()
        if not val or "Room " not in val:
            return None
        try:
            room_no = val.split("—")[0].replace("Room", "").strip()
            return get_room(room_no)
        except Exception:
            return None

    def update_cost_preview(self):
        guest_name = self.guest_name_entry.get().strip()
        self.prev_guest_lbl.config(text=guest_name if guest_name else "—")

        room = self.get_selected_room_from_form()
        if room:
            self.prev_room_lbl.config(text=f"Room {room['room_number']}")
            self.prev_tier_lbl.config(text=room["type"])
            self.prev_rate_lbl.config(text=format_php(room["price_per_night"]))
            rate = room["price_per_night"]
        else:
            self.prev_room_lbl.config(text="—")
            self.prev_tier_lbl.config(text="—")
            self.prev_rate_lbl.config(text="—")
            rate = 0.0

        is_valid_nights, _, nights = validate_nights(self.nights_var.get())
        if is_valid_nights and room:
            self.prev_nights_lbl.config(text=f"{nights} night(s)")
            total = rate * nights
            self.prev_total_lbl.config(text=format_php(total))
        else:
            self.prev_nights_lbl.config(text=f"{self.nights_var.get()} (Invalid)" if not is_valid_nights else "—")
            self.prev_total_lbl.config(text="PHP 0.00")

    def show_booking_error(self, message: str):
        self.book_error_banner.config(text=f"⚠ {message}")
        self.book_error_banner.pack(fill="x", pady=(0, 12), before=self.guest_name_entry.master.winfo_children()[2])

    def hide_booking_error(self):
        self.book_error_banner.pack_forget()

    def clear_booking_form(self):
        self.guest_name_entry.delete(0, tk.END)
        self.nights_var.set("1")
        self.hide_booking_error()
        self.refresh_booking_form_rooms()

    def process_booking(self):
        self.hide_booking_error()

        if not any(r["is_available"] for r in main.rooms):
            self.show_booking_error("Sorry, all rooms are currently occupied! No rooms available.")
            return

        guest_name = self.guest_name_entry.get().strip()
        name_valid, name_err = validate_guest_name(guest_name)
        if not name_valid:
            self.show_booking_error(name_err)
            self.guest_name_entry.focus_set()
            return

        room = self.get_selected_room_from_form()
        if not room:
            self.show_booking_error("Please choose a valid available room from the list.")
            return

        if not room["is_available"]:
            self.show_booking_error(f"Error: Room {room['room_number']} is ALREADY OCCUPIED! Please choose another room.")
            return

        nights_valid, nights_err, nights = validate_nights(self.nights_var.get())
        if not nights_valid:
            self.show_booking_error(nights_err)
            self.nights_entry.focus_set()
            return

        price_per_night = room["price_per_night"]
        total_cost = price_per_night * nights

        room["is_available"] = False
        new_booking = {
            "guest_name": guest_name,
            "room_number": room["room_number"],
            "nights": nights,
            "total_cost": total_cost,
        }
        main.bookings.append(new_booking)

        self.show_booking_receipt(new_booking, room)
        self.clear_booking_form()
        self.refresh_all_data()

    def show_booking_receipt(self, booking: dict, room: dict):
        receipt = tk.Toplevel(self)
        receipt.title("Booking Confirmation & Receipt")
        receipt.geometry("460x520")
        receipt.minsize(420, 480)
        receipt.configure(bg="#FFFFFF")
        receipt.transient(self)
        receipt.grab_set()

        header = tk.Frame(receipt, bg="#0F172A", padx=20, pady=20)
        header.pack(fill="x")

        tk.Label(header, text="🏨 GRAND PALACE HOTEL", font=(FONT_FAMILY, 14, "bold"), fg="#D97706", bg="#0F172A").pack(anchor="w")
        tk.Label(header, text="Official Reservation Confirmation", font=(FONT_FAMILY, 9), fg="#94A3B8", bg="#0F172A").pack(anchor="w")

        body = tk.Frame(receipt, bg="#FFFFFF", padx=24, pady=20)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="BOOKING SUCCESSFUL!", font=(FONT_FAMILY, 12, "bold"), fg=THEME["success"], bg="#FFFFFF").pack(anchor="w", pady=(0, 14))

        details = [
            ("Date & Time", datetime.now().strftime("%B %d, %Y  %I:%M %p")),
            ("Guest Name", booking["guest_name"]),
            ("Room Number", f"{booking['room_number']} ({room['type']})"),
            ("Rate per Night", format_php(room["price_per_night"])),
            ("Nights Booked", f"{booking['nights']} night(s)"),
            ("Status", "CONFIRMED / OCCUPIED"),
        ]

        for lbl, val in details:
            row = tk.Frame(body, bg="#FFFFFF")
            row.pack(fill="x", pady=4)
            tk.Label(row, text=lbl, font=(FONT_FAMILY, 9), fg=THEME["text_muted"], bg="#FFFFFF").pack(side="left")
            tk.Label(row, text=val, font=(FONT_FAMILY, 9, "bold"), fg=THEME["text_main"], bg="#FFFFFF").pack(side="right")

        tk.Frame(body, bg=THEME["card_border"], height=1).pack(fill="x", pady=14)

        tot_row = tk.Frame(body, bg="#FFFFFF")
        tot_row.pack(fill="x", pady=2)
        tk.Label(tot_row, text="Total Amount Paid:", font=(FONT_FAMILY, 11, "bold"), fg=THEME["text_main"], bg="#FFFFFF").pack(side="left")
        tk.Label(tot_row, text=format_php(booking["total_cost"]), font=(FONT_FAMILY, 14, "bold"), fg=THEME["accent"], bg="#FFFFFF").pack(side="right")

        btn_frame = tk.Frame(receipt, bg="#FFFFFF", padx=24, pady=16)
        btn_frame.pack(fill="x", side="bottom")

        close_btn = tk.Button(
            btn_frame,
            text="Close & Return to System",
            font=(FONT_FAMILY, 10, "bold"),
            bg=THEME["primary"],
            fg="#FFFFFF",
            bd=0,
            pady=10,
            cursor="hand2",
            command=receipt.destroy,
        )
        close_btn.pack(fill="x")

    def create_bookings_page(self):
        page = tk.Frame(self.content_container, bg=THEME["content_bg"])

        toolbar = tk.Frame(page, bg=THEME["card_bg"], padx=16, pady=12, bd=1, relief="solid")
        toolbar.configure(highlightbackground=THEME["card_border"], highlightthickness=1)
        toolbar.pack(fill="x", pady=(0, 14))

        tk.Label(toolbar, text="🔍 Search Bookings:", font=(FONT_FAMILY, 10, "bold"), bg=THEME["card_bg"], fg=THEME["text_main"]).pack(side="left", padx=(0, 8))

        self.booking_search_var = tk.StringVar()
        search_entry = tk.Entry(toolbar, textvariable=self.booking_search_var, font=(FONT_FAMILY, 10), bg=THEME["input_bg"], relief="solid", bd=1, width=28)
        search_entry.pack(side="left", ipady=4, padx=(0, 8))
        self.booking_search_var.trace_add("write", lambda *args: self.refresh_bookings_table())

        clear_search_btn = tk.Button(
            toolbar,
            text="Clear",
            font=(FONT_FAMILY, 9),
            bg="#F1F5F9",
            fg=THEME["text_muted"],
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=lambda: self.booking_search_var.set(""),
        )
        clear_search_btn.pack(side="left")

        checkout_btn = tk.Button(
            toolbar,
            text="🚪 Checkout Selected",
            font=(FONT_FAMILY, 9, "bold"),
            bg=THEME["danger"],
            fg="#FFFFFF",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.checkout_selected_from_bookings,
        )
        checkout_btn.pack(side="right", padx=(8, 0))

        view_rcpt_btn = tk.Button(
            toolbar,
            text="🧾 View Receipt",
            font=(FONT_FAMILY, 9, "bold"),
            bg=THEME["card_bg"],
            fg=THEME["primary"],
            bd=1,
            relief="solid",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self.view_selected_receipt,
        )
        view_rcpt_btn.pack(side="right")

        table_card = tk.Frame(page, bg=THEME["card_bg"], padx=16, pady=16, bd=1, relief="solid")
        table_card.configure(highlightbackground=THEME["card_border"], highlightthickness=1)
        table_card.pack(fill="both", expand=True)

        cols = ("num", "guest", "room", "type", "nights", "rate", "total")
        self.bookings_tree = ttk.Treeview(table_card, columns=cols, show="headings", style="Custom.Treeview")

        self.bookings_tree.heading("num", text="#")
        self.bookings_tree.heading("guest", text="Guest Name")
        self.bookings_tree.heading("room", text="Room No.")
        self.bookings_tree.heading("type", text="Room Type")
        self.bookings_tree.heading("nights", text="Nights")
        self.bookings_tree.heading("rate", text="Rate / Night")
        self.bookings_tree.heading("total", text="Total Paid")

        self.bookings_tree.column("num", width=50, anchor="center")
        self.bookings_tree.column("guest", width=180, anchor="w")
        self.bookings_tree.column("room", width=90, anchor="center")
        self.bookings_tree.column("type", width=150, anchor="w")
        self.bookings_tree.column("nights", width=80, anchor="center")
        self.bookings_tree.column("rate", width=130, anchor="e")
        self.bookings_tree.column("total", width=140, anchor="e")

        scroll = ttk.Scrollbar(table_card, orient="vertical", command=self.bookings_tree.yview)
        self.bookings_tree.configure(yscrollcommand=scroll.set)

        self.bookings_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        return page

    def refresh_bookings_table(self):
        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)

        query = self.booking_search_var.get().strip().lower()

        if not main.bookings:
            return

        for idx, b in enumerate(main.bookings, start=1):
            guest = b["guest_name"]
            room_no = b["room_number"]
            room = get_room(room_no)
            room_type = room["type"] if room else "Unknown"
            rate = room["price_per_night"] if room else 0.0

            if query and (query not in guest.lower() and query not in room_no.lower()):
                continue

            self.bookings_tree.insert(
                "",
                "end",
                values=(
                    idx,
                    guest,
                    room_no,
                    room_type,
                    b["nights"],
                    format_php(rate),
                    format_php(b["total_cost"]),
                ),
            )

    def get_selected_booking(self):
        selected = self.bookings_tree.selection()
        if not selected:
            return None
        item = self.bookings_tree.item(selected[0])
        room_no = str(item["values"][2])
        for b in main.bookings:
            if str(b["room_number"]) == room_no:
                return b
        return None

    def view_selected_receipt(self):
        booking = self.get_selected_booking()
        if not booking:
            messagebox.showinfo("Select Booking", "Please select a booking from the table to view its receipt.")
            return
        room = get_room(booking["room_number"])
        self.show_booking_receipt(booking, room)

    def checkout_selected_from_bookings(self):
        booking = self.get_selected_booking()
        if not booking:
            messagebox.showinfo("Select Booking", "Please select a booking from the table to checkout.")
            return

        self.navigate_to("checkout")
        self.preselect_checkout_room(booking["room_number"])

    def create_checkout_page(self):
        page = tk.Frame(self.content_container, bg=THEME["content_bg"])

        split = tk.Frame(page, bg=THEME["content_bg"])
        split.pack(fill="both", expand=True)
        split.columnconfigure(0, weight=3)
        split.columnconfigure(1, weight=2)
        split.rowconfigure(0, weight=1)

        left_card = tk.Frame(split, bg=THEME["card_bg"], padx=18, pady=16, bd=1, relief="solid")
        left_card.configure(highlightbackground=THEME["card_border"], highlightthickness=1)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(left_card, text="Select Room or Guest to Checkout", font=(FONT_FAMILY, 12, "bold"), bg=THEME["card_bg"], fg=THEME["text_main"]).pack(anchor="w", pady=(0, 4))
        tk.Label(left_card, text="Click on any reservation below to load breakdown.", font=(FONT_FAMILY, 9), bg=THEME["card_bg"], fg=THEME["text_muted"]).pack(anchor="w", pady=(0, 12))

        cols = ("room", "guest", "type", "total")
        self.checkout_tree = ttk.Treeview(left_card, columns=cols, show="headings", style="Custom.Treeview")
        self.checkout_tree.heading("room", text="Room No.")
        self.checkout_tree.heading("guest", text="Guest Name")
        self.checkout_tree.heading("type", text="Room Tier")
        self.checkout_tree.heading("total", text="Total Cost")

        self.checkout_tree.column("room", width=90, anchor="center")
        self.checkout_tree.column("guest", width=160, anchor="w")
        self.checkout_tree.column("type", width=140, anchor="w")
        self.checkout_tree.column("total", width=120, anchor="e")

        self.checkout_tree.pack(fill="both", expand=True)
        self.checkout_tree.bind("<<TreeviewSelect>>", lambda e: self.on_checkout_table_select())

        right_card = tk.Frame(split, bg=THEME["card_bg"], padx=20, pady=20, bd=1, relief="solid")
        right_card.configure(highlightbackground=THEME["card_border"], highlightthickness=1)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        tk.Label(right_card, text="Checkout Confirmation", font=(FONT_FAMILY, 13, "bold"), bg=THEME["card_bg"], fg=THEME["text_main"]).pack(anchor="w", pady=(0, 4))
        tk.Label(right_card, text="Review details before clearing room status.", font=(FONT_FAMILY, 9), bg=THEME["card_bg"], fg=THEME["text_muted"]).pack(anchor="w", pady=(0, 16))

        box = tk.Frame(right_card, bg="#F8FAFC", padx=16, pady=16, bd=1, relief="solid")
        box.configure(highlightbackground=THEME["card_border"], highlightthickness=1)
        box.pack(fill="x", pady=(0, 16))

        def make_co_row(parent, label_text):
            row = tk.Frame(parent, bg="#F8FAFC")
            row.pack(fill="x", pady=4)
            lbl = tk.Label(row, text=label_text, font=(FONT_FAMILY, 9), bg="#F8FAFC", fg=THEME["text_muted"])
            lbl.pack(side="left")
            val = tk.Label(row, text="—", font=(FONT_FAMILY, 9, "bold"), bg="#F8FAFC", fg=THEME["text_main"])
            val.pack(side="right")
            return val

        self.co_guest_lbl = make_co_row(box, "Guest Name:")
        self.co_room_lbl = make_co_row(box, "Room Number:")
        self.co_type_lbl = make_co_row(box, "Room Type:")
        self.co_nights_lbl = make_co_row(box, "Nights Stayed:")
        self.co_rate_lbl = make_co_row(box, "Rate / Night:")

        tk.Frame(box, bg=THEME["card_border"], height=1).pack(fill="x", pady=8)

        tot_row = tk.Frame(box, bg="#F8FAFC")
        tot_row.pack(fill="x", pady=2)
        tk.Label(tot_row, text="Total Bill Cleared:", font=(FONT_FAMILY, 10, "bold"), bg="#F8FAFC", fg=THEME["text_main"]).pack(side="left")
        self.co_total_lbl = tk.Label(tot_row, text="PHP 0.00", font=(FONT_FAMILY, 13, "bold"), bg="#F8FAFC", fg=THEME["accent"])
        self.co_total_lbl.pack(side="right")

        self.process_checkout_btn = tk.Button(
            right_card,
            text="🚪 Confirm Checkout & Free Room",
            font=(FONT_FAMILY, 11, "bold"),
            bg=THEME["danger"],
            fg="#FFFFFF",
            bd=0,
            pady=12,
            cursor="hand2",
            state="disabled",
            command=self.process_checkout,
        )
        self.process_checkout_btn.pack(fill="x", pady=(10, 0))

        tk.Label(
            right_card,
            text="💡 Checking out will remove this guest reservation\n"
                 "and immediately restore room status to AVAILABLE.",
            font=(FONT_FAMILY, 8),
            fg=THEME["text_muted"],
            bg=THEME["card_bg"],
            justify="center",
        ).pack(anchor="center", pady=(12, 0))

        return page

    def refresh_checkout_table(self):
        for item in self.checkout_tree.get_children():
            self.checkout_tree.delete(item)

        if not main.bookings:
            self.reset_checkout_details()
            return

        for b in main.bookings:
            room = get_room(b["room_number"])
            room_type = room["type"] if room else "Standard"
            self.checkout_tree.insert(
                "",
                "end",
                values=(
                    b["room_number"],
                    b["guest_name"],
                    room_type,
                    format_php(b["total_cost"]),
                ),
            )

    def preselect_checkout_room(self, room_number: str):
        for item in self.checkout_tree.get_children():
            vals = self.checkout_tree.item(item)["values"]
            if str(vals[0]) == str(room_number):
                self.checkout_tree.selection_set(item)
                self.checkout_tree.focus(item)
                self.on_checkout_table_select()
                break

    def on_checkout_table_select(self):
        selected = self.checkout_tree.selection()
        if not selected:
            self.reset_checkout_details()
            return

        vals = self.checkout_tree.item(selected[0])["values"]
        room_no = str(vals[0])
        
        target = None
        for b in main.bookings:
            if str(b["room_number"]) == room_no:
                target = b
                break

        if not target:
            self.reset_checkout_details()
            return

        room = get_room(target["room_number"])
        self.selected_checkout_booking = target
        self.selected_checkout_room = room

        self.co_guest_lbl.config(text=target["guest_name"])
        self.co_room_lbl.config(text=f"Room {target['room_number']}")
        self.co_type_lbl.config(text=room["type"] if room else "—")
        self.co_nights_lbl.config(text=f"{target['nights']} night(s)")
        self.co_rate_lbl.config(text=format_php(room["price_per_night"]) if room else "—")
        self.co_total_lbl.config(text=format_php(target["total_cost"]))

        self.process_checkout_btn.config(state="normal", bg=THEME["danger"])

    def reset_checkout_details(self):
        self.selected_checkout_booking = None
        self.selected_checkout_room = None
        self.co_guest_lbl.config(text="—")
        self.co_room_lbl.config(text="—")
        self.co_type_lbl.config(text="—")
        self.co_nights_lbl.config(text="—")
        self.co_rate_lbl.config(text="—")
        self.co_total_lbl.config(text="PHP 0.00")
        self.process_checkout_btn.config(state="disabled", bg="#CBD5E1")

    def process_checkout(self):
        if not hasattr(self, "selected_checkout_booking") or not self.selected_checkout_booking:
            messagebox.showinfo("No Selection", "Please select an active reservation to checkout.")
            return

        b = self.selected_checkout_booking
        guest = b["guest_name"]
        room_no = b["room_number"]

        confirm = messagebox.askyesno(
            "Confirm Checkout / Cancellation",
            f"Are you sure you want to checkout guest '{guest}' from Room {room_no}?\n\n"
            f"This will mark Room {room_no} as AVAILABLE and clear the reservation.",
            parent=self,
        )

        if not confirm:
            return

        for r in main.rooms:
            if str(r["room_number"]) == str(room_no):
                r["is_available"] = True
                break

        if b in main.bookings:
            main.bookings.remove(b)

        messagebox.showinfo(
            "Checkout Successful",
            f"✔ Room {room_no} is now AVAILABLE!\n"
            f"Reservation for '{guest}' has been successfully cleared.",
            parent=self,
        )

        self.reset_checkout_details()
        self.refresh_all_data()


def launch_gui():
    app = HotelReservationGUI()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
