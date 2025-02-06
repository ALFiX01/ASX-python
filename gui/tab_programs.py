import os
import tkinter as tk
try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    import sys
    sys.exit(1)
from tkinter import messagebox
import requests
import subprocess
import zipfile

class ProgramsTab:
    def __init__(self, parent):
        self.parent = parent

        self.search_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.search_frame.pack(fill="x", padx=10, pady=(5, 10))

        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Поиск программ...",
            height=35,
            corner_radius=8
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.search_entry.bind("<KeyRelease>", self.search_programs)

        self.programs_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent"
        )
        self.programs_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.setup_programs_list()

    def _find_child_frame_by_type(self, parent_frame, frame_type):
        """Helper function to find a child frame of a specific type."""
        for child in parent_frame.winfo_children():
            if isinstance(child, frame_type):
                return child
        return None # Return None if not found

    def setup_programs_list(self):
        """Setup the list of available programs"""
        programs = [
            ("Chrome", "Веб-браузер от Google", "ChromeSetup.exe", "https://dl.google.com/chrome/install/latest/chrome_installer.exe"),
            ("Discord", "Платформа для общения", "DiscordSetup.exe", "https://discord.com/api/downloads/distributions/app/installers/latest?channel=stable&platform=win&arch=x64"),
            ("Steam", "Игровая платформа", "SteamSetup.exe", "https://cdn.akamai.steamstatic.com/client/installer/SteamSetup.exe"),
            ("KMSAuto", "Активатор Windows (ZIP)", "KMSAuto.zip", "https://github.com/ALFiX01/ASX-Hub/releases/download/File/KMSAuto.zip", True, "KMSAuto Net Portable.exe"), # ZIP example: executable_path is relative to extract_folder
            # Add more programs here
        ]

        for name, description, filename, download_url, *zip_info in programs:
            is_zip_archive = zip_info and zip_info[0] == True
            executable_name_in_zip = zip_info[1] if zip_info and len(zip_info) > 1 else None

            program_frame = ctk.CTkFrame(
                self.programs_frame,
                fg_color=("gray86", "gray17"),
                corner_radius=10,
                border_width=0
            )
            program_frame.pack(fill="x", padx=10, pady=5)
            program_frame.bind("<Enter>", lambda event, frame=program_frame: self.on_program_hover(event, frame))
            program_frame.bind("<Leave>", lambda event, frame=program_frame: self.on_program_leave(event, frame))

            content_frame = ctk.CTkFrame(
                program_frame,
                fg_color="transparent"
            )
            content_frame.pack(fill="x", padx=15, pady=15)

            icon_label = ctk.CTkLabel(
                content_frame,
                text="📦",
                font=("Arial", 30),
                text_color=("gray50", "gray70")
            )
            icon_label.pack(side="left", padx=(0, 15))

            text_frame = ctk.CTkFrame(
                content_frame,
                fg_color="transparent"
            )
            text_frame.pack(side="left", fill="x", expand=True)

            name_label = ctk.CTkLabel(
                text_frame,
                text=name,
                font=("Arial", 15, "bold")
            )
            name_label.pack(anchor="w")

            desc_label = ctk.CTkLabel(
                text_frame,
                text=description,
                font=("Arial", 12),
                text_color=("gray50", "gray60")
            )
            desc_label.pack(anchor="w")

            progressbar = ctk.CTkProgressBar(content_frame)
            progressbar.pack(fill="x", padx=5, pady=5, anchor="s")
            progressbar.set(0)
            progressbar.configure(mode="determinate", height=5)
            progressbar.pack_forget()

            download_button = ctk.CTkButton(
                content_frame,
                text="Загрузить",
                command=lambda url=download_url, prog_name=name, file_name=filename, progress_bar=progressbar, is_zip=is_zip_archive, executable_name=executable_name_in_zip: self.download_program(prog_name, url, file_name, progress_bar, is_zip, executable_name),
                width=100,
                height=32,
                corner_radius=8
            )
            download_button.pack(side="right", padx=5)

    def search_programs(self, event):
        """Фильтрация программ на основе текста поиска"""
        search_text = self.search_entry.get().lower()

        for program_frame in self.programs_frame.winfo_children():
            content_frame = self._find_child_frame_by_type(program_frame, ctk.CTkFrame)  # Ищем content_frame по типу
            if content_frame is None:
                print(f"DEBUG: content_frame not found in {program_frame}, skipping")
                program_frame.pack_forget()
                continue

            text_frame = self._find_child_frame_by_type(content_frame, ctk.CTkFrame)  # Ищем text_frame по типу
            if text_frame is None:
                print(f"DEBUG: text_frame not found in {content_frame}, skipping")
                program_frame.pack_forget()
                continue

            program_name_text = ""
            # Перебираем дочерние виджеты text_frame в поисках ctk.CTkLabel (имени программы)
            for widget in text_frame.winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    program_name_text = widget.cget("text").lower()
                    break

            if search_text in program_name_text:
                program_frame.pack(fill="x", padx=10, pady=5)
            else:
                program_frame.pack_forget()

    def download_program(self, program_name, download_url, filename, progress_bar, is_zip, executable_name):
        """Загрузка программы с прямой ссылки с полоской загрузки и (опционально) распаковкой ZIP и запуском"""
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
            progress_bar.set(0)

            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        progress = downloaded_size / total_size
                        progress_bar.set(progress)
                    else:
                        progress_bar.set(0)
                    progress_bar.update()

            progress_bar.pack_forget()
            self.show_message(f"{program_name} успешно загружен!")

            if is_zip:
                try:
                    os.makedirs(extract_folder, exist_ok=True)
                    with zipfile.ZipFile(filepath, 'r') as zip_ref:
                        zip_ref.extractall(extract_folder)
                    self.show_message(f"{program_name} успешно загружен и распакован в '{extract_folder}'!")
                    if executable_name: # Check if executable_name is provided before launching
                        executable_path = os.path.join(extract_folder, executable_name)
                    else:
                        self.show_message(f"{program_name} ZIP архив распакован в '{extract_folder}'.\nИсполняемый файл для запуска не указан в настройках.")
                except Exception as extract_error:
                    print(f"Error extracting {program_name} ZIP: {extract_error}")
                    self.show_message(f"{program_name} загружен, но не удалось распаковать ZIP архив. Ошибка распаковки: {extract_error}")
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
                except Exception as launch_error:
                    print(f"Error launching {program_name}: {launch_error}")
                    self.show_message(f"{program_name} загружен, но не удалось запустить. Ошибка запуска: {launch_error}")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {program_name} from {download_url}: {e}")
            progress_bar.pack_forget()
            self.show_message(f"Ошибка при загрузке {program_name}: {e}")

    def show_message(self, message):
        """Отображение диалогового окна сообщения"""
        messagebox.showinfo(
            title="Сообщение",
            message=message
        )

    def on_program_hover(self, event, frame):
        """Обработчик наведения мыши на карточку программы"""
        frame.configure(border_width=2, border_color=("#56a6db", "#56a6db"))

    def on_program_leave(self, event, frame):
        """Обработчик ухода мыши с карточки программы"""
        frame.configure(border_width=0, border_color=("gray70", "gray30"))

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Programs Tab Example")
    app.geometry("800x700")

    programs_tab = ProgramsTab(app)

    app.mainloop()