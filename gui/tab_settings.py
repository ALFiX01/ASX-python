import os
import tkinter as tk
import json

try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    import sys
    sys.exit(1)

class SettingsTab:
    def __init__(self, parent):
        self.parent = parent
        self.settings_file = "settings.json"
        self.load_settings()
        self.setup_settings_page()

    def load_settings(self):
        """Loads settings from the settings file."""
        try:
            with open(self.settings_file, "r") as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {
                "appearance_mode": "System",
                "theme": "blue"
            }
        except json.JSONDecodeError:
            print("Warning: settings.json is corrupted. Using default settings.")
            self.settings = {
                "appearance_mode": "System",
                "theme": "blue"
            }

    def save_settings(self):
        """Saves the current settings to the settings file."""
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def setup_settings_page(self):
        """Setup the content of the Settings tab"""
        self.settings_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent"  # Keep this transparent
        )
        self.settings_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # === Appearance Settings Card ===
        appearance_card = ctk.CTkFrame(
            self.settings_frame,
            fg_color=("gray95", "gray16"),
            corner_radius=10,
        )
        appearance_card.pack(fill="x", padx=10, pady=(0, 15))

        # Inner frame: Set fg_color explicitly, corner_radius=0
        appearance_content = ctk.CTkFrame(
            appearance_card,
            fg_color=("gray95", "gray16"),  # Match the card's fg_color
            corner_radius=0  # No rounded corners needed here
        )
        appearance_content.pack(fill="x", padx=20, pady=20)

        appearance_title_label = ctk.CTkLabel(
            appearance_content,
            text="Внешний вид",
            font=("Arial", 20, "bold")
        )
        appearance_title_label.pack(anchor="w", pady=(0, 10))

        appearance_mode_label = ctk.CTkLabel(
            appearance_content,
            text="Режим отображения:",
            font=("Arial", 12)
        )
        appearance_mode_label.pack(anchor="w", pady=(0, 5))

        self.appearance_mode_optionmenu = ctk.CTkOptionMenu(
            appearance_content,
            values=["Системный", "Светлый", "Темный"],
            command=self.change_appearance_mode_event
        )
        mode_map = {"System": "Системный", "Light": "Светлый", "Dark": "Темный"}
        self.appearance_mode_optionmenu.set(mode_map.get(self.settings["appearance_mode"], "Системный"))
        self.appearance_mode_optionmenu.pack(anchor="w", pady=(0, 10))

        theme_label = ctk.CTkLabel(
            appearance_content,
            text="Тема:",
            font=("Arial", 12)
        )
        theme_label.pack(anchor="w", pady=(0, 5))

        self.theme_optionmenu = ctk.CTkOptionMenu(
            appearance_content,
            values=["Синяя", "Зеленая", "Темно-синяя"],
            command=self.change_theme_event,
            state = "disabled"
        )
        theme_map = {"blue": "Синяя", "green": "Зеленая", "dark-blue": "Темно-синяя"}
        self.theme_optionmenu.set(theme_map.get(self.settings["theme"], "Синяя"))
        self.theme_optionmenu.pack(anchor="w")

        # === Language Settings Card ===
        language_card = ctk.CTkFrame(
            self.settings_frame,
            fg_color=("gray95", "gray16"),
            corner_radius=10,
        )
        language_card.pack(fill="x", padx=10, pady=(15, 15))

        # Inner frame: Set fg_color explicitly, corner_radius=0
        language_content = ctk.CTkFrame(
            language_card,
            fg_color=("gray95", "gray16"),  # Match the card's fg_color
            corner_radius=0   # No rounded corners needed
        )
        language_content.pack(fill="x", padx=20, pady=20)

        language_title_label = ctk.CTkLabel(
            language_content,
            text="Язык (Разработка)",
            font=("Arial", 20, "bold")
        )
        language_title_label.pack(anchor="w", pady=(0, 10))

        language_label = ctk.CTkLabel(
            language_content,
            text="Язык приложения:",
            font=("Arial", 12)
        )
        language_label.pack(anchor="w", pady=(0, 5))

        self.language_optionmenu = ctk.CTkOptionMenu(
            language_content,
            values=["Русский", "English (Soon)"],
            state="disabled"
        )
        self.language_optionmenu.set("Русский")
        self.language_optionmenu.pack(anchor="w")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        """Changes the appearance mode."""
        mode_map = {"Системный": "System", "Светлый": "Light", "Темный": "Dark"}
        mode_value = mode_map.get(new_appearance_mode, "System")
        ctk.set_appearance_mode(mode_value)
        self.settings["appearance_mode"] = mode_value
        self.save_settings()
        self.update_colors()  # Call a dedicated color update function

    def change_theme_event(self, new_theme: str):
        theme_values = {"Синяя": "blue", "Зеленая": "green", "Темно-синяя": "dark-blue"}
        theme_name = theme_values.get(new_theme, "blue")
        ctk.set_default_color_theme(theme_name)
        self.settings["theme"] = theme_name
        self.save_settings()
        self.update_colors()

        # Принудительное обновление интерфейса
        self.parent.update_idletasks()

    def update_colors(self):
        """Updates the colors of frames that need explicit updates."""

        # Get the correct colors based on the current appearance mode
        light_color = "gray95"
        dark_color = "gray16"
        current_bg_color = light_color if ctk.get_appearance_mode() == "Light" else dark_color

        # Explicitly update the inner frames
        for widget in self.settings_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                # Update the outer card frames
                widget.configure(fg_color=current_bg_color)
                for inner_widget in widget.winfo_children():
                    if isinstance(inner_widget, ctk.CTkFrame):
                        # Update inner content frames
                        inner_widget.configure(fg_color=current_bg_color)

        # Use update_idletasks() *after* setting the colors, not before.
        self.parent.update_idletasks()


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Settings Tab Example")
    app.geometry("800x700")
    settings_tab = SettingsTab(app)
    app.mainloop()