import os
import sys
import ctypes
import platform
import tkinter as tk
try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    sys.exit(1)

from gui.tab_tweaks import TweaksTab
from gui.tab_programs import ProgramsTab
from gui.tab_utilities import UtilitiesTab

APP_VERSION = "1.0.0"

def is_admin():
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin()
        return True  # На других ОС пока считаем, что права есть
    except:
        return False

class ASXHub(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title(f"ASX Hub v{APP_VERSION}")
        self.geometry("900x600")
        self.minsize(800, 500)

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Create main tabview
        self.tabview = ctk.CTkTabview(self.main_container)
        self.tabview.pack(fill="both", expand=True)

        # Add tabs
        self.tab_tweaks = self.tabview.add("Твики")
        self.tab_programs = self.tabview.add("Программы")
        self.tab_utilities = self.tabview.add("Утилиты")
        self.tab_web = self.tabview.add("Веб-ресурсы")
        self.tab_info = self.tabview.add("Информация")
        self.tab_settings = self.tabview.add("Настройка")

        # Initialize tab contents
        self.tweaks_tab = TweaksTab(self.tab_tweaks)
        self.programs_tab = ProgramsTab(self.tab_programs)
        self.utilities_tab = UtilitiesTab(self.tab_utilities)

        # Create status bar
        self.status_bar = ctk.CTkFrame(self.main_container, height=30)
        self.status_bar.pack(fill="x", pady=(5, 0))

        # Version label
        self.version_label = ctk.CTkLabel(
            self.status_bar,
            text=f"Версия: {APP_VERSION}",
            font=("Arial", 12)
        )
        self.version_label.pack(side="left", padx=10)

        # Admin status
        admin_text = "Администратор" if is_admin() else "Обычный пользователь"
        self.admin_label = ctk.CTkLabel(
            self.status_bar,
            text=admin_text,
            font=("Arial", 12)
        )
        self.admin_label.pack(side="right", padx=10)

def main():
    if platform.system() == "Windows" and not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    app = ASXHub()
    app.mainloop()

if __name__ == "__main__":
    main()