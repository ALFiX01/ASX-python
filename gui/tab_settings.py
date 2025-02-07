import os
import tkinter as tk
try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    import sys
    sys.exit(1)

class SettingsTab:
    def __init__(self, parent):
        self.parent = parent

        # === Settings Content Frame (Scrollable) ===
        self.settings_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent" # Transparent background for integration
        )
        self.settings_frame.pack(fill="both", expand=True, padx=20, pady=20) # Increased padding around the tab content

        self.setup_settings_page()

    def setup_settings_page(self):
        """Setup the content of the Settings tab"""

        # === Appearance Settings Card ===
        appearance_card = ctk.CTkFrame(
            self.settings_frame,
            fg_color=("gray95", "gray16"), # Светлее для светлой темы
            corner_radius=10,
            border_width=1,
            border_color=("gray80", "gray30") # Более заметная граница для светлой темы
        )
        appearance_card.pack(fill="x", padx=10, pady=(0, 15)) # Increased bottom pady for card spacing

        appearance_content = ctk.CTkFrame(appearance_card, fg_color="transparent")
        appearance_content.pack(fill="x", padx=20, pady=20) # Increased padding inside card

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
        self.appearance_mode_optionmenu.set(ctk.get_appearance_mode()) # Set default value - Оставляем эту строку, она работает для режима отображения
        self.appearance_mode_optionmenu.pack(anchor="w", pady=(0, 10))

        theme_label = ctk.CTkLabel(
            appearance_content,
            text="Тема:",
            font=("Arial", 12)
        )
        theme_label.pack(anchor="w", pady=(0, 5))

        self.theme_optionmenu = ctk.CTkOptionMenu(
            appearance_content,
            values=["Синяя", "Зеленая", "Темно-синяя"], # Example themes
            command=self.change_theme_event
        )
        # current_theme = ctk.get_default_color_theme() # Удаляем строку, вызывающую ошибку
        # theme_names = {"blue": "Синяя", "green": "Зеленая", "dark-blue": "Темно-синяя"} # Map theme names
        # self.theme_optionmenu.set(theme_names.get(current_theme, "Синяя")) # Set default based on current theme - Удаляем строку, вызывающую ошибку

        self.theme_optionmenu.set("Синяя") # Устанавливаем тему "Синяя" по умолчанию жестко
        self.theme_optionmenu.pack(anchor="w")

        # === Language Settings Card ===
        language_card = ctk.CTkFrame(
            self.settings_frame,
            fg_color=("gray95", "gray16"),
            corner_radius=10,
            border_width=1,
            border_color=("gray80", "gray30")
        )
        language_card.pack(fill="x", padx=10, pady=(15, 15)) # Increased top and bottom pady for card spacing

        language_content = ctk.CTkFrame(language_card, fg_color="transparent")
        language_content.pack(fill="x", padx=20, pady=20)

        language_title_label = ctk.CTkLabel(
            language_content,
            text="Язык (Разработка)", # Indicate it's under development
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
            values=["Русский", "English (Soon)"], # Example languages, "Soon" for not yet implemented
            state="disabled" # пока disabled, функционал в разработке
        )
        self.language_optionmenu.set("Русский") # Default language
        self.language_optionmenu.pack(anchor="w")


    def change_appearance_mode_event(self, new_appearance_mode: str):
        """Changes the appearance mode of the application."""
        if new_appearance_mode == "Системный":
            ctk.set_appearance_mode("System")
        elif new_appearance_mode == "Светлый":
            ctk.set_appearance_mode("Light")
        elif new_appearance_mode == "Темный":
            ctk.set_appearance_mode("Dark")

    def change_theme_event(self, new_theme: str):
        """Changes the color theme of the application."""
        theme_values = {"Синяя": "blue", "Зеленая": "green", "Темно-синяя": "dark-blue"}
        theme_name = theme_values.get(new_theme, "blue") # Default to blue if not found
        ctk.set_default_color_theme(theme_name)


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Settings Tab Example")
    app.geometry("800x700")

    settings_tab = SettingsTab(app) # You would usually create this tab within your main app

    app.mainloop()