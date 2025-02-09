import os
import tkinter as tk
try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found.  Please install it using: pip install customtkinter")
    import sys
    sys.exit(1)
from tkinter import messagebox

# from utils.github_handler import GitHubHandler  # Assuming you have this -  SEE IMPORTANT NOTE BELOW

# IMPORTANT NOTE:  For testing/running this code directly, replace the above line with:
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
        self.github_handler = GitHubHandler()
        self.is_searching = False # Track search state

        # --- Search Frame ---  (Copied from ProgramsTab and adjusted placeholder)
        self.search_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.search_frame.pack(fill="x", padx=20, pady=(10, 5)) # Increased padx to 20 for better alignment

        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Поиск утилит...", # Adjusted placeholder text
            width=200,
            height=35,
            corner_radius=8,
            border_width=2,
            fg_color=("gray85", "gray17"),
            border_color = "gray25",
            font=("Roboto", 12) # Added Roboto font
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
        self.utilities_frame.pack(fill="both", expand=True, padx=20, pady=10) # Increased padx to 20 for better alignment

        self.utilities = [  # Store utilities as a list of tuples
            ("CPU-Z", "Информация о процессоре и системе"),
            ("HWiNFO", "Мониторинг системы"),
            ("MSI Afterburner", "Разгон видеокарты"),
            ("CCleaner", "Очистка системы"),
            ("CrystalDiskInfo", "Мониторинг состояния жестких дисков"),
            ("MemTest64", "Тестирование оперативной памяти"),
            ("FurMark", "Тестирование видеокарты"),
            ("Rivatuner Statistics Server", "Отображение FPS и системной информации в играх"),
        ]
        # --- Optimization:  Create utility widgets once and hide/show them ---
        self.utility_widgets = {}  # Dictionary to store utility frames
        self.create_utility_widgets()
        self.original_utilities = self.utilities.copy() # Copy of the original list
        self.setup_utilities_list() # Initial display


    def create_utility_widgets(self):
        """Creates all utility widgets initially and stores them."""
        for name, description in self.utilities:
            utility_frame = ctk.CTkFrame(
                self.utilities_frame,
                fg_color=("gray86", "gray17"),  # Lighter background
                corner_radius=10, # Унифицировано с ProgramsTab
                border_width=0,  # No border for cleaner look
            )
            utility_frame.bind("<Enter>", lambda e, f=utility_frame: self.on_utility_hover(e, f)) # Hover effect
            utility_frame.bind("<Leave>", lambda e, f=utility_frame: self.on_utility_leave(e, f)) # Hover effect
            # --- Don't pack here yet ---

            content_frame = ctk.CTkFrame(utility_frame, fg_color="transparent")
            content_frame.pack(fill="x", padx=15, pady=15) # Унифицировано с ProgramsTab

            icon_label = ctk.CTkLabel(
                content_frame,
                text="🔧",  #  Slightly smaller icon
                font=("Roboto", 24),  #  Унифицировано с ProgramsTab, уменьшен шрифт, Changed to Roboto
                text_color=("gray50", "gray70")
            )
            icon_label.pack(side="left", padx=(0, 10)) # Reduced padding, унифицировано с ProgramsTab

            text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True)

            name_label = ctk.CTkLabel(
                text_frame,
                text=name,
                font=("Roboto", 14, "bold")  #  Унифицировано с ProgramsTab, уменьшен шрифт, Changed to Roboto
            )
            name_label.pack(anchor="w")

            desc_label = ctk.CTkLabel(
                text_frame,
                text=description,
                font=("Roboto", 12), # Changed to Roboto
                text_color=("gray50", "gray60") # Оставил цвет как был, можно унифицировать с ProgramsTab если нужно
            )
            desc_label.pack(anchor="w")

            button_text = "Запустить" if self.is_installed(name) else "Установить"
            action_button = ctk.CTkButton(
                content_frame,
                text=button_text,
                command=lambda n=name: self.handle_utility(n),
                width=100,
                height=32,
                corner_radius=8,
                fg_color="#4CAF50", # Унифицировано с ProgramsTab
                hover_color="#66BB6A", # Унифицировано с ProgramsTab
                font=("Roboto", 12) # Added Roboto font to button text
            )
            action_button.pack(side="right", padx=5)
            action_button.bind("<Enter>", lambda e, b=action_button: b.configure(fg_color="#66BB6A")) # Hover effect
            action_button.bind("<Leave>", lambda e, b=action_button: b.configure(fg_color="#4CAF50")) # Hover effect


            # --- Store the frame in the dictionary, keyed by utility name ---
            self.utility_widgets[name] = utility_frame

    def setup_utilities_list(self):
        """Displays the (potentially filtered) utilities."""

        # --- Optimization: Hide all, then show only the relevant ones ---
        for frame in self.utility_widgets.values():
            frame.pack_forget()  # Hide all frames initially

        for name, _ in self.utilities: # Iterate through the current list (filtered or original).
            if name in self.utility_widgets:  # Check needed for safety
                self.utility_widgets[name].pack(fill="x", padx=10, pady=5) # Унифицировано с ProgramsTab

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
            accent_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
            if isinstance(accent_color, tuple):
                accent_color = accent_color[ctk.AppearanceModeTracker.get_mode()]
            self.search_entry.configure(border_color=accent_color)
        elif ctk.AppearanceModeTracker.get_mode() == 1:  # Dark
            self.search_entry.configure(border_color="gray25")
        else:  # Light
            self.search_entry.configure(border_color="gray70")

    def is_installed(self, utility_name):
        return os.path.exists(os.path.join(self.github_handler.download_folder, f"{utility_name.lower()}_setup.exe"))

    def handle_utility(self, utility_name):
        if self.is_installed(utility_name):
            self.launch_utility(utility_name)
        else:
            self.install_utility(utility_name)

    def install_utility(self, utility_name):
        # github_url = f"https://github.com/example/{utility_name.lower()}"  #  REPLACE with your actual repos
        github_url = f"https://github.com/example/{utility_name.lower()}" # Placeholder
        filename = f"{utility_name.lower()}_setup.exe"
        downloaded_file = self.github_handler.download_release(github_url, filename)
        if downloaded_file:
            self.show_message(f"{utility_name} успешно установлена!")
            self.update_utility_button(utility_name)  # You'll need to adapt this
        else:
            self.show_message(f"Ошибка при установке {utility_name}")

    def launch_utility(self, utility_name):
        try:
            file_path = os.path.join(self.github_handler.download_folder, f"{utility_name.lower()}_setup.exe")
            if os.path.exists(file_path):
                if os.name == 'nt':
                    os.startfile(file_path)
                else:
                    self.show_message("Запуск программ доступен только в Windows")
        except Exception as e:
            self.show_message(f"Ошибка при запуске {utility_name}: {str(e)}")


    def update_utility_button(self, utility_name):
        """Updates the button text after installation."""
        if utility_name in self.utility_widgets:
            frame = self.utility_widgets[utility_name]
            content_frame = frame.winfo_children()[0]
            # Find the button (it's the last child of content_frame)
            action_button = content_frame.winfo_children()[-1]
            action_button.configure(text="Запустить")

    def on_utility_hover(self, event, frame):
        frame.configure(border_width=2, border_color="#56a6db")
        frame.configure(fg_color=("gray75", "gray25"))

    def on_utility_leave(self, event, frame):
        frame.configure(border_width=0)
        frame.configure(fg_color=("gray86", "gray17"))


    def show_message(self, message):
        messagebox.showinfo(title="Сообщение", message=message, font=("Roboto", 12)) # Added Roboto font

    def filter_utilities(self, event):
        """Filters the utilities list based on the search term."""
        search_term = self.search_entry.get().lower()
        self.update_search_entry_border_color()

        if not search_term:
            self.utilities = self.original_utilities.copy() # Restore original
            self.setup_utilities_list()
            return

        self.utilities = [
            (name, desc) for name, desc in self.original_utilities  # Filter the original
            if search_term in name.lower() or search_term in desc.lower()
        ]
        self.setup_utilities_list()

    def clear_search(self):
        """Clears the search entry and shows all utilities."""
        self.search_entry.delete(0, tk.END)
        self.utilities = self.original_utilities.copy() # Restore to original
        self.setup_utilities_list()



if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Utilities Tab Example")
    app.geometry("800x700")  #  Adjust as needed
    utilities_tab = UtilitiesTab(app)
    app.mainloop()