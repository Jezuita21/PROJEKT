import datetime
import math
import tkinter as tk
from tkinter import messagebox, ttk

class Vehicle:
    def __init__(self, registration: str, vehicle_type: str, rate_multiplier: float):
        self.registration = registration.upper()
        self.vehicle_type = vehicle_type
        self.rate_multiplier = rate_multiplier
        self.entry_time = datetime.datetime.now()

class Car(Vehicle):
    def __init__(self, registration: str):
        super().__init__(registration, "Osobowy", 1.0)

class Motorcycle(Vehicle):
    def __init__(self, registration: str):
        super().__init__(registration, "Motocykl", 0.7)

class Truck(Vehicle):
    def __init__(self, registration: str):
        super().__init__(registration, "Ciężarowy", 1.5)


class ParkingSpot:
    def __init__(self, spot_id: int, spot_type: str, base_rate: float):
        self.spot_id = spot_id
        self.spot_type = spot_type  # Standard, VIP, Niepełnosprawni
        self.base_rate = base_rate  # Cena za godzinę
        self.vehicle = None         # Aktualnie zaparkowany pojazd
        self.is_faulty = False      # Status techniczny miejsca

    def park_vehicle(self, vehicle: Vehicle) -> bool:
        if self.vehicle or self.is_faulty:
            return False
        self.vehicle = vehicle
        return True

    def release_spot(self):
        self.vehicle = None

    def toggle_fault(self):
        self.is_faulty = not self.is_faulty
        if self.is_faulty:
            self.vehicle = None  # Usunięcie pojazdu w przypadku awarii


class ParkingSystem:
    def __init__(self):
        self.spots = {}
        self._generate_spots()

    def _generate_spots(self):
        # Generowanie miejsc
        for i in range(1, 13):
            self.spots[i] = ParkingSpot(i, "Standard", 5.0)
        for i in range(13, 17):
            self.spots[i] = ParkingSpot(i, "VIP", 10.0)
        for i in range(17, 21):
            self.spots[i] = ParkingSpot(i, "Niepełnosprawni", 3.0)

    def calculate_fee(self, spot: ParkingSpot, simulated_hours: float) -> float:
        if not spot.vehicle:
            return 0.0
        # Zaokrąglanie
        hours = math.ceil(simulated_hours)
        if hours < 1:
            hours = 1
        return hours * spot.base_rate * spot.vehicle.rate_multiplier


# INTERFEJS GRAFICZNY

