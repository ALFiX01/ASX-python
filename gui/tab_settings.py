import json
import sys

try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Install it: pip install customtkinter")
    sys.exit(1)


class SettingsTab:
    """Manages the settings tab and its UI elements."""

    def __init__(self, parent):
        self.parent = parent
        self.settings_file = "settings.json"
        self.settings = self._load_settings()
        self.ui = {}  # Dictionary to store UI elements
        self.accent_color = None  # Store the accent color
        self.setup_ui()
        self._apply_settings()

    def _load_settings(self):
        """Loads settings; uses defaults if loading fails."""
        try:
            with open(self.settings_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading settings: {e}. Using default settings.")
            return {
                "appearance_mode": "System",
                "theme": "blue",
                "language": "Russian",
            }

    def _save_settings(self):
        """Saves settings to the JSON file."""
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)
        except OSError as e:
            print(f"Error saving settings: {e}")

    def setup_ui(self):
        """Creates all UI elements for the settings tab."""
        self.settings_frame = ctk.CTkScrollableFrame(
            self.parent, fg_color="transparent"
        )
        self.settings_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._create_appearance_card()
        self._create_language_card()
        self._create_example_card()  # Add an example card

    def _create_appearance_card(self):
        """Creates the appearance settings card."""
        card = self._create_card("Внешний вид")

        self.ui["theme_label"] = self._create_label(card, "Тема приложения:", font=("Montserrat", 13))
        self.ui["theme_optionmenu"] = self._create_option_menu(
            card, ["Синяя", "Зеленая", "Темно-синяя"], self.change_theme, font=("Roboto", 13),
            text_color=("#f0f0f0")
        )

        self.ui["theme_restart_label"] = self._create_label(
            card,
            "*Для смены темы нужен перезапуск приложения",
            text_color=("#7E7E7E")  # Корректный формат для светлой/темной темы
        )

    def _create_language_card(self):
        """Creates the language settings card."""
        card = self._create_card("Язык (Разработка)")

        self.ui["language_label"] = self._create_label(card, "Язык приложения:", font=("Montserrat", 13)) # Changed Font
        self.ui["language_optionmenu"] = self._create_option_menu(
            card, ["Русский", "English (Soon)"], None, state="disabled", font=("Roboto", 13),
            text_color=("#f0f0f0")
        )

    def _create_example_card(self):
        """Creates a card with example widgets to demonstrate accent color."""
        card = self._create_card("Пример")

        # Add some example widgets.  These will have their accent colors changed.
        self.ui["example_button"] = ctk.CTkButton(card, text="Кнопка")
        self.ui["example_button"].pack(pady=5)

        self.ui["example_checkbox"] = ctk.CTkCheckBox(card, text="Чекбокс")
        self.ui["example_checkbox"].pack(pady=5)

        self.ui["example_slider"] = ctk.CTkSlider(card)
        self.ui["example_slider"].pack(pady=5)

        self.ui["example_progressbar"] = ctk.CTkProgressBar(card)
        self.ui["example_progressbar"].pack(pady=5)
        self.ui["example_progressbar"].set(0.5)  # set progress

    def _create_card(self, title_text):
        """Helper function to create a settings card."""
        card_frame = ctk.CTkFrame(
            self.settings_frame, fg_color=("gray85", "gray17"), corner_radius=10
        )
        card_frame.pack(fill="x", padx=10, pady=(0, 15))

        content_frame = ctk.CTkFrame(
            card_frame, fg_color=("gray85", "gray17"), corner_radius=0
        )
        content_frame.pack(fill="x", padx=20, pady=20)

        title_label = ctk.CTkLabel(
            content_frame, text=title_text, font=("Montserrat", 21, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 10))

        return content_frame

    def _create_label(self, parent, text, text_color=None, font=("Roboto", 13)): # Added font
        """Helper function to create a label."""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=font, # Using provided font
            text_color=text_color  # Передаем цвет текста
        )
        label.pack(anchor="w", pady=(0, 5))
        return label

    def _create_option_menu(self, parent, values, command, state="normal", font=None, text_color=None):
        menu = ctk.CTkOptionMenu(parent, values=values, command=command, state=state, font=font, text_color=text_color)
        menu.pack(anchor="w", pady=(0, 10))
        return menu

    def _apply_settings(self):
        """Applies loaded settings."""
        theme_map = {"blue": "Синяя", "green": "Зеленая", "dark-blue": "Темно-синяя"}
        # Correct color map for CustomTkinter
        color_map = {
            "Синяя": "#1f6aa5",
            "Зеленая": "#418b6b",
            "Темно-синяя": "#1a4766",  # Corrected color
        }

        self.ui["theme_optionmenu"].set(
            theme_map.get(self.settings["theme"], "Синяя")
        )
        self.ui["language_optionmenu"].set(self.settings.get("language", "Русский"))
        # Use color_map, not theme_map, for initial application
        self.change_theme(theme_map.get(self.settings["theme"], "Синяя"))

    def change_theme(self, new_theme: str):
        """Handles theme changes (accent color only)."""
        theme_map = {"Синяя": "blue", "Зеленая": "green", "Темно-синяя": "dark-blue"}
        color_map = {"Синяя": "#1f6aa5", "Зеленая": "#418b6b", "Темно-синяя": "#1a4766"}

        theme_value = theme_map.get(new_theme, "blue")
        color_value = color_map.get(new_theme, "#1f6aa5")

        self.settings["theme"] = theme_value
        self._save_settings()

        self.accent_color = color_value
        self._update_accent_colors()

        # Обновляем UI без перезапуска
        self.update_colors()

    def _update_accent_colors(self):
        """Updates the accent color of specific widgets."""
        if self.accent_color:
            for widget_name in [
                "example_button",
                "example_checkbox",
                "example_slider",
                "example_progressbar",
            ]:
                if widget_name in self.ui:
                    self.ui[widget_name].configure(fg_color=self.accent_color)
                    # For widgets that have a progress_color, set that too
                    if hasattr(self.ui[widget_name], "progress_color"):
                        self.ui[widget_name].configure(
                            progress_color=self.accent_color
                        )
                    if hasattr(
                        self.ui[widget_name], "button_color"
                    ):  # checkbox
                        self.ui[widget_name].configure(button_color=self.accent_color)
                    if (
                        hasattr(self.ui[widget_name], "border_color")
                        and widget_name == "example_checkbox"
                    ):  # checkbox
                        self.ui[widget_name].configure(
                            border_color=self.accent_color
                        )

    def update_colors(self):
        """Updates widget colors based on appearance mode."""
        light_color = "gray85"
        dark_color = "gray17"
        current_bg_color = (
            light_color if ctk.get_appearance_mode() == "Light" else dark_color
        )

        for widget in self.settings_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.configure(fg_color=current_bg_color)
                for inner_widget in widget.winfo_children():
                    if isinstance(inner_widget, ctk.CTkFrame):
                        inner_widget.configure(fg_color=current_bg_color)

        self.parent.update_idletasks()
        self.parent.update()  # Принудительно обновляем интерфейс
        self._update_accent_colors()


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Settings Example")
    app.geometry("800x700")
    settings_tab = SettingsTab(app)
    app.mainloop()