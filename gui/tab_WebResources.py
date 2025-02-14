import os
import json
import tkinter as tk
try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    import sys
    sys.exit(1)
from tkinter import messagebox
import webbrowser

def load_settings(settings_file="settings.json"):
    """Loads settings from a JSON file."""
    try:
        with open(settings_file, "r") as f:
            settings = json.load(f)
            return settings
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading settings: {e}. Using default settings.")
        return {
            "appearance_mode": "System",
            "theme": "blue",
            "language": "Russian",
            "accent_color": "#1f6aa5"  # Default accent color
        }

class WebResourcesTab:
    def __init__(self, parent):
        self.parent = parent

        # Load settings
        settings = load_settings()

        # Define accent color from settings
        self.accent_color = settings.get("accent_color", "#FF5733")  # Default to a color if not found

        # === Web Resources List Frame (Scrollable) ===
        self.web_resources_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent"  # Transparent background for better integration
        )
        self.web_resources_frame.pack(fill="both", expand=True, padx=20, pady=20)  # More generous padding

        self.setup_web_resources_list()

    def setup_web_resources_list(self):
        """Setup the list of web resources"""
        web_resources = [
            ("Сочетания клавиш Windows", "Поисковая система", "https://alfix-inc.yonote.ru/share/bf2a0a30-f29e-4dc0-a9ef-52b034503497"),
            ("Расширения для браузера", "Видеохостинг", "https://alfix-inc.yonote.ru/share/8e24ecd0-aadb-4a1e-83f4-b66d76710d2c"),
            ("Веб-Сайты", "Платформа для разработчиков", "https://alfix-inc.yonote.ru/share/c09b6731-f1e2-4fe4-a924-f420ecef3972"),
            # Add more web resources here
        ]

        for name, description, url in web_resources:
            # === Web Resource Card (Individual Item) ===
            web_resource_frame = ctk.CTkFrame(
                self.web_resources_frame,
                fg_color=("gray90", "gray15"),  # Lighter background for contrast, subtle difference
                corner_radius=12,             # Slightly more rounded corners
                border_width=1,              # Subtle border
                border_color=("gray80", "gray25") # Light border, consistent with theme
            )
            web_resource_frame.pack(fill="x", padx=10, pady=8)  # Tighter vertical padding, consistent spacing
            web_resource_frame.bind("<Enter>", lambda event, frame=web_resource_frame: self.on_resource_hover(event, frame))
            web_resource_frame.bind("<Leave>", lambda event, frame=web_resource_frame: self.on_resource_leave(event, frame))

            # === Content Frame (Inner layout) ===
            content_frame = ctk.CTkFrame(
                web_resource_frame,
                fg_color="transparent"  # Inherit background from parent
            )
            content_frame.pack(fill="x", padx=16, pady=16)  # Consistent padding

            # === Icon Label ===
            icon_label = ctk.CTkLabel(
                content_frame,
                text="🌐",  # Placeholder icon -  we're keeping this
                font=("Arial", 28),  # Slightly smaller icon
                text_color=("gray60", "gray50")  # Consistent color, slightly darker in light mode
            )
            icon_label.pack(side="left", padx=(0, 16))  # Consistent spacing

            # === Text Frame (For Name and Description) ===
            text_frame = ctk.CTkFrame(
                content_frame,
                fg_color="transparent"
            )
            text_frame.pack(side="left", fill="x", expand=True)

            name_label = ctk.CTkLabel(
                text_frame,
                text=name,
                font=("Segoe UI", 16, "bold"),  # Use a more modern font, slightly larger
                anchor="w",                     # Left-align text
                justify="left"                  # Ensure multi-line text is left-aligned
            )
            name_label.pack(fill="x")  # Fill horizontally

            desc_label = ctk.CTkLabel(
                text_frame,
                text=description,
                font=("Segoe UI", 13),  # Slightly larger description, modern font
                text_color=("gray50", "gray60"),
                anchor="w",
                justify="left",
                wraplength=400  # Add wraplength to prevent very long descriptions from stretching the layout
            )
            desc_label.pack(fill="x")

            # === Open Button ===
            open_button = ctk.CTkButton(
                content_frame,
                text="Открыть",
                command=lambda u=url: self.open_web_resource(u),
                width=100,
                height=32,
                corner_radius=8,
                fg_color=self.accent_color,  # Use the accent color
                hover_color=self.accent_color, # Same color on hover
                font = ("Roboto", 13)
            )
            open_button.pack(side="right", padx=(10, 0))  # Add some left padding

    def open_web_resource(self, url):
        """Open web resource in default browser"""
        webbrowser.open_new_tab(url)

    def show_message(self, message):
        """Show a message dialog"""
        messagebox.showinfo(title="Сообщение", message=message)

    def on_resource_hover(self, event, frame):
        """Handle mouse hover on resource card"""
        frame.configure(border_width=2, border_color=("#4285F4", "#4285F4"))  # More distinct hover color (blue)

    def on_resource_leave(self, event, frame):
        """Handle mouse leaving resource card"""
        frame.configure(border_width=1, border_color=("gray80", "gray25"))  # Back to subtle border

if __name__ == "__main__":
    ctk.set_appearance_mode("system")  # Use system's light/dark mode
    ctk.set_default_color_theme("blue") #A good default theme

    app = ctk.CTk()
    app.title("Web Resources Tab Example")
    app.geometry("1050x800")  # Slightly adjusted size

    web_resources_tab = WebResourcesTab(app)

    app.mainloop()
