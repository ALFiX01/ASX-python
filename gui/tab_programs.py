import os
import json
import tkinter as tk
from tkinter import messagebox, ttk
import requests
import subprocess
import zipfile
import threading
import re
import winreg
import sys
from PIL import Image, ImageTk

try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found.  Please install it using: pip install customtkinter")
    sys.exit(1)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_settings(settings_file="settings.json"):
    try:
        with open(resource_path(settings_file), "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading settings: {e}.  Using default settings.")
        return {
            "appearance_mode": "System",
            "theme": "blue",
            "language": "Russian",
            "accent_color": "#1f6aa5"
        }


def is_program_installed(program_name):
    """Checks if a program is installed (using Windows Registry)."""
    try:
        for key in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            for arch in [winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY, 0]:
                try:
                    uninstall_key = winreg.OpenKey(key, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0,
                                                   winreg.KEY_READ | arch)
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(uninstall_key, i)
                            subkey = winreg.OpenKey(uninstall_key, subkey_name)
                            try:
                                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                if program_name.lower() in display_name.lower():
                                    return True
                            except OSError:
                                pass
                            finally:
                                winreg.CloseKey(subkey)
                            i += 1
                        except OSError:
                            break
                    winreg.CloseKey(uninstall_key)
                except OSError:
                    pass
    except Exception:
        return False
    return False


def get_program_version_registry(program_name):
    """Attempts to get the installed program's version from the Windows Registry."""
    try:
        for key in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            for arch in [winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY, 0]:
                try:
                    uninstall_key = winreg.OpenKey(key, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0,
                                                   winreg.KEY_READ | arch)
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(uninstall_key, i)
                            subkey = winreg.OpenKey(uninstall_key, subkey_name)
                            try:
                                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                if program_name.lower() in display_name.lower():
                                    try:
                                        version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                        return version
                                    except OSError:
                                        return None
                            except OSError:
                                pass
                            finally:
                                winreg.CloseKey(subkey)
                            i += 1
                        except OSError:
                            break
                    winreg.CloseKey(uninstall_key)
                except OSError:
                    pass
    except Exception:
        return None
    return None


def check_program_by_path(program_path):
    """Checks if a program is installed by checking for its executable path."""
    return os.path.exists(program_path)


def check_program_by_command(command):
    """Checks if a program is installed by trying to run a command."""
    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_installed_programs():
    """Retrieves a list of installed programs from the Windows Registry."""
    installed_programs = []
    try:
        for key in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            for arch in [winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY, 0]:
                try:
                    uninstall_key = winreg.OpenKey(key, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0,
                                                   winreg.KEY_READ | arch)
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(uninstall_key, i)
                            subkey = winreg.OpenKey(uninstall_key, subkey_name)
                            try:
                                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                version = winreg.QueryValueEx(subkey, "DisplayVersion")[0] if winreg.QueryValueEx(subkey, "DisplayVersion") else "N/A"
                                installed_programs.append((display_name, version))
                            except OSError:
                                pass
                            finally:
                                winreg.CloseKey(subkey)
                            i += 1
                        except OSError:
                            break
                    winreg.CloseKey(uninstall_key)
                except OSError:
                    pass
    except Exception as e:
        print(f"Error getting installed programs: {e}")
    return installed_programs

class Program:
    def __init__(self, name, description, filename, download_url, category_icon_key,
                 is_zip=False, executable_name_in_zip=None, silent_install_args=None, install_check_name=None,
                 install_check_path=None, install_check_command=None):
        self.name = name
        self.description = description
        self.filename = filename
        self.download_url = download_url
        self.category_icon_key = category_icon_key
        self.is_zip = is_zip
        self.executable_name_in_zip = executable_name_in_zip
        self.silent_install_args = silent_install_args or []
        self.install_check_name = install_check_name or name
        self.install_check_path = install_check_path
        self.install_check_command = install_check_command
        self.is_installed_cache = None
        self.install_check_thread = None
        self.version = None

    def is_installed(self):
        if self.is_installed_cache is None:
            if self.install_check_path:
                self.is_installed_cache = check_program_by_path(self.install_check_path)
            elif self.install_check_command:
                self.is_installed_cache = check_program_by_command(self.install_check_command)
            else:
                self.is_installed_cache = is_program_installed(self.install_check_name)

            if self.is_installed_cache:
                self.version = get_program_version_registry(self.install_check_name)

        return self.is_installed_cache

    def start_install_check(self, callback):
        if self.install_check_thread and self.install_check_thread.is_alive():
            return
        self.install_check_thread = threading.Thread(target=self._check_install_and_update, args=(callback,))
        self.install_check_thread.daemon = True
        self.install_check_thread.start()

    def _check_install_and_update(self, callback):
        is_installed = self.is_installed()
        callback(self, is_installed)


