import os
import json
import sys
import threading
import tkinter as tk
import asyncio
import subprocess
import re
from collections import defaultdict
from tkinter import ttk  # Import ttk for themed widgets

try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    sys.exit(1)

from config import TWEAK_CATEGORIES, TWEAKS  # Keep for future use
from utils.system_tweaks import SystemTweaks  # Keep for future use

def load_settings(settings_file="settings.json"):
    """Loads settings from a JSON file."""
    try:
        with open(settings_file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading settings: {e}. Using default settings.")
        return {
            "appearance_mode": "System",
            "theme": "blue",
            "language": "Russian",
            "accent_color": "#1f6aa5"
        }

settings = load_settings()
ctk.set_appearance_mode(settings.get("appearance_mode", "System"))
ctk.set_default_color_theme(settings.get("theme", "blue"))

def start_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

loop = asyncio.new_event_loop()
threading.Thread(target=start_asyncio_loop, args=(loop,), daemon=True).start()

class DynamicStatusBar(ctk.CTkFrame):
    """Status bar widget with text update capability."""
    def __init__(self, parent, default_text="", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.label = ctk.CTkLabel(self, text=default_text, anchor="w")
        self.label.pack(side="left", padx=10)
        self.configure(height=25)
        self.pack(side="bottom", fill="x")
        self._after_id = None

    def update_text(self, text, duration=0):
        """Updates the status bar text."""
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

        self.label.configure(text=text)
        if duration > 0:
            self._after_id = self.after(duration, lambda: self.update_text(""))

class DriverTab:
    """Tab for managing drivers."""

    def __init__(self, parent, status_bar):
        self.parent = parent
        self.status_bar = status_bar
        self.drivers = []
        self.outdated_drivers = []
        self.accent_color = settings.get("accent_color", "#1f6aa5")
        self.driver_descriptions = self.load_driver_descriptions()  # Load descriptions
        self._setup_ui()
        self.load_drivers()  # Load drivers on initialization

    def _setup_ui(self):
        """Sets up the user interface for the tab."""
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)  # Allow for expansion

        #  Content frame
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)


        self._create_content_area()

    def _create_content_area(self):
        """Creates the area to display the driver list."""
        self.scrollable_content = ctk.CTkScrollableFrame(
            self.content_frame, corner_radius=10, fg_color=("gray85", "gray17")
        )
        self.scrollable_content.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        self.scrollable_content.grid_columnconfigure(0, weight=1)

        # Add a refresh button
        self.refresh_button = ctk.CTkButton(
            self.content_frame, text="Обновить", command=self.load_drivers,
            font=("Roboto", 14)
        )
        self.refresh_button.grid(row=1, column=0, pady=(0, 10))  # Place below scrollable frame

        # Search bar will be created conditionally
        self.search_var = None
        self.search_entry = None

    def load_driver_descriptions(self, filename="driver_descriptions.json"):
        """Loads driver descriptions from a JSON file."""
        try:
            with open(filename, "r", encoding="utf-8") as f:  # Ensure UTF-8 encoding
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading driver descriptions: {e}")
            return {}  # Return an empty dict if the file is missing or invalid

    def get_driver_description(self, original_name):
        """Retrieves the description for a driver based on its original name."""
        return self.driver_descriptions.get(original_name, "Описание отсутствует.")

    def run_pnputil(self):
        """Executes the pnputil /enum-drivers command and returns its output."""
        try:
            result = subprocess.run(['pnputil', '/enum-drivers'], capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.status_bar.update_text(f"Ошибка выполнения pnputil: {e.stderr}", duration=5000)
            return ""

    def parse_pnputil_output(self, output):
        """Parses the pnputil output and collects driver data."""
        drivers = []
        current_driver = {}
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("Опубликованное имя:"):
                if current_driver:
                    drivers.append(current_driver)
                current_driver = {"Published Name": line.split(":", 1)[1].strip()}
            elif line.startswith("Исходное имя:"):
                current_driver["Original Name"] = line.split(":", 1)[1].strip()
            elif line.startswith("Имя поставщика:"):
                current_driver["Provider"] = line.split(":", 1)[1].strip()
            elif line.startswith("Имя класса:"):
                current_driver["Class"] = line.split(":", 1)[1].strip()
            elif line.startswith("Версия драйвера:"):
                parts = line.split(":", 1)[1].strip().split(" ")
                if len(parts) == 2:
                    current_driver["Driver Date"] = parts[0].strip()
                    current_driver["Driver Version"] = parts[1].strip()
        if current_driver:
            drivers.append(current_driver)
        return drivers

    def version_to_tuple(self, version_str):
        """Converts a version string to a tuple of numbers for comparison."""
        numbers = re.findall(r'\d+', version_str)
        return tuple(map(int, numbers)) if numbers else (0,)

    def date_to_tuple(self, date_str):
        """Converts a date from MM/DD/YYYY to (YYYY, MM, DD)."""
        try:
            mm, dd, yyyy = map(int, date_str.split("/"))
            return (yyyy, mm, dd)
        except ValueError:
            return (0, 0, 0)

    def find_outdated_drivers(self, drivers):
        """Identifies outdated drivers."""
        groups = defaultdict(list)
        for driver in drivers:
            key = (driver.get("Original Name", ""), driver.get("Class", ""), driver.get("Provider", ""))
            groups[key].append(driver)

        outdated = []
        for key, group in groups.items():
            if len(group) > 1:
                sorted_group = sorted(
                    group,
                    key=lambda d: (self.date_to_tuple(d.get("Driver Date", "0/0/0")),
                                   self.version_to_tuple(d.get("Driver Version", "0"))),
                    reverse=True
                )
                outdated.extend(sorted_group[1:])
        return outdated

    def delete_driver(self, driver):
        """Deletes a driver via pnputil."""
        published_name = driver.get("Published Name")
        if not published_name:
            self.status_bar.update_text("Нет 'Published Name' для удаления драйвера.", duration=3000)
            return False

        command = f'pnputil /delete-driver "{published_name}" /uninstall /force'
        self.status_bar.update_text(f"Удаление драйвера: {published_name}...", duration=2000)

        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            self.status_bar.update_text(f"Драйвер {published_name} удалён.", duration=3000)
            return True
        except subprocess.CalledProcessError as e:
            self.status_bar.update_text(f"Ошибка при удалении {published_name}: {e.stderr}", duration=4000)
            return False

    def confirm_and_delete(self, driver):
        """Opens a confirmation dialog before deleting a driver."""
        # Use CTkDialog for better styling consistency
        dialog = ctk.CTkInputDialog(
            text=f"Вы уверены, что хотите удалить драйвер {driver['Published Name']}?\nВведите 'yes' для подтверждения.",
            title="Подтверждение удаления"
        )
        confirmation = dialog.get_input()

        if confirmation and confirmation.lower() == 'yes':
            if self.delete_driver(driver):
                self.load_drivers()

    def display_drivers(self):
        """Displays driver information in the UI, with descriptions below each driver."""
        for widget in self.scrollable_content.winfo_children():
            widget.destroy()

        if not self.outdated_drivers:
            label = ctk.CTkLabel(self.scrollable_content, text="Все драйверы актуальны.", font=("Roboto", 16, "bold"))
            label.pack(pady=20)
            return

        # Conditionally create the search bar if there are more than 10 outdated drivers
        if len(self.outdated_drivers) > 10:
            if self.search_var is None:
                self.search_var = tk.StringVar()
                self.search_var.trace_add("write", self.filter_drivers)
                self.search_entry = ctk.CTkEntry(
                    self.content_frame, textvariable=self.search_var, placeholder_text="Поиск драйверов..."
                )
                self.search_entry.grid(row=2, column=0, pady=(0, 10), sticky="ew")
        elif self.search_entry:
            self.search_entry.grid_forget()


        label = ctk.CTkLabel(self.scrollable_content, text="Здесь перечислены драйверы, которые ASX Hub считает устаревшими. Их можно удалить, но не факт что это безопасно.", font=("Segoe UI Semilight Italic", 15), wraplength=850, justify="center")
        label.pack(pady=(5,5))

        # --- Driver Entries ---
        for drv in self.outdated_drivers:
            driver_frame = ctk.CTkFrame(self.scrollable_content, corner_radius=10, fg_color=("gray90", "gray20"))  # Card for each driver
            driver_frame.pack(fill="x", expand=False, padx=5, pady=5)  # Padding around driver card

            driver_frame.grid_columnconfigure(0, weight=1) # Name column takes all available space
            driver_frame.grid_columnconfigure(1, weight=0) # Button column fits content

            # --- Row 1: Name and Delete Button ---
            ctk.CTkLabel(driver_frame, text=drv.get('Original Name', 'N/A'), font=("Segoe UI", 15, "bold"), wraplength=300, justify="left", anchor="w").grid(row=0, column=0, sticky="ew", padx=(10, 20), pady=(10, 0))  # Increased padx, pady
            delete_button = ctk.CTkButton(driver_frame, text="Удалить Драйвер", command=lambda d=drv: self.confirm_and_delete(d), fg_color="#d05858", hover_color="darkred", text_color="white", width=80, font=("Roboto", 13))  # Increased font for button
            delete_button.grid(row=0, column=1, sticky="e", padx=10, pady=(10, 0))  # Increased padx, pady

            # --- Row 2: Version and Date ---
            version_date_frame = ctk.CTkFrame(driver_frame, fg_color="transparent") # Frame to group version and date
            version_date_frame.grid(row=1, column=0, columnspan=1, sticky="ew", padx=(10, 20), pady=(0, 0))
            version_date_frame.grid_columnconfigure(0, weight=1) # Version column
            version_date_frame.grid_columnconfigure(1, weight=1) # Date column

            ctk.CTkLabel(version_date_frame, text=f"Версия: {drv.get('Driver Version', 'N/A')}", font=("Consolas", 13), anchor="w").grid(row=0, column=0, sticky="ew", padx=0, pady=0)  # Increased padx, pady
            ctk.CTkLabel(version_date_frame, text=f"Дата: {drv.get('Driver Date', 'N/A')}", font=("Consolas", 13), anchor="w").grid(row=1, column=0, sticky="ew", padx=0, pady=0)  # Increased padx, pady


            # --- Row 3: Description ---
            description = self.get_driver_description(drv.get('Original Name', ''))
            description_label = ctk.CTkLabel(driver_frame, text=description, font=("Roboto", 12), wraplength=700, justify="left", anchor="w", fg_color=("gray94", "gray25"), corner_radius=6)  # Slightly lighter background for description, increased corner_radius
            description_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(8, 10))  # Increased padx, pady


    def filter_drivers(self, *args):
        """Filters the displayed drivers based on the search query."""
        query = self.search_var.get().lower()
        filtered_drivers = [drv for drv in self.outdated_drivers if query in drv.get('Original Name', '').lower()]
        self.display_filtered_drivers(filtered_drivers)

    def display_filtered_drivers(self, drivers):
        """Displays the filtered list of drivers."""
        for widget in self.scrollable_content.winfo_children():
            widget.destroy()

        if not drivers:
            label = ctk.CTkLabel(self.scrollable_content, text="Нет совпадений.", font=("Roboto", 16, "bold"))
            label.pack(pady=20)
            return

        # --- Header Removed ---

        # --- Driver Entries ---
        for drv in drivers:
            driver_frame = ctk.CTkFrame(self.scrollable_content, corner_radius=10, fg_color=("gray90", "gray20"))  # Card for each driver
            driver_frame.pack(fill="x", expand=False, padx=5, pady=5)  # Padding around driver card

            driver_frame.grid_columnconfigure(0, weight=1) # Name column takes all available space
            driver_frame.grid_columnconfigure(1, weight=0) # Button column fits content

            # --- Row 1: Name and Delete Button ---
            ctk.CTkLabel(driver_frame, text=drv.get('Original Name', 'N/A'), font=("Roboto", 12), wraplength=300, justify="left", anchor="w").grid(row=0, column=0, sticky="ew", padx=(10, 20), pady=(10, 0))  # Increased padx, pady
            delete_button = ctk.CTkButton(driver_frame, text="Удалить", command=lambda d=drv: self.confirm_and_delete(d), fg_color="#d05858", hover_color="darkred", text_color="white", width=80, font=("Roboto", 12))  # Increased font for button
            delete_button.grid(row=0, column=1, sticky="e", padx=10, pady=(10, 0))  # Increased padx, pady

            # --- Row 2: Version and Date ---
            version_date_frame = ctk.CTkFrame(driver_frame, fg_color="transparent") # Frame to group version and date
            version_date_frame.grid(row=1, column=0, columnspan=1, sticky="ew", padx=(10, 20), pady=(0, 0))
            version_date_frame.grid_columnconfigure(0, weight=1) # Version column
            version_date_frame.grid_columnconfigure(1, weight=1) # Date column

            ctk.CTkLabel(version_date_frame, text=f"Версия: {drv.get('Driver Version', 'N/A')}", font=("Roboto", 12), anchor="w").grid(row=0, column=0, sticky="ew", padx=0, pady=0)  # Increased padx, pady
            ctk.CTkLabel(version_date_frame, text=f"Дата: {drv.get('Driver Date', 'N/A')}", font=("Roboto", 12), anchor="w").grid(row=1, column=0, sticky="ew", padx=0, pady=0)  # Increased padx, pady


            # --- Row 3: Description ---
            description = self.get_driver_description(drv.get('Original Name', ''))
            description_label = ctk.CTkLabel(driver_frame, text=description, font=("Roboto", 12), wraplength=700, justify="left", anchor="w", fg_color=("gray94", "gray25"), corner_radius=6)  # Slightly lighter background for description, increased corner_radius
            description_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(8, 10))  # Increased padx, pady


    def load_drivers(self):
        """Loads and displays driver information."""
        self.status_bar.update_text("Загрузка драйверов...")  # Immediate feedback
        output = self.run_pnputil()
        if output:
            self.drivers = self.parse_pnputil_output(output)
            self.outdated_drivers = self.find_outdated_drivers(self.drivers)
            self.status_bar.update_text("Драйверы загружены.", duration=3000)  # Completion message
        else:
            self.status_bar.update_text("Не удалось загрузить драйверы.", duration=5000)  # Error message
        self.display_drivers()

class App(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("Driver and System Tweaker")
        self.geometry("1050x800")  # Increased width for descriptions
        self.dynamic_status = DynamicStatusBar(self, default_text="")

        self.notebook = ctk.CTkTabview(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.driver_tab_frame = self.notebook.add("Драйверы")
        self.driver_tab = DriverTab(self.driver_tab_frame, self.dynamic_status)

if __name__ == "__main__":
    app = App()
    app.mainloop()