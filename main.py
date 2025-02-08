import os
import sys
import ctypes
import platform
import tkinter as tk
import json
try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    sys.exit(1)

from gui.tab_tweaks import TweaksTab
from gui.tab_programs import ProgramsTab
from gui.tab_utilities import UtilitiesTab
from gui.tab_WebResources import WebResourcesTab
from gui.tab_information import InformationTab
from gui.tab_settings import SettingsTab

APP_VERSION = "0.0.05"

def is_admin():
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin()
        return True
    except:
        return False

class ASXHub(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"ASX Hub v{APP_VERSION}")
        self.geometry("1050x800")
        self.minsize(1050, 750)

        self.load_and_apply_settings()  # Load and apply settings

        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabview = ctk.CTkTabview(self.main_container)
        self.tabview.pack(fill="both", expand=True)

        self.tab_tweaks = self.tabview.add("Твики")
        self.tab_programs = self.tabview.add("Программы")
        self.tab_utilities = self.tabview.add("Утилиты")
        self.tab_web = self.tabview.add("Веб-ресурсы")
        self.tab_info = self.tabview.add("Информация")
        self.tab_settings = self.tabview.add("Настройка")

        self.tweaks_tab = TweaksTab(self.tab_tweaks)
        self.programs_tab = ProgramsTab(self.tab_programs)
        self.utilities_tab = UtilitiesTab(self.tab_utilities)
        self.web_resources_tab = WebResourcesTab(self.tab_web)
        self.information_tab = InformationTab(self.tab_info)
        self.settings_tab = SettingsTab(self.tab_settings)

        self.status_bar = ctk.CTkFrame(self.main_container, height=30)
        self.status_bar.pack(fill="x", pady=(5, 0))

        self.version_label = ctk.CTkLabel(
            self.status_bar,
            text=f"Версия: {APP_VERSION}",
            font=("Arial", 12)
        )
        self.version_label.pack(side="left", padx=10)

        admin_text = "Администратор" if is_admin() else "Обычный пользователь"
        self.admin_label = ctk.CTkLabel(
            self.status_bar,
            text=admin_text,
            font=("Arial", 12)
        )
        self.admin_label.pack(side="right", padx=10)

    def load_and_apply_settings(self):
        """Loads settings and applies them, handling 'System' mode."""
        settings_file = "settings.json"
        try:
            with open(settings_file, "r") as f:
                settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            settings = {
                "appearance_mode": "System",  # Default to System
                "theme": "blue"
            }
            try:
                with open(settings_file, "w") as f:
                    json.dump(settings, f, indent=4)
            except Exception as e:
                print(f"Error creating default settings file: {e}")

        # --- CRITICAL: Handle 'System' mode correctly ---
        if settings["appearance_mode"] == "System":
            import darkdetect
            system_mode = "Dark" if darkdetect.isDark() else "Light"
            ctk.set_appearance_mode(system_mode)
        else:
            ctk.set_appearance_mode(settings["appearance_mode"])

        ctk.set_default_color_theme(settings["theme"])

def main():
    if platform.system() == "Windows" and not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    app = ASXHub()
    app.mainloop()

if __name__ == "__main__":
    main()