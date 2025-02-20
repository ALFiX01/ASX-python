import json
import sys

try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Install it: pip install customtkinter")
    sys.exit(1)

class DynamicStatusLabel(ctk.CTkLabel):
    """A label that displays messages for a limited time."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.after_id = None

    def update_text(self, text, message_type="info", duration=3000):
        """Update the label text and schedule its clearing."""
        self.configure(text=text)
        self._set_text_color(message_type)

        if self.after_id:
            self.after_cancel(self.after_id)
        self.after_id = self.after(duration, self.clear_text)

    def clear_text(self):
        """Clear the label text."""
        self.configure(text="")
        self.after_id = None

    def _set_text_color(self, message_type):
        """Set text color based on message type."""
        if message_type == "info":
            self.configure(text_color="white")
        elif message_type == "success":
            self.configure(text_color="green")
        elif message_type == "warning":
            self.configure(text_color="yellow")
        elif message_type == "error":
            self.configure(text_color="red")
        else:  # Default
            self.configure(text_color="white")

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
        self.patch_notes_visible = False  # Track visibility of patch notes

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
                "accent_color": "#1f6aa5"  # Default accent color
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
        self._create_update_card()

    def _create_update_card(self):
        """Creates the update check card."""
        card = self._create_card("Обновления")

        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.pack(fill="x", pady=5)

        self.check_update_button = ctk.CTkButton(
            button_frame,
            text="Проверить обновления",
            command=self.check_for_updates,
            font=("Roboto", 13)
        )
        self.check_update_button.pack(side="left", pady=5)

        self.update_button = ctk.CTkButton(
            button_frame,
            text="Обновить",
            command=self.update_app,
            state="disabled",
            font=("Roboto", 13)
        )
        self.update_button.pack(side="left", padx=(10, 0), pady=5)

        # Patch notes frame - initially hidden
        self.patch_notes_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.patch_notes_frame.pack(fill="x", pady=(10, 5), padx=5)
        self.patch_notes_frame.pack_forget()  # Initially hidden

        self.patch_notes_text = ctk.CTkTextbox(
            self.patch_notes_frame,
            height=140,
            font=("Roboto", 12),
            wrap="word",
            state="disabled"
        )
        self.patch_notes_text.pack(fill="x", expand=True)

    def check_for_updates(self):
        """Check for available updates."""
        try:
            import requests
            from config import APP_VERSION  # Assuming you have APP_VERSION

            self.parent.winfo_toplevel().dynamic_status.update_text(f"Проверяю наличие обновлений...", message_type="info", duration=2000)

            version_response = requests.get(
                "https://raw.githubusercontent.com/ALFiX01/ASX-python/refs/heads/main/ActualVersion.txt", timeout=5)  # Added timeout
            version_response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            latest_version = version_response.text.strip()

            if latest_version > APP_VERSION:
                # Get patch notes
                try:
                    patch_response = requests.get(
                        "https://raw.githubusercontent.com/ALFiX01/ASX-python/refs/heads/main/PatchNotes.txt", timeout=5)  # Added timeout
                    patch_response.raise_for_status()
                    patch_notes = patch_response.text.strip()

                    # Show patch notes
                    self.patch_notes_text.configure(state="normal")
                    self.patch_notes_text.delete("1.0", "end")
                    self.patch_notes_text.insert("1.0", f"Версия {latest_version}\n\n{patch_notes}")
                    self.patch_notes_text.configure(state="disabled")
                    if not self.patch_notes_visible:
                        self.patch_notes_frame.pack(fill="x", pady=(10, 5), padx=5)  # Show the frame
                        self.patch_notes_visible = True

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching patch notes: {e}")
                    self.show_error_message("Ошибка загрузки примечаний к патчу.")

                self.parent.winfo_toplevel().dynamic_status.update_text(
                    f"Доступна новая версия: {latest_version}",
                    message_type="info",
                    duration=5000
                )
                self.update_button.configure(state="normal")
            else:
                if self.patch_notes_visible:
                    self.patch_notes_frame.pack_forget()  # Hide
                    self.patch_notes_visible = False

                self.parent.winfo_toplevel().dynamic_status.update_text(
                    "У вас установлена актуальная версия",
                    message_type="success",
                    duration=3000
                )
                self.update_button.configure(state="disabled")

        except requests.exceptions.RequestException as e:
            print(f"Error checking for updates: {e}")
            self.parent.winfo_toplevel().dynamic_status.update_text(
                "Ошибка проверки обновлений",
                message_type="error",
                duration=3000
            )
            if self.patch_notes_visible:  # Hide if visible
                self.patch_notes_frame.pack_forget()
                self.patch_notes_visible = False

    def show_error_message(self, message):
        """Displays an error message using the dynamic status label."""
        self.parent.winfo_toplevel().dynamic_status.update_text(
            message,
            message_type="error",
            duration=3000
        )

    def update_app(self):
        """Update the application."""
        # Here you would implement the actual update logic
        self.parent.winfo_toplevel().dynamic_status.update_text(
            "Функция обновления в разработке",
            message_type="warning",
            duration=3000
        )

    def _create_appearance_card(self):
        """Creates the appearance settings card."""
        card = self._create_card("Внешний вид")

        self.ui["theme_label"] = self._create_label(card, "Тема приложения:", font=("Montserrat", 13))
        self.ui["theme_optionmenu"] = self._create_option_menu(
            card, ["Синяя", "Зеленая", "Темно-синяя"], self.change_theme, state="disabled", font=("Roboto", 13),
            text_color=("#f0f0f0")
        )

        self.ui["theme_restart_label"] = self._create_label(
            card,
            "*Для смены темы нужен перезапуск приложения",
            text_color=("#7E7E7E")  # Correct format for light/dark theme
        )

    def _create_language_card(self):
        """Creates the language settings card."""
        card = self._create_card("Язык (Разработка)")

        self.ui["language_label"] = self._create_label(card, "Язык приложения:",
                                                       font=("Montserrat", 13))  # Changed Font
        self.ui["language_optionmenu"] = self._create_option_menu(
            card, ["Русский", "English (Soon)"], None, state="disabled", font=("Roboto", 13),
            text_color=("#f0f0f0")
        )

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

    def _create_label(self, parent, text, text_color=None, font=("Roboto", 13)):  # Added font
        """Helper function to create a label."""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=font,  # Using provided font
            text_color=text_color  # Pass text color
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

        self.ui["theme_optionmenu"].set(
            theme_map.get(self.settings["theme"], "Синяя")
        )
        self.ui["language_optionmenu"].set(self.settings.get("language", "Русский"))
        # Use accent_color for initial application
        self.change_theme(theme_map.get(self.settings["theme"], "Синяя"), display_message=False) # Pass display_message=False

    def change_theme(self, new_theme: str, display_message=True): # Added display_message parameter
        """Handles theme changes and updates the accent color in settings."""
        try:
            theme_map = {"Синяя": "blue", "Зеленая": "green", "Темно-синяя": "dark-blue"}
            accent_colors = {
                "blue": "#1f6aa5",
                "green": "#418b6b",
                "dark-blue": "#1a4766"
            }

            theme_value = theme_map.get(new_theme, "blue")
            color_value = accent_colors.get(theme_value, "#1f6aa5")

            self.settings["theme"] = theme_value
            self.settings["accent_color"] = color_value  # Save accent color
            self._save_settings()

            # Получаем главное окно
            root = self.parent.winfo_toplevel()

            # Обновляем статус-бар, если он есть и display_message is True
            if display_message and hasattr(root, "dynamic_status"): # Conditional message display
                root.dynamic_status.update_text(f"Тема изменена на {new_theme}. Перезапустите ASX Hub для применения темы", message_type="info", duration=2500)

            # Меняем цвет акцента и обновляем интерфейс
            self.accent_color = color_value
            self.update_colors()

        except Exception as e:
            error_message = f"Ошибка при смене темы: {e}"

            # Если есть статус-бар, выводим сообщение в него, иначе в консоль
            if hasattr(root, "dynamic_status"):
                root.dynamic_status.update_text(error_message, message_type="error", duration=4000)
            else:
                print(error_message)

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
        self.parent.update()  # Force UI update

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Settings Example")
    app.geometry("1050x800")

    # Add the dynamic status label to the main app window
    dynamic_status = DynamicStatusLabel(app, text="")
    dynamic_status.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
    app.dynamic_status = dynamic_status  # Store a reference

    settings_tab = SettingsTab(app)
    app.mainloop()