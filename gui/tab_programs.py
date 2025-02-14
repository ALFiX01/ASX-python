import os
import json
import tkinter as tk
try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    import sys
    sys.exit(1)
from tkinter import messagebox, ttk
import requests
import subprocess
import zipfile
import threading
from PIL import Image, ImageTk
import re

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

class ProgramsTab:
    def __init__(self, parent):
        self.parent = parent
        self.search_cache = {}
        self.search_results = []
        self.compiled_search_term = None
        self.all_program_frames = []
        self.is_searching = False  # Track search state

        # Load settings
        settings = load_settings()

        # Define accent color from settings
        self.accent_color = settings.get("accent_color", "#FF5733")  # Default to a color if not found

        # --- Search Frame ---
        self.search_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.search_frame.pack(fill="x", padx=20, pady=(10, 5))  # Increased padx to 20 for better alignment

        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Поиск программ...",
            width=200,
            height=40,
            corner_radius=8,
            border_width=2,
            fg_color=("gray85", "gray17"),
            border_color="gray25",
            font=("Roboto", 14)  # Added Roboto font
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.search_entry.bind("<KeyRelease>", self.search_programs)
        self.search_entry.bind("<Return>", self.search_programs)
        self.search_entry.bind("<FocusIn>", self.start_search)
        self.search_entry.bind("<FocusOut>", self.end_search)

        # --- Programs Frame ---
        self.programs_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.programs_frame.pack(fill="both", expand=True, padx=20, pady=(5, 10))  # Increased padx to 20 for better alignment

        self.programs = [
            ("Chrome", "Веб-браузер от Google", "ChromeSetup.exe", "https://dl.google.com/chrome/install/latest/chrome_installer.exe", "browser_icon.png"),
            ("Discord", "Платформа для общения", "DiscordSetup.exe", "https://discord.com/api/downloads/distributions/app/installers/latest?channel=stable&platform=win&arch=x64", "communication_icon.png"),
            ("Steam", "Игровая платформа", "SteamSetup.exe", "https://cdn.akamai.steamstatic.com/client/installer/SteamSetup.exe", "gaming_icon.png"),
            ("KMSAuto", "Активатор Windows (ZIP)", "KMSAuto.zip", "https://github.com/ALFiX01/ASX-Hub/releases/download/File/KMSAuto.zip", "utility_icon.png", True, "KMSAuto Net Portable.exe"),
            ("Adobe Photoshop", "Редактор изображений", "PhotoshopSetup.exe", "https://example.com/photoshop", "graphics_icon.png"),
            ("Microsoft Office", "Офисный пакет", "OfficeSetup.exe", "https://example.com/office", "office_icon.png"),
        ]
        self.category_icons = {
            "browser_icon.png": "browser_icon.png",
            "communication_icon.png": "communication_icon.png",
            "gaming_icon.png": "gaming_icon.png",
            "utility_icon.png": "utility_icon.png",
            "graphics_icon.png": "graphics_icon.png",
            "office_icon.png": "office_icon.png",
        }

        # Создаем все элементы заранее
        for program in self.programs:
            frame = self.create_program_frame(program)
            self.all_program_frames.append(frame)
            frame.pack(fill="x", padx=10, pady=5)

    def create_program_frame(self, program):
        name, description, filename, download_url, category_icon_key, *zip_info = program
        is_zip_archive = zip_info and zip_info[0] == True
        executable_name_in_zip = zip_info[1] if zip_info and len(zip_info) > 1 else None
        icon_path = self.category_icons.get(category_icon_key, "default_icon.png")

        program_frame = ctk.CTkFrame(
            self.programs_frame,
            fg_color=("gray86", "gray17"),
            corner_radius=10,  # Унифицировано с UtilitiesTab
            border_width=0,
        )
        program_frame.program_data = program  # Сохраняем данные программы
        program_frame.bind("<Enter>", lambda e, f=program_frame: self.on_program_hover(e, f))  # Hover effect
        program_frame.bind("<Leave>", lambda e, f=program_frame: self.on_program_leave(e, f))  # Hover effect

        content_frame = ctk.CTkFrame(program_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=15)

        try:
            icon = ctk.CTkImage(Image.open(os.path.join("icons", icon_path)), size=(48, 48))
            icon_label = ctk.CTkLabel(content_frame, image=icon, text="")
            icon_label.image = icon
            icon_label.pack(side="left", padx=(0, 10))  # Reduced padx to 10 for better alignment
        except Exception:
            icon_label = ctk.CTkLabel(content_frame, text="📦", font=("Roboto", 24), text_color=("gray50", "gray70"))  # Changed font to Roboto, унифицировано с UtilitiesTab, уменьшен шрифт
            icon_label.pack(side="left", padx=(0, 10))  # Reduced padx to 10 for better alignment

        text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)

        name_label = ctk.CTkLabel(text_frame, text=name, font=("Roboto", 14, "bold"))  # Changed font to Roboto, унифицировано с UtilitiesTab, уменьшен шрифт
        name_label.pack(anchor="w")

        desc_label = ctk.CTkLabel(
            text_frame,
            text=description,
            font=("Roboto", 12),  # Changed font to Roboto
            text_color=("#7E7E7E"),  # Оставил цвет как был, можно унифицировать с UtilitiesTab если нужно
        )
        desc_label.pack(anchor="w")

        style = ttk.Style(content_frame)
        style.theme_use('clam')
        style.configure("Horizontal.TProgressbar", troughcolor='#f0f0f0', background=self.accent_color, thickness=8,
                        troughrelief='flat', relief='flat', lightcolor=self.accent_color, darkcolor=self.accent_color, borderwidth=0)
        progressbar = ttk.Progressbar(content_frame, orient="horizontal", length=200, mode="determinate", style="Horizontal.TProgressbar")
        progressbar.pack(fill="x", padx=5, pady=5, anchor="s")
        progressbar.pack_forget()

        download_button = ctk.CTkButton(
            content_frame,
            text="Загрузить",
            command=lambda url=download_url, prog_name=name, file_name=filename,
                   progress_bar=progressbar, is_zip=is_zip_archive,
                   executable_name=executable_name_in_zip: self.start_download_thread(prog_name, url, file_name, progress_bar, is_zip, executable_name),
            width=100,
            height=32,
            corner_radius=8,
            fg_color=self.accent_color,  # Use the accent color
            hover_color=self.accent_color,  # Same color on hover
            font=("Roboto", 13)  # Added Roboto font to button text
        )
        download_button.pack(side="right", padx=5)
        download_button.bind("<Enter>", lambda e, b=download_button: b.configure(fg_color="#66BB6A"))  # Hover effect
        download_button.bind("<Leave>", lambda e, b=download_button: b.configure(fg_color=self.accent_color))  # Hover effect

        return program_frame

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

    def search_programs(self, event=None):
        """Filters programs with regex and caching, optimized for speed."""
        search_text = self.search_entry.get().lower()
        self.update_search_entry_border_color()

        if not search_text:  # If search is empty, show all programs
            self.compiled_search_term = None  # Clear compiled regex
            self.search_results = self.programs
            self.setup_programs_list(self.programs)
            return

        if search_text in self.search_cache:
            if self.search_cache[search_text] is not None:  # Check for valid cached results
                self.search_results = self.search_cache[search_text]
                self.setup_programs_list(self.search_results)
                return

        try:
            # Compile the regular expression for efficiency. This is the key optimization.
            self.compiled_search_term = re.compile(search_text)
            self.search_results = [
                program for program in self.programs
                if self.compiled_search_term.search(program[0].lower()) or self.compiled_search_term.search(program[1].lower())
            ]
            self.search_cache[search_text] = self.search_results  # Cache results
            self.setup_programs_list(self.search_results)

        except re.error:
            # Handle invalid regex (e.g., unmatched parenthesis)
            self.search_cache[search_text] = None  # Store None on regex error.
            messagebox.showerror("Regex Error", "Invalid regular expression.", font=("Roboto", 12))  # Added font to messagebox
            return

    def setup_programs_list(self, programs_to_display):
        for frame in self.all_program_frames:
            frame.pack_forget()

        displayed_programs = set(programs_to_display)
        for frame in self.all_program_frames:
            if frame.program_data in displayed_programs:
                frame.pack(fill="x", padx=10, pady=5)

    def start_download_thread(self, program_name, download_url, filename, progress_bar, is_zip, executable_name):
        download_thread = threading.Thread(
            target=self.download_program,
            args=(program_name, download_url, filename, progress_bar, is_zip, executable_name),
        )
        download_thread.daemon = True
        download_thread.start()

    def download_program(self, program_name, download_url, filename, progress_bar, is_zip, executable_name):
        os.makedirs("downloads", exist_ok=True)
        filepath = os.path.join("downloads", filename)
        extract_folder = os.path.join("downloads", program_name)
        executable_path = None

        try:
            response = requests.get(download_url, stream=True, allow_redirects=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            progress_bar.pack(fill="x", padx=5, pady=5, anchor="s")
            progress_bar.start()

            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            progress_bar['value'] = progress
                            progress_bar.update_idletasks()

            progress_bar.stop()
            progress_bar.pack_forget()
            self.show_message(f"{program_name} успешно загружен!")

            if is_zip:
                try:
                    os.makedirs(extract_folder, exist_ok=True)
                    with zipfile.ZipFile(filepath, 'r') as zip_ref:
                        zip_ref.extractall(extract_folder)
                    self.show_message(f"{program_name} успешно загружен и распакован в '{extract_folder}'!")

                    if executable_name:
                        executable_path = os.path.join(extract_folder, executable_name)
                    else:
                        self.show_message(f"{program_name} ZIP архив распакован. Исполняемый файл не указан.")

                except zipfile.BadZipFile:
                    self.show_message(f"Ошибка: {filepath} не является ZIP архивом")
                    return
                except Exception as extract_error:
                    print(f"Error extracting {program_name}: {extract_error}")
                    self.show_message(f"Ошибка распаковки {program_name}: {extract_error}")
                    return
            else:
                executable_path = filepath

            if executable_path and os.path.exists(executable_path):
                try:
                    if os.name == 'nt':
                        os.startfile(executable_path)
                    else:
                        subprocess.run([executable_path], check=True)
                    self.show_message(f"{program_name} успешно загружен и запущен!")

                except FileNotFoundError:
                    self.show_message(f"Ошибка: файл {executable_path} не найден.")
                except subprocess.CalledProcessError as e:
                    self.show_message(f"Ошибка при запуске {executable_path}: {e}")
                except OSError as e:
                    self.show_message(f"Ошибка при запуске: {e}")
                except Exception as launch_error:
                    print(f"Error launching {program_name}: {launch_error}")
                    self.show_message(f"Ошибка запуска {program_name}: {launch_error}")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {program_name}: {e}")
            progress_bar.pack_forget()
            self.show_message(f"Ошибка загрузки {program_name}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            progress_bar.pack_forget()
            self.show_message(f"Произошла непредвиденная ошибка: {e}")

    def show_message(self, message):
        messagebox.showinfo(title="Сообщение", message=message, font=("Roboto", 12))  # Added font to messagebox

    def on_program_hover(self, event, frame):
        frame.configure(border_width=2, border_color="#56a6db")
        frame.configure(fg_color=("gray75", "gray25"))

    def on_program_leave(self, event, frame):
        frame.configure(border_width=0)
        frame.configure(fg_color=("gray86", "gray17"))

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Программы")
    app.geometry("1050x800")

    if not os.path.exists("icons"):
        os.makedirs("icons")

    programs_tab = ProgramsTab(app)
    app.mainloop()