class ParkingApp(tk.Tk):
    def __init__(self, parking_system: ParkingSystem):
        super().__init__()
        self.system = parking_system
        self.selected_spot_id = None

        self.title("System Zarządzania Parkingiem ")
        self.geometry("900x620")
        self.configure(bg="#f0f2f5")

        self.spot_buttons = {}
        self.create_widgets()

    def create_widgets(self):
        # Nagłówek aplikacji
        header = tk.Label(self, text="MENEDŻER PARKINGU", font=("Arial", 16, "bold"), bg="#2c3e50", fg="white", pady=10)
        header.pack(fill=tk.X)

        # Siatka i Panel Sterowania
        main_container = tk.Frame(self, bg="#f0f2f5")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # LEWA STRONA: Siatka miejsc parkingowych
        grid_frame = tk.LabelFrame(main_container, text=" Układ Miejsc Parkingowych ", font=("Arial", 11, "bold"), padx=10, pady=10)
        grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tworzenie siatki 4x5
        for idx, (spot_id, spot) in enumerate(self.system.spots.items()):
            row = idx // 5
            col = idx % 5

            btn = tk.Button(grid_frame, text=f"M{spot_id}\n({spot.spot_type[0]})", width=10, height=3,
                            font=("Arial", 9, "bold"), relief=tk.GROOVE,
                            command=lambda s_id=spot_id: self.select_spot(s_id))
            btn.grid(row=row, column=col, padx=5, pady=5)
            self.spot_buttons[spot_id] = btn

        self.update_grid_colors()

        # PRAWA STRONA: Panel boczny
        self.sidebar = tk.LabelFrame(main_container, text=" Panel Zarządzania Miejscem ", font=("Arial", 11, "bold"), padx=15, pady=10)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))

        # Widżety informacyjne panelu bocznego
        self.info_label = tk.Label(self.sidebar, text="Wybierz miejsce z siatki,\naby zarządzać rezerwacją.",
                                   font=("Arial", 10, "italic"), fg="#7f8c8d", width=30, height=4, justify=tk.LEFT)
        self.info_label.pack(anchor=tk.W, pady=10)

        ttk.Separator(self.sidebar, orient='horizontal').pack(fill='x', pady=10)

        # Sekcja: Zaparkuj Pojazd
        tk.Label(self.sidebar, text="Rejestracja pojazdu:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.reg_entry = tk.Entry(self.sidebar, font=("Arial", 10), width=25)
        self.reg_entry.pack(anchor=tk.W, pady=2)

        tk.Label(self.sidebar, text="Typ pojazdu:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(5, 0))
        self.type_combo = ttk.Combobox(self.sidebar, values=["Osobowy", "Motocykl", "Ciężarowy"], state="readonly", width=23)
        self.type_combo.current(0)
        self.type_combo.pack(anchor=tk.W, pady=2)

        self.park_btn = tk.Button(self.sidebar, text="Zarezerwuj / Zaparkuj", bg="#2ecc71", fg="white",
                                  font=("Arial", 10, "bold"), width=22, command=self.action_park, state=tk.DISABLED)
        self.park_btn.pack(pady=10)

        # Sekcja: Zwolnij Miejsce i Awaria
        ttk.Separator(self.sidebar, orient='horizontal').pack(fill='x', pady=10)

        # Pole do symulacji czasu - system opłat
        tk.Label(self.sidebar, text="Czas postoju do rozliczenia (h):", font=("Arial", 9)).pack(anchor=tk.W)
        self.hours_spin = tk.Spinbox(self.sidebar, from_=1, to=24, width=5, font=("Arial", 10))
        self.hours_spin.pack(anchor=tk.W, pady=2)

        self.leave_btn = tk.Button(self.sidebar, text="Zwolnij miejsce (Opuść)", bg="#e74c3c", fg="white",
                                   font=("Arial", 10, "bold"), width=22, command=self.action_leave, state=tk.DISABLED)
        self.leave_btn.pack(pady=5)

        self.fault_btn = tk.Button(self.sidebar, text="Zgłoś / Napraw Usterkę", bg="#f39c12", fg="white",
                                   font=("Arial", 10, "bold"), width=22, command=self.action_toggle_fault, state=tk.DISABLED)
        self.fault_btn.pack(pady=5)

        # Legenda
        self.create_legend()

    def create_legend(self):
        legend_frame = tk.Frame(self.sidebar)
        legend_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        tk.Label(legend_frame, text="Legenda stref:", font=("Arial", 8, "bold")).pack(anchor=tk.W)
        tk.Label(legend_frame, text="🟢 Wolne | 🔴 Zajęte | ⚫ Awaria", font=("Arial", 8)).pack(anchor=tk.W)
        tk.Label(legend_frame, text="Tekst: (S) Standard | (V) VIP | (N) Niepełnosprawni", font=("Arial", 8), fg="#7f8c8d").pack(anchor=tk.W)

    def update_grid_colors(self):
        for spot_id, spot in self.system.spots.items():
            btn = self.spot_buttons[spot_id]
            if spot.is_faulty:
                btn.configure(bg="#7f8c8d", fg="white")  # Szary - Awaria
            elif spot.vehicle:
                btn.configure(bg="#e74c3c", fg="white")  # Czerwony - Zajęte
            else:
                # Kolory bazowe wolnych miejsc w zależności od klasy
                if spot.spot_type == "VIP":
                    btn.configure(bg="#d4af37", fg="black")  # Złoy dla VIP
                elif spot.spot_type == "Niepełnosprawni":
                    btn.configure(bg="#3498db", fg="white")  # Niebieski niepełnoprawni
                else:
                    btn.configure(bg="#2ecc71", fg="white")  # Zielony Standard

    def select_spot(self, spot_id):
        self.selected_spot_id = spot_id
        spot = self.system.spots[spot_id]

        # Ramka wybranego przycisku
        for b_id, btn in self.spot_buttons.items():
            btn.configure(relief=tk.GROOVE, bd=2)
        self.spot_buttons[spot_id].configure(relief=tk.SUNKEN, bd=4)

        # Aktualizacja etykiety informacyjnej
        status_text = f"Miejsce: M{spot_id} ({spot.spot_type})\nStawka: {spot.base_rate} PLN/h\nStatus: "
        if spot.is_faulty:
            status_text += "AWARIA / WYŁĄCZONE"
        elif spot.vehicle:
            status_text += f"ZAJĘTE ({spot.vehicle.vehicle_type})\nRejestracja: {spot.vehicle.registration}"
        else:
            status_text += "WOLNE"

        self.info_label.configure(text=status_text, font=("Arial", 10, "bold"), fg="#2c3e50")

        # Aktywacja odpowiednich przycisków akcji
        self.fault_btn.configure(state=tk.NORMAL)
        if spot.is_faulty:
            self.park_btn.configure(state=tk.DISABLED)
            self.leave_btn.configure(state=tk.DISABLED)
        elif spot.vehicle:
            self.park_btn.configure(state=tk.DISABLED)
            self.leave_btn.configure(state=tk.NORMAL)
        else:
            self.park_btn.configure(state=tk.NORMAL)
            self.leave_btn.configure(state=tk.DISABLED)

    def action_park(self):
        if not self.selected_spot_id:
            return

        reg = self.reg_entry.get().strip()
        if not reg:
            messagebox.showerror("Błąd", "Wprowadź numer rejestracyjny pojazdu!")
            return

        v_type = self.type_combo.get()
        if v_type == "Osobowy":
            vehicle = Car(reg)
        elif v_type == "Motocykl":
            vehicle = Motorcycle(reg)
        else:
            vehicle = Truck(reg)

        spot = self.system.spots[self.selected_spot_id]
        if spot.park_vehicle(vehicle):
            self.reg_entry.delete(0, tk.END)
            self.update_grid_colors()
            self.select_spot(self.selected_spot_id)
            messagebox.showinfo("Sukces", f"Pojazd {reg} został pomyślnie zaparkowany.")
        else:
            messagebox.showerror("Błąd", "Nie można zaparkować na tym miejscu!")

    def action_leave(self):
        if not self.selected_spot_id:
            return

        spot = self.system.spots[self.selected_spot_id]
        try:
            hours = float(self.hours_spin.get())
        except ValueError:
            hours = 1.0

        fee = self.system.calculate_fee(spot, hours)

        summary = (f" PODSUMOWANIE KOSZTÓW \n"
                   f"-----------------------------\n"
                   f"Pojazd: {spot.vehicle.registration} ({spot.vehicle.vehicle_type})\n"
                   f"Typ strefy: {spot.spot_type} (baza: {spot.spot_type} PLN/h)\n"
                   f"Mnożnik pojazdu: x{spot.vehicle.rate_multiplier}\n"
                   f"Czas postoju: {hours} h\n"
                   f"-----------------------------\n"
                   f"DO ZAPŁATY: {fee:.2f} PLN")

        if messagebox.askyesno("Rozliczenie i Wyjazd", summary + "\n\nCzy potwierdzasz dokonanie opłaty i wyjazd?"):
            spot.release_spot()
            self.update_grid_colors()
            self.select_spot(self.selected_spot_id)

    def action_toggle_fault(self):
        if not self.selected_spot_id:
            return

        spot = self.system.spots[self.selected_spot_id]
        spot.toggle_fault()
        self.update_grid_colors()
        self.select_spot(self.selected_spot_id)

        status = "zgłoszona (miejsce zablokowane)" if spot.is_faulty else "naprawiona (miejsce wolne)"
        messagebox.showinfo("Status techniczny", f"Usterka na miejscu M{spot.spot_id} została {status}.")


# URUCHOMIENIE PROGRAMU

if __name__ == "__main__":
    parking_backend = ParkingSystem()
    app = ParkingApp(parking_backend)
    app.mainloop()