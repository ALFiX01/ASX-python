import os
import json
import tkinter as tk
import subprocess  # Import subprocess to run external commands
import sys
from gui.utils import resource_path

try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    sys.exit(1)
from tkinter import messagebox

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

class GitHubHandler:  # Dummy GitHubHandler for standalone testing
    def __init__(self):
        self.download_folder = "downloads"  # Create a 'downloads' folder in the same directory
        os.makedirs(self.download_folder, exist_ok=True)

    def download_release(self, github_url, filename):
        # Simulate download (create a dummy file)
        print(f"Simulating download from {github_url} to {filename}")
        dummy_file_path = os.path.join(self.download_folder, filename)
        with open(dummy_file_path, "w") as f:
            f.write("Dummy content")
        return dummy_file_path

class UtilitiesTab:
    def __init__(self, parent):
        self.parent = parent
        self.github_handler = GitHubHandler() # Keep it for potential future use or remove if not needed
        self.is_searching = False
        self.tile_width = 200
        self.tile_height = 200  # Увеличена высота фреймов
        self.tile_padx = 15
        self.tile_pady = 15

        # Load settings
        settings = load_settings()

        # Define accent color from settings
        self.accent_color = settings.get("accent_color", "#FF5733")

        # --- Search Frame ---
        self.search_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.search_frame.pack(fill="x", padx=20, pady=(10, 5))

        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Поиск утилит...",
            width=200,
            height=40,
            corner_radius=8,
            border_width=2,
            fg_color=("gray85", "gray17"),
            border_color="gray25",
            font=("Roboto", 14)
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.search_entry.bind("<KeyRelease>", self.filter_utilities)
        self.search_entry.bind("<Return>", self.filter_utilities)
        self.search_entry.bind("<FocusIn>", self.start_search)
        self.search_entry.bind("<FocusOut>", self.end_search)

        # === Utilities List Frame (Scrollable) ===
        self.utilities_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent"
        )
        self.utilities_frame.pack(fill="both", expand=True, padx=20, pady=(5, 10))

        self.utilities = [
            ("File Cleaner", "Анализ мусора и удаление"),
            ("PC monitor", "Просмотр информации о пк"),
            ("Startup Manager", "Управление автозапуском"),
        ]
        self.utility_widgets = {}
        self.create_utility_widgets()
        self.original_utilities = self.utilities.copy()
        self.setup_utilities_list()

        self.parent.bind("<Configure>", self.reflow_utilities)

    def create_utility_widgets(self):
        """Creates all utility widgets as square tiles with improved design."""
        for name, description in self.utilities:
            utility_frame = ctk.CTkFrame(
                self.utilities_frame,
                fg_color=("gray86", "gray17"),
                corner_radius=12,
                border_width=1,
                border_color=("gray70", "gray30"),
                width=self.tile_width,
                height=self.tile_height
            )
            utility_frame.grid_propagate(False)  # Prevent automatic resizing
            utility_frame.grid_columnconfigure(0, weight=1)
            utility_frame.grid_rowconfigure(1, weight=1)

            # Remove hover bindings from the frame
            # utility_frame.bind("<Enter>", lambda e, f=utility_frame: self.on_utility_hover(e, f))
            # utility_frame.bind("<Leave>", lambda e, f=utility_frame: self.on_utility_leave(e, f))

            icon_label = ctk.CTkLabel(
                utility_frame,
                text="🔧",
                font=("Roboto", 36),
                text_color=("gray50", "gray70")
            )
            icon_label.grid(row=0, column=0, padx=10, pady=(15, 0), sticky="n")

            text_frame = ctk.CTkFrame(utility_frame, fg_color="transparent")
            text_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

            name_label = ctk.CTkLabel(
                text_frame,
                text=name,
                font=("Roboto", 14, "bold")
            )
            name_label.pack(anchor="center", pady=(0, 3))

            desc_label = ctk.CTkLabel(
                text_frame,
                text=description,
                font=("Roboto", 12),
                text_color=("gray50", "gray60"),
                wraplength=self.tile_width - 30,
                justify="center"
            )
            desc_label.pack(anchor="n", pady=(0, 10))

            action_button = ctk.CTkButton(
                utility_frame,
                text="Запустить", # Button text is now always "Запустить"
                command=lambda n=name: self.handle_utility(n),
                width=100,
                height=32,
                corner_radius=8,
                fg_color=self.accent_color,
                hover_color="#144870",  # Change to a different color on hover
                font=("Roboto", 12)
            )
            action_button.grid(row=2, column=0, pady=(0, 15), sticky="s")
            # Keep hover effects *only* on the button
            action_button.bind("<Enter>", lambda e, b=action_button: b.configure(fg_color="#144870"))
            action_button.bind("<Leave>", lambda e, b=action_button: b.configure(fg_color=self.accent_color))

            self.utility_widgets[name] = utility_frame

    def setup_utilities_list(self):
        """Displays utilities in a grid layout with consistent tile sizes."""
        for frame in self.utility_widgets.values():
            frame.grid_forget()

        row_num = 0
        col_num = 0
        max_cols = 4
        for name, _ in self.utilities:
            if name in self.utility_widgets:
                self.utility_widgets[name].grid(row=row_num, column=col_num, padx=self.tile_padx, pady=self.tile_pady)
                col_num += 1
                if col_num >= max_cols:
                    col_num = 0
                    row_num += 1

    def reflow_utilities(self, event=None):
        """Reflows the utilities grid layout based on available width."""
        frame_width = self.utilities_frame.winfo_width()
        if frame_width <= 1:
            return

        tile_width_with_padding = self.tile_width + 2 * self.tile_padx
        max_cols = max(1, frame_width // tile_width_with_padding)

        row_num = 0
        col_num = 0

        for name, _ in self.utilities:
            if name in self.utility_widgets:
                self.utility_widgets[name].grid(row=row_num, column=col_num, padx=self.tile_padx, pady=self.tile_pady)
                col_num += 1
                if col_num >= max_cols:
                    col_num = 0
                    row_num += 1

        # Hide any remaining tiles if the number of columns decreased
        for name, frame in self.utility_widgets.items():
            grid_info = frame.grid_info()
            if grid_info and grid_info['row'] >= row_num and grid_info['column'] >= col_num:
                frame.grid_forget()

    def start_search(self, _=None):
        """Indicates that a search is in progress."""
        self.is_searching = True
        self.update_search_entry_border_color()

    def end_search(self, _=None):
        """Indicates the end of a search and updates border color."""
        self.is_searching = False
        self.update_search_entry_border_color()

    def update_search_entry_border_color(self, _=None):
        """Updates the search entry border color."""
        if self.is_searching:
            self.search_entry.configure(border_color=self.accent_color)
        elif ctk.AppearanceModeTracker.get_mode() == 1:  # Dark
            self.search_entry.configure(border_color="gray25")
        else:  # Light
            self.search_entry.configure(border_color="gray70")

    # Removed is_installed, install_utility, update_utility_button as they are not needed anymore

    def handle_utility(self, utility_name):
        """Handles utility execution."""
        self.run_utility(utility_name)

    def run_utility(self, utility_name):
        """Runs the specified utility."""
        utility_module_name = utility_name.lower().replace(" ", "_") # convert space to underscore for file name
        utility_file_path = resource_path(os.path.join("utilities", f"{utility_module_name}.py"))

        if not os.path.exists(utility_file_path):
            self.show_message(f"Утилита '{utility_name}' не найдена в папке 'utilities'.")
            return

        try:
            # Run the Python utility file as a subprocess
            subprocess.Popen([sys.executable, utility_file_path]) # Use sys.executable to ensure correct python interpreter
        except Exception as e:
            self.show_message(f"Ошибка при запуске '{utility_name}': {str(e)}")


    # Remove hover methods for the frame
    # def on_utility_hover(self, event, frame):
    #     frame.configure(border_width=2, border_color=self.accent_color)
    #     frame.configure(fg_color=("gray75", "gray25"))

    # def on_utility_leave(self, event, frame):
    #     frame.configure(border_width=1, border_color=("gray70", "gray30"))
    #     frame.configure(fg_color=("gray86", "gray17"))

    def show_message(self, message):
        messagebox.showinfo(title="Сообщение", message=message)

    def filter_utilities(self, event):
        """Filters the utilities list based on the search term."""
        search_term = self.search_entry.get().lower()
        self.update_search_entry_border_color()

        if not search_term:
            self.utilities = self.original_utilities.copy()
            self.setup_utilities_list()
            return

        self.utilities = [
            (name, desc) for name, desc in self.original_utilities
            if search_term in name.lower() or search_term in desc.lower()
        ]
        self.setup_utilities_list()

    def clear_search(self):
        """Clears the search entry and shows all utilities."""
        self.search_entry.delete(0, tk.END)
        self.utilities = self.original_utilities.copy()
        self.setup_utilities_list()