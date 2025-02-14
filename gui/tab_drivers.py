import os
import json
import sys
import threading
import tkinter as tk
import asyncio
import subprocess
import re
from collections import defaultdict

try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found.  Please install it using: pip install customtkinter")
    sys.exit(1)

from config import TWEAK_CATEGORIES, TWEAKS  #  Keep this for potential future use with the sidebar.
from utils.system_tweaks import SystemTweaks  # Keep this for similar reasons


def load_settings(settings_file="settings.json"):
    """Загружает настройки из JSON-файла."""
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
    """Виджет статус-бара с возможностью обновления текста."""
    def __init__(self, parent, default_text="", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.label = ctk.CTkLabel(self, text=default_text, anchor="w")
        self.label.pack(side="left", padx=10)
        self.configure(height=25)  # Фиксированная высота
        self.pack(side="bottom", fill="x")  # Расположение внизу и растягивание по X
        self._after_id = None

    def update_text(self, text, duration=0):
        """Обновляет текст статус-бара."""
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

        self.label.configure(text=text)
        if duration > 0:
            self._after_id = self.after(duration, lambda: self.update_text(""))


class DriverTab:
    """Вкладка для управления драйверами."""

    def __init__(self, parent, status_bar):
        self.parent = parent
        self.status_bar = status_bar
        self.drivers = []
        self.outdated_drivers = []
        self.accent_color = settings.get("accent_color", "#FF5733")
        self._setup_ui()
        self.load_drivers()  # Load drivers immediately on initialization


    def _setup_ui(self):
        """Настройка пользовательского интерфейса вкладки."""
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)  #  Single column, takes all space
        self.main_frame.grid_rowconfigure(0, weight=1)

        #  No sidebar needed specifically for drivers in this design
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.grid(row=0, column=0, sticky="nsew") #  Place content directly
        self.content_frame.grid_rowconfigure(0, weight=1)  # Allow content area to grow
        self.content_frame.grid_columnconfigure(0, weight=1)

        self._create_content_area()


    def _create_content_area(self):
        """Создание области для отображения списка драйверов."""
        self.scrollable_content = ctk.CTkScrollableFrame(
            self.content_frame, corner_radius=10, fg_color=("gray85", "gray17")
        )
        self.scrollable_content.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        self.scrollable_content.grid_columnconfigure(0, weight=1) # Make content fill scrollable area.

    def run_pnputil(self):
        """Выполняет команду pnputil /enum-drivers и возвращает её вывод."""
        try:
            result = subprocess.run(['pnputil', '/enum-drivers'], capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.status_bar.update_text(f"Ошибка выполнения pnputil: {e.stderr}", duration=5000)
            return ""

    def parse_pnputil_output(self, output):
        """Парсит вывод pnputil и собирает данные о драйверах."""
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
        """Преобразует строку версии в кортеж чисел для сравнения."""
        numbers = re.findall(r'\d+', version_str)
        return tuple(map(int, numbers)) if numbers else (0,)

    def date_to_tuple(self, date_str):
        """Преобразует дату из MM/DD/YYYY в (YYYY, MM, DD)."""
        try:
            mm, dd, yyyy = map(int, date_str.split("/"))
            return (yyyy, mm, dd)
        except ValueError:
            return (0, 0, 0)

    def find_outdated_drivers(self, drivers):
        """Определяет устаревшие драйверы."""
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
        """Удаляет драйвер через pnputil."""
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
        """Открывает диалоговое окно подтверждения удаления и удаляет драйвер."""
        dialog = ctk.CTkInputDialog(
            text=f"Вы уверены, что хотите удалить драйвер {driver['Published Name']}?\nВведите 'yes' для подтверждения.",
            title="Подтверждение удаления"
        )
        confirmation = dialog.get_input()
        if confirmation and confirmation.lower() == 'yes':
            if self.delete_driver(driver):
                self.load_drivers()  # Reload after deletion

    def display_drivers(self):
        """Отображает информацию о драйверах в интерфейсе."""
        for widget in self.scrollable_content.winfo_children():
            widget.destroy()

        container = ctk.CTkFrame(self.scrollable_content, corner_radius=8, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=5, pady=5)
        container.grid_columnconfigure(0, weight=1) # Make the container fill the space

        if self.outdated_drivers:
            label = ctk.CTkLabel(container, text="Найдены устаревшие драйверы:", font=("Roboto", 16, "bold"))
            label.grid(row=0, column=0, sticky="w", pady=(10, 5), padx=10) # Use grid for layout
            row_num = 1

            for i, drv in enumerate(self.outdated_drivers, start=1):
                driver_frame = ctk.CTkFrame(container, corner_radius=10, fg_color=("gray90", "gray20"), border_width=1, border_color=("gray80", "gray30"))
                driver_frame.grid(row=row_num, column=0, sticky="ew", padx=10, pady=8) # Use grid, sticky EW
                driver_frame.columnconfigure(0, weight=1) # Make info label expand
                row_num += 1


                info_label = ctk.CTkLabel(driver_frame, text=f"{i}. {drv['Published Name']} | {drv['Original Name']} | Версия: {drv['Driver Version']} | Дата: {drv['Driver Date']}", font=("Roboto", 12), wraplength=600, justify="left")
                info_label.grid(row=0, column=0, sticky="ew", padx=10, pady=10) # Use grid, sticky EW

                delete_button = ctk.CTkButton(driver_frame, text="Удалить", command=lambda d=drv: self.confirm_and_delete(d), fg_color="red", hover_color="darkred", text_color="white")
                delete_button.grid(row=0, column=1, sticky="e", padx=10, pady=10)  # Use grid, sticky E
        else:
            label = ctk.CTkLabel(container, text="Все драйверы актуальны.", font=("Roboto", 16, "bold"))
            label.grid(row=0, column=0, sticky="w", pady=20, padx=10)

    def load_drivers(self):
        """Загружает и отображает информацию о драйверах."""
        output = self.run_pnputil()
        if output:
            self.drivers = self.parse_pnputil_output(output)
            self.outdated_drivers = self.find_outdated_drivers(self.drivers)
        self.display_drivers()


class App(ctk.CTk):
    """Главное окно приложения."""

    def __init__(self):
        super().__init__()
        self.title("Driver and System Tweaker")
        self.geometry("800x600")
        self.dynamic_status = DynamicStatusBar(self, default_text="Ready")  # Create status bar first

        self.notebook = ctk.CTkTabview(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.driver_tab_frame = self.notebook.add("Драйверы")
        # Correct instantiation: Pass self.dynamic_status
        self.driver_tab = DriverTab(self.driver_tab_frame, self.dynamic_status)

        # You could add the TweaksTab back here if needed in the future
        # self.tweaks_tab_frame = self.notebook.add("Твики")
        # self.tweaks_tab = TweaksTab(self.tweaks_tab_frame, self.dynamic_status)


if __name__ == "__main__":
    app = App()
    app.mainloop()