class ProgramsTab:
    def __init__(self, parent):
        self.parent = parent
        self.search_cache = {}
        self.search_results = []
        self.compiled_search_term = None
        self.all_program_frames = []
        self.is_searching = False
        self.programs = []
        self.load_programs()
        self.description_color = "#7E7E7E"  # Store the description color

        settings = load_settings()
        self.accent_color = settings.get("accent_color", "#FF5733")

        self.search_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.search_frame.pack(fill="x", padx=20, pady=(10, 5))

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Поиск программ...", width=200,
                                        height=40, corner_radius=8, border_width=2, fg_color=("gray85", "gray17"),
                                        border_color="gray25", font=("Roboto", 14))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.search_entry.bind("<KeyRelease>", self.search_programs)
        self.search_entry.bind("<Return>", self.search_programs)
        self.search_entry.bind("<FocusIn>", self.start_search)
        self.search_entry.bind("<FocusOut>", self.end_search)

        self.programs_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.programs_frame.pack(fill="both", expand=True, padx=20, pady=(5, 10))

        self.category_icons = {
            "browser_icon.png": resource_path("icons/browser_icon.png"),
            "communication_icon.png": resource_path("icons/communication_icon.png"),
            "gaming_icon.png": resource_path("icons/gaming_icon.png"),
            "utility_icon.png": resource_path("icons/utility_icon.png"),
            "graphics_icon.png": resource_path("icons/graphics_icon.png"),
            "office_icon.png": resource_path("icons/office_icon.png"),
        }
        self.create_program_frames()

    def load_programs(self):
        try:
            with open(resource_path("programs.json"), "r", encoding="utf-8") as f:
                program_data = json.load(f)
                for p_data in program_data:
                    program = Program(**p_data)
                    self.programs.append(program)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Failed to load programs.json: {e}")
            sys.exit(1)

    def create_program_frames(self):
        for program in self.programs:
            frame = self.create_program_frame(program)
            self.all_program_frames.append(frame)
            frame.pack(fill="x", padx=10, pady=5)

    def create_program_frame(self, program):
        program_frame = ctk.CTkFrame(self.programs_frame, fg_color=("gray86", "gray17"), corner_radius=10,
                                     border_width=0)
        program_frame.program_data = program
        # Remove the hover bindings here
        # program_frame.bind("<Enter>", lambda e, f=program_frame: self.on_program_hover(e, f))
        # program_frame.bind("<Leave>", lambda e, f=program_frame: self.on_program_leave(e, f))

        content_frame = ctk.CTkFrame(program_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=15)

        icon_path = self.category_icons.get(program.category_icon_key, "default_icon.png")
        try:
            icon = ctk.CTkImage(Image.open(resource_path(os.path.join("icons", icon_path))), size=(48, 48))
            icon_label = ctk.CTkLabel(content_frame, image=icon, text="")
            icon_label.image = icon
            icon_label.pack(side="left", padx=(0, 10))
        except Exception:
            icon_label = ctk.CTkLabel(content_frame, text="📦", font=("Roboto", 24), text_color=("gray50", "gray70"))
            icon_label.pack(side="left", padx=(0, 10))

        text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)
        name_label = ctk.CTkLabel(text_frame, text=program.name, font=("Roboto", 14, "bold"))
        name_label.pack(anchor="w")

        self.version_label = ctk.CTkLabel(text_frame, text="", font=("Roboto", 12), text_color=self.description_color)
        self.version_label.pack(anchor="w")

        desc_label = ctk.CTkLabel(text_frame, text=program.description, font=("Roboto", 12), text_color=self.description_color)
        desc_label.pack(anchor="w")

        style = ttk.Style(content_frame)
        style.theme_use('clam')
        style.configure("Horizontal.TProgressbar", troughcolor='#f0f0f0', background=self.accent_color, thickness=8,
                        troughrelief='flat', relief='flat', lightcolor=self.accent_color,
                        darkcolor=self.accent_color, borderwidth=0)
        progressbar = ttk.Progressbar(content_frame, orient="horizontal", length=200, mode="determinate",
                                      style="Horizontal.TProgressbar")
        progressbar.pack(fill="x", padx=5, pady=5, anchor="s")
        progressbar.pack_forget()

        self.download_button = ctk.CTkButton(content_frame, text="Загрузить", width=100, height=32, corner_radius=8,
                                        fg_color=self.accent_color, hover_color="#144870", font=("Roboto", 13))
        self.download_button.pack(side="right", padx=5)


        program_frame.download_button = self.download_button
        program_frame.progressbar = progressbar

        program.start_install_check(lambda prog, installed: self.update_button_state(prog, program_frame))

        self.update_button_state(program, program_frame)  # Initial state

        return program_frame
    def update_button_state(self, program, program_frame):

        if program.is_installed():
            self.version_label.configure(text=f"v{program.version}" if program.version else "Установлено")
            self.download_button.configure(text="Установлено", state="disabled", fg_color="#545454",
                                           hover_color="#c9c9c9", command=None)
            self.download_button.configure(width=100, height=32)  # Keep size consistent

            # --- Disable hover effects ---
            self.download_button.unbind("<Enter>")  # Remove hover binding
            self.download_button.unbind("<Leave>")
        else:
            self.version_label.configure(text="")
            self.download_button.configure(
                text="Загрузить",
                state="normal",
                fg_color=self.accent_color,
                hover_color="#144870",
                command=lambda: self.start_download_thread(program, program_frame.progressbar)
            )
            self.download_button.configure(width=100, height=32) # Keep size consistent

            # --- Re-enable hover effects for "Загрузить" button ---
            self.download_button.bind("<Enter>", lambda e, b=self.download_button: b.configure(fg_color="#144870"))
            self.download_button.bind("<Leave>", lambda e, b=self.download_button: b.configure(fg_color=self.accent_color))

    def start_download_thread(self, program, progress_bar):
        download_thread = threading.Thread(target=self.download_program, args=(program, progress_bar))
        download_thread.daemon = True
        download_thread.start()

    def download_program(self, program, progress_bar):
        """Downloads and installs the program."""
        os.makedirs("downloads", exist_ok=True)
        filepath = os.path.join("downloads", program.filename)
        extract_folder = os.path.join("downloads", program.name)
        executable_path = None

        try:
            response = requests.get(program.download_url, stream=True, allow_redirects=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            self.parent.after(0,
                              lambda: progress_bar.pack(fill="x", padx=5, pady=5, anchor="s"))
            self.parent.after(0, progress_bar.start)

            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            self.parent.after(0,
                                              lambda p=progress: progress_bar.configure(
                                                  value=p))

            self.parent.after(0, progress_bar.stop)
            self.parent.after(0, progress_bar.pack_forget)
            self.parent.after(0, lambda: self.show_message(f"{program.name} успешно загружен!"))

            if program.is_zip:
                try:
                    os.makedirs(extract_folder, exist_ok=True)
                    with zipfile.ZipFile(filepath, 'r') as zip_ref:
                        zip_ref.extractall(extract_folder)
                    self.parent.after(0, lambda: self.show_message(f"{program.name} успешно загружен и распакован!"))
                    if program.executable_name_in_zip:
                        executable_path = os.path.join(extract_folder, program.executable_name_in_zip)

                except zipfile.BadZipFile:
                    self.parent.after(0, lambda: self.show_message(f"Ошибка: {filepath} не является ZIP архивом"))
                    return
                except Exception as extract_error:
                    self.parent.after(0, lambda: self.show_message(f"Ошибка распаковки: {extract_error}"))
                    return
            else:
                executable_path = filepath

            if executable_path and os.path.exists(executable_path):
                try:
                    if program.silent_install_args:
                        process = subprocess.Popen([executable_path] + program.silent_install_args,
                                                   shell=os.name == 'nt')
                        process.wait()
                        if process.returncode == 0:
                            self.parent.after(0, lambda: self.show_message(f"{program.name} успешно установлен!"))
                            program.is_installed_cache = True
                            program.version = get_program_version_registry(program.install_check_name)
                            for frame in self.all_program_frames:
                                if frame.program_data == program:
                                    self.parent.after(0, lambda f=frame: self.update_button_state(program, f))
                        else:
                            self.parent.after(0, lambda: self.show_message(
                                f"Ошибка установки {program.name}: Код {process.returncode}"))


                    else:
                        if os.name == 'nt':
                            os.startfile(executable_path)
                        else:
                            subprocess.run([executable_path], check=True)
                        self.parent.after(0, lambda: self.show_message(f"{program.name} успешно загружен и запущен!"))
                except (FileNotFoundError, subprocess.CalledProcessError, OSError) as e:
                    self.parent.after(0, lambda: self.show_message(f"Ошибка запуска/установки: {e}"))

        except requests.exceptions.RequestException as e:
            self.parent.after(0, lambda: progress_bar.pack_forget())
            self.parent.after(0, lambda: self.show_message(f"Ошибка загрузки: {e}"))
        except Exception as e:
            self.parent.after(0, lambda: progress_bar.pack_forget())
            self.parent.after(0, lambda: self.show_message(f"Произошла непредвиденная ошибка: {e}"))


    def show_message(self, message):
        messagebox.showinfo(title="Сообщение", message=message)

    # Remove hover methods
    # def on_program_hover(self, event, frame):
    #     frame.configure(border_width=2, border_color="#56a6db", fg_color=("gray75", "gray25"))

    # def on_program_leave(self, event, frame):
    #     frame.configure(border_width=0, fg_color=("gray86", "gray17"))

    def start_search(self, _=None):
        self.is_searching = True
        self.update_search_entry_border_color()

    def end_search(self, _=None):
        self.is_searching = False
        self.update_search_entry_border_color()

    def update_search_entry_border_color(self, _=None):
        if self.is_searching:
            self.search_entry.configure(border_color=self.accent_color)
        elif ctk.AppearanceModeTracker.get_mode() == 1:
            self.search_entry.configure(border_color="gray25")
        else:
            self.search_entry.configure(border_color="gray70")

    def search_programs(self, event=None):
        search_text = self.search_entry.get().lower()
        self.update_search_entry_border_color()

        if not search_text:
            self.compiled_search_term = None
            self.search_results = self.programs
            self.setup_programs_list(self.programs)
            return

        if search_text in self.search_cache:
            if self.search_cache[search_text] is not None:
                self.search_results = self.search_cache[search_text]
                self.setup_programs_list(self.search_results)
                return

        try:
            self.compiled_search_term = re.compile(search_text)
            self.search_results = [
                program for program in self.programs
                if self.compiled_search_term.search(program.name.lower()) or self.compiled_search_term.search(
                    program.description.lower())
            ]
            self.search_cache[search_text] = self.search_results
            self.setup_programs_list(self.search_results)
        except re.error:
            self.search_cache[search_text] = None
            messagebox.showerror("Regex Error", "Invalid regular expression.", font=("Roboto", 12))
            return

    def setup_programs_list(self, programs_to_display):
        for frame in self.all_program_frames:
            frame.pack_forget()

        displayed_programs_set = set(programs_to_display)
        for frame in self.all_program_frames:
            if frame.program_data in displayed_programs_set:
                frame.pack(fill="x", padx=10, pady=5)


class InstalledProgramsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill="both", expand=True)

        self.installed_programs_list = ctk.CTkTextbox(self, state="disabled", font=("Roboto", 14), wrap="none")
        self.installed_programs_list.pack(fill="both", expand=True, padx=20, pady=20)
        self.refresh_button = ctk.CTkButton(self, text="Обновить список", command=self.display_installed_programs)
        self.refresh_button.pack(pady=10)

        self.display_installed_programs()


    def display_installed_programs(self):
        installed_programs = get_installed_programs()
        self.installed_programs_list.configure(state="normal")
        self.installed_programs_list.delete("1.0", "end")

        for name, version in installed_programs:
                self.installed_programs_list.insert("end", f"{name} (Версия: {version})\n")
        self.installed_programs_list.configure(state="disabled")



class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Программы")
        self.geometry("1050x800")

        if not os.path.exists("icons"):
            os.makedirs("icons")

        self.notebook = ctk.CTkTabview(self)
        self.notebook.pack(fill="both", expand=True)

        self.programs_tab = ProgramsTab(self.notebook.add("Установка программ"))
        self.installed_tab = InstalledProgramsTab(self.notebook.add("Установленные программы"))



if __name__ == "__main__":
    app = App()
    app.mainloop()