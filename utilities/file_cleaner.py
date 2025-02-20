import os
import glob
import shutil
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox, Listbox, MULTIPLE
import time
try:
    import customtkinter as ctk
except ImportError:
    print("CustomTkinter not found, using standard tkinter.")
    ctk = tk

# Импортируем pywinstyles
import pywinstyles

def get_env(var, default=""):
    value = os.environ.get(var)
    return value if value is not None else default

class FileCleaner:
    def __init__(self, master, verbose=False):
        self.master = master
        self.master.title("File Cleaner")
        self.verbose = verbose
        self.found_items = set()
        self.is_scanning = False
        self.total_size_bytes = 0

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        main_frame = ctk.CTkFrame(self.master, fg_color="transparent")
        main_frame.pack(padx=30, pady=20, fill="both", expand=True)

        self.status_label = ctk.CTkLabel(main_frame, text="Начинается сканирование...", font=("Roboto", 14))
        self.status_label.pack(pady=(0, 10))

        self.freed_space_label = ctk.CTkLabel(main_frame, text="", font=("Roboto", 12), text_color="#8F8F8F", width=260)
        self.freed_space_label.pack(pady=(0, 10))

        self.scan_button = ctk.CTkButton(main_frame, text="Найти мусорные файлы", command=self.scan_files, width=200, corner_radius=8,
                                        font=("Roboto", 13))
        self.scan_button.pack(pady=5)

        # Создаем основной фоновый фрейм с обводкой
        self.list_background = ctk.CTkFrame(
            main_frame,
            corner_radius=10,
            border_width=1,
            border_color="#3B3B3B"
        )
        self.list_background.pack(pady=15, padx=15, fill="both", expand=True)

        # Внутренний фрейм для списка (прозрачный)
        list_container = ctk.CTkFrame(self.list_background, fg_color="transparent")
        list_container.pack(fill="both", expand=True, padx=12, pady=12)

        # 1. Создаем Listbox
        self.file_list = Listbox(
            list_container,
            selectmode=MULTIPLE,
            height=10,
            font=("Roboto", 12),
            bg="gray17",
            fg="#E0E0E0",
            borderwidth=0,
            highlightthickness=0,
            selectbackground="#3B8ED0",
            selectforeground="white",
            activestyle="none",
            relief="flat",
            cursor="hand2"
        )

        # 2. Создаем скроллбар и связываем с Listbox
        self.file_list_scrollbar = ctk.CTkScrollbar(
            list_container,
            button_color="#3B8ED0",
            button_hover_color="#2F73A6",
            command=self.file_list.yview  # Теперь file_list уже существует
        )

        # 3. Настраиваем обратную связь для Listbox
        self.file_list.configure(yscrollcommand=self.file_list_scrollbar.set)

        # Размещение элементов
        self.file_list_scrollbar.pack(side="right", fill="y", pady=2)
        self.file_list.pack(side="left", fill="both", expand=True)

        self.file_list.bind("<Double-Button-1>", self.open_selected_item)

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent") # Важно: делаем фон фрейма прозрачным
        button_frame.pack(pady=(15, 0), fill="x")

        self.delete_selected_button = ctk.CTkButton(button_frame, text="Удалить выбранное", command=self.delete_selected_items, state=tk.DISABLED,
                                                    corner_radius=8, width=150, font=("Roboto", 13))
        self.delete_selected_button.grid(row=0, column=0, padx=(0, 10), sticky="ew") # Используем grid

        self.delete_all_button = ctk.CTkButton(button_frame, text="Удалить все", command=self.delete_all_items, state=tk.DISABLED,
                                                 corner_radius=8, width=150, font=("Roboto", 13))
        self.delete_all_button.grid(row=0, column=1, padx=10, sticky="ew") # Используем grid

        self.cancel_scan_button = ctk.CTkButton(button_frame, text="Отменить", command=self.cancel_scan, state=tk.DISABLED,
                                                  corner_radius=8, width=120, font=("Roboto", 13))
        self.cancel_scan_button.grid(row=0, column=2, padx=(10, 0), sticky="ew") # Используем grid

        button_frame.columnconfigure(0, weight=1) # Равномерное распределение места
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)


        self.blacklist_paths = [
            os.path.join(get_env("windir", "C:\\Windows"), "System32"),
            os.path.join(get_env("windir", "C:\\Windows"), "SysWOW64"),
            os.path.join(get_env("ProgramFiles", "C:\\Program Files")),
            os.path.join(get_env("ProgramFiles(x86)", "C:\\Program Files (x86)")),
            os.path.join(get_env("SystemDrive", "C:") + "\\System Volume Information"),
            os.path.join(get_env("SystemDrive", "C:") + "\\Recovery"),
            os.path.join(get_env("LocalAppData"), "ProgramData"),
            os.path.join(get_env("SystemDrive", "C:") + "\\$Recycle.Bin"),
            "C:\\bootmgr",
            "C:\\BOOTNXT",
            "C:\\hiberfil.sys",
            "C:\\pagefile.sys",
            "C:\\swapfile.sys"
        ]
        self.blacklist_files = [
            "bootmgr",
            "BOOTNXT",
            "hiberfil",
            "pagefile",
            "swapfile"
        ]
        self.blacklist_extensions = [".dll", ".exe", ".sys", ".msi", ".drv", ".mun", ".mui", ".lnk"]

        self.master.after(100, self.start_automatic_scan)

    def start_automatic_scan(self):
        self.scan_files()
        self.scan_button.configure(state=tk.NORMAL)

    def is_blacklisted(self, path):
        path = path.lower()
        if os.path.basename(path).split('.')[0].lower() in self.blacklist_files:
            if self.verbose:
                print(f"Файл '{path}' по имени находится в черном списке файлов.")
            return True
        for blacklisted_path in self.blacklist_paths:
            if blacklisted_path.lower() in path:
                if self.verbose:
                    print(f"Путь '{path}' находится в черном списке: '{blacklisted_path}'")
                return True
        for ext in self.blacklist_extensions:
            if path.lower().endswith(ext):
                if self.verbose:
                    print(f"Расширение '{ext}' для пути '{path}' находится в черном списке расширений.")
                return True
        return False

    def safe_delete_directory(self, path, retries=3, delay=0.5):
        if self.is_blacklisted(path):
            if self.verbose:
                print(f"Пропущено удаление папки '{path}' из-за черного списка.")
            return False, 0

        deleted_files_count = 0
        folder_deleted = False
        is_temp_cache_folder = any(folder_name.lower() in path.lower() for folder_name in ["temp", "cache", "временные"])

        if is_temp_cache_folder and os.path.isdir(path):
            if self.verbose:
                print(f"Очистка содержимого папки Temp/Cache: '{path}'")
            try:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if not self.is_blacklisted(item_path):
                        try:
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                                deleted_files_count += 1
                                if self.verbose:
                                    print(f"Удалён файл (содержимое Temp/Cache) {item_path}")
                            elif os.path.isdir(item_path):
                                folder_deleted_inner, files_deleted_inner = self.safe_delete_directory(item_path, retries, delay)
                                deleted_files_count += files_deleted_inner
                        except Exception as e:
                            if self.verbose:
                                print(f"Ошибка при удалении элемента (содержимое Temp/Cache) {item_path}: {e}")
                    else:
                        if self.verbose:
                            print(f"Пропущен элемент (содержимое Temp/Cache) '{item_path}' из-за черного списка.")
                return True, deleted_files_count
            except Exception as top_e_temp_cache:
                if self.verbose:
                    print(f"Общая ошибка при очистке содержимого Temp/Cache папки '{path}': {top_e_temp_cache}")
                return False, deleted_files_count


        files_deleted_in_attempt = 0
        dirs_deleted_in_attempt = 0
        files_failed_in_attempt = 0
        dirs_failed_in_attempt = 0

        for attempt in range(retries):
            if self.verbose and attempt > 0:
                print(f"Повторная попытка {attempt+1}/{retries} удаления содержимого папки: {path}")

            for root, dirs, files in os.walk(path, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    if not self.is_blacklisted(file_path):
                        try:
                            os.remove(file_path)
                            files_deleted_in_attempt += 1
                            if self.verbose:
                                print(f"Удалён файл {file_path}")
                        except Exception as ex:
                            files_failed_in_attempt += 1
                            if self.verbose:
                                print(f"Ошибка при удалении файла {file_path}: {ex}")
                    else:
                        if self.verbose:
                            print(f"Пропущен файл '{file_path}' из-за черного списка.")
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    if not self.is_blacklisted(dir_path):
                        try:
                            os.rmdir(dir_path)
                            dirs_deleted_in_attempt += 1
                            if self.verbose:
                                print(f"Удалена папка {dir_path}")
                        except Exception as ex:
                            dirs_failed_in_attempt += 1
                            if self.verbose:
                                print(f"Ошибка при удалении папки {dir_path}: {ex}")
                    else:
                        if self.verbose:
                            print(f"Пропущена папка '{dir_path}' из-за черного списка.")
            if files_failed_in_attempt == 0 and dirs_failed_in_attempt == 0:
                break

            if attempt < retries - 1 and (files_failed_in_attempt > 0 or dirs_failed_in_attempt > 0):
                time.sleep(delay)
                if self.verbose:
                    print(f"Ожидание {delay} секунд перед следующей попыткой удаления содержимого папки {path}...")


        deleted_files_count += files_deleted_in_attempt

        if not is_temp_cache_folder:
            try:
                os.rmdir(path)
                if self.verbose:
                    print(f"Папка {path} удалена после очистки содержимого.")
                folder_deleted = True
                return folder_deleted, deleted_files_count + 1
            except Exception as ex:
                if self.verbose:
                    print(f"Не удалось удалить папку {path} после очистки содержимого: {ex}")
                folder_deleted = False
        else:
            folder_deleted = True

        return folder_deleted, deleted_files_count

    def get_folder_size(self, folder_path):
        total_size = 0
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                except OSError:
                    if self.verbose:
                        print(f"Невозможно получить размер файла: {file_path}")
                    pass
        return total_size


    def scan_files(self):
        self.status_label.configure(text="Сканирование...")
        self.freed_space_label.configure(text="")
        self.file_list.delete(0, tk.END)
        self.found_items.clear()
        self.total_size_bytes = 0
        self.delete_selected_button.configure(state=tk.DISABLED)
        self.delete_all_button.configure(state=tk.DISABLED)
        self.scan_button.configure(state=tk.DISABLED)
        self.cancel_scan_button.configure(state=tk.NORMAL)
        self.is_scanning = True

        env = {
            "windir": get_env("windir", "C:\\Windows"),
            "systemdrive": get_env("SystemDrive", "C:"),
            "TEMP": get_env("TEMP"),
            "AppData": get_env("AppData"),
            "LocalAppData": get_env("LocalAppData"),
            "ProgramFiles(x86)": get_env("ProgramFiles(x86)"),
            "localappdata": get_env("localappdata"),
            "ProgramData": get_env("ProgramData"),
            "HomePath": get_env("HomePath")
        }

        file_patterns = [
            os.path.join(env["windir"], "Temp", "*"),
            os.path.join(env["LocalAppData"], "Temp", "*"),
            os.path.join(env["AppData"], "Temp", "*"),
            os.path.join(env["TEMP"], "*"),
            os.path.join(env["LocalAppData"], "Microsoft", "Windows", "Explorer", "thumbcache_*.db"),
            os.path.join(env["LocalAppData"], "Microsoft", "Windows", "Explorer", "*.db"),
            os.path.join(env["LocalAppData"], "Mozilla", "Firefox", "Crash Reports", "pending", "*"),
            os.path.join(env["LocalAppData"], "Google", "Chrome", "User Data", "Crashpad", "reports", "*"),
            os.path.join(env["systemdrive"], "*.tmp"),
            os.path.join(env["systemdrive"], "*._mp"),
            os.path.join(env["systemdrive"], "*.log"),
            os.path.join(env["systemdrive"], "*.old"),
            os.path.join(env["windir"], "*.bak"),
            os.path.join(env["windir"], "Logs", "*.log"),
            os.path.join(env["windir"], "Prefetch", "*.pf"),
            os.path.join(env["AppData"], "Microsoft", "Windows", "Recent", "*"),
            os.path.join(env["LocalAppData"], "Microsoft", "Windows", "INetCache", "*"),
            os.path.join(env["AppData"], "Local", "Microsoft", "Windows", "INetCookies", "*"),
            os.path.join(env["LocalAppData"], "Discord", "Cache", "*"),
            os.path.join(env["LocalAppData"], "Discord", "Code Cache", "*"),
        ]

        folder_paths = [
            os.path.join(env["windir"], "Temp"),
            os.path.join(env["windir"], "Prefetch"),
            env["TEMP"],
            os.path.join(env["AppData"], "Temp"),
            os.path.join(env["LocalAppData"], "Temp"),
            os.path.join(env["systemdrive"], "windows.old"),
            os.path.join(env["systemdrive"], "OneDriveTemp"),
            os.path.join(env["ProgramData"], "Microsoft", "Diagnosis"),
            os.path.join(env["ProgramData"], "Microsoft", "Network"),
            os.path.join(env["ProgramData"], "Microsoft", "Search"),
            os.path.join(env["LocalAppData"], "Microsoft", "Windows", "AppCache"),
            os.path.join(env["LocalAppData"], "Microsoft", "Windows", "History"),
            os.path.join(env["LocalAppData"], "Microsoft", "Windows", "WebCache")
        ]

        if self.verbose:
            print("Начало сканирования мусорных файлов...")
            print("Файловые шаблоны:")
            for pattern in file_patterns:
                print("  ", pattern)
            print("Папки для очистки содержимого:")
            for folder in folder_paths:
                print("  ", folder)
            print("Черный список путей:")
            for blacklisted_path in self.blacklist_paths:
                print("  ", blacklisted_path)
            print("Черный список расширений:")
            for ext in self.blacklist_extensions:
                print("  ", ext)
            print("Черный список файлов (по имени):")
            for file_name in self.blacklist_files:
                print("  ", file_name)

        found_count = 0
        update_interval = 100

        for pattern in file_patterns:
            if not self.is_scanning:
                break
            try:
                for path in glob.glob(pattern, recursive=True):
                    if os.path.isfile(path) or os.path.isdir(path):
                        if not self.is_blacklisted(path):
                            self.found_items.add(path)
                            if os.path.isfile(path):
                                try:
                                    self.total_size_bytes += os.path.getsize(path)
                                except OSError:
                                    if self.verbose:
                                        print(f"Невозможно получить размер файла: {path}")
                                    pass
                            elif os.path.isdir(path):
                                self.total_size_bytes += self.get_folder_size(path)
                            found_count += 1
                            if found_count % update_interval == 0:
                                self.master.update()
                        else:
                            if self.verbose:
                                print(f"Пропущен '{path}' из-за черного списка.")
            except Exception as e:
                if self.verbose:
                    print(f"Ошибка при сканировании по шаблону {pattern}: {e}")
            self.master.update()


        for folder in folder_paths:
            if not self.is_scanning:
                break
            if folder and os.path.exists(folder) and not self.is_blacklisted(folder):
                if folder not in self.found_items:
                    self.found_items.add(folder)
                    self.total_size_bytes += self.get_folder_size(folder)
                    found_count += 1
                    if found_count % update_interval == 0:
                        self.master.update()
            else:
                if self.verbose and folder and self.is_blacklisted(folder):
                    print(f"Пропущена папка '{folder}' из списка папок для очистки содержимого из-за черного списка.")
            self.master.update()

        self.is_scanning = False
        self.cancel_scan_button.configure(state=tk.DISABLED)
        self.scan_button.configure(state=tk.NORMAL)
        self.display_found_items()

        total_size_mb = self.total_size_bytes / (1024 * 1024)
        self.freed_space_label.configure(text=f"Можно освободить: ~{total_size_mb:.2f} МБ")
        self.status_label.configure(text=f"Сканирование завершено. Найдено {len(self.found_items)} объектов.")


    def cancel_scan(self):
        self.is_scanning = False
        self.status_label.configure(text="Сканирование отменено.")

    def display_found_items(self):
        self.file_list.delete(0, tk.END)
        found_items_list = list(self.found_items)
        for item in found_items_list:
            self.file_list.insert(tk.END, item)
        if found_items_list:
            self.delete_selected_button.configure(state=tk.NORMAL)
            self.delete_all_button.configure(state=tk.NORMAL)
        else:
            self.status_label.configure(text="Мусор не найден.")
            self.freed_space_label.configure(text="")

    def delete_selected_items(self):
        selected_indices = self.file_list.curselection()
        if not selected_indices:
            messagebox.showinfo("Выберите объекты", "Выберите файлы для удаления.")
            return

        items_to_delete = [self.file_list.get(index) for index in selected_indices]
        if messagebox.askyesno("Подтверждение", f"Удалить {len(items_to_delete)} объектов?"):
            deleted_count = 0
            errors_count = 0
            updated_items_set = set(self.found_items)
            deleted_size_bytes = 0

            for item_path in items_to_delete:
                if item_path in updated_items_set:
                    try:
                        if os.path.isfile(item_path):
                            file_size = os.path.getsize(item_path)
                            os.remove(item_path)
                            deleted_count += 1
                            deleted_size_bytes += file_size

                        elif os.path.isdir(item_path):
                            folder_deleted, files_in_folder_deleted = self.safe_delete_directory(item_path)
                            if folder_deleted:
                                deleted_count += files_in_folder_deleted
                                deleted_size_bytes += self.get_folder_size(item_path)
                            else:
                                raise Exception(f"Не удалось удалить папку {item_path} или ее содержимое")

                        if self.verbose:
                            print(f"Удалено: {item_path}")
                        updated_items_set.remove(item_path)
                    except Exception as e:
                        errors_count += 1
                        if self.verbose:
                            print(f"Ошибка при удалении {item_path}: {e}")

            self.found_items = updated_items_set
            self.display_found_items()
            deleted_size_mb = deleted_size_bytes / (1024 * 1024)
            msg = f"Удалено {deleted_count} объектов. Освобождено {deleted_size_mb:.2f} MB."
            if errors_count:
                msg += f" Ошибок: {errors_count}."
            self.status_label.configure(text=msg)
            if not self.found_items:
                self.delete_selected_button.configure(state=tk.DISABLED)
                self.delete_all_button.configure(state=tk.DISABLED)
                self.freed_space_label.configure(text="")

    def delete_all_items(self):
        if not self.found_items:
            messagebox.showinfo("Нет объектов", "Нет мусора для удаления.")
            return

        if messagebox.askyesno("Подтверждение", f"Удалить ВСЕ {len(self.found_items)} объектов?"):
            deleted_count = 0
            errors_count = 0
            items_to_delete = list(self.found_items)
            updated_items_set = set(self.found_items)
            deleted_size_bytes = 0

            for item_path in items_to_delete:
                if item_path in updated_items_set:
                    try:
                        if os.path.isfile(item_path):
                            file_size = os.path.getsize(item_path)
                            os.remove(item_path)
                            deleted_count += 1
                            deleted_size_bytes += file_size
                        elif os.path.isdir(item_path):
                            folder_deleted, files_in_folder_deleted = self.safe_delete_directory(item_path)
                            if folder_deleted:
                                deleted_count += files_in_folder_deleted
                                deleted_size_bytes += self.get_folder_size(item_path)
                            else:
                                raise Exception(f"Не удалось удалить папку {item_path} или ее содержимое")

                        if self.verbose:
                            print(f"Удалено: {item_path}")
                        updated_items_set.remove(item_path)
                    except Exception as e:
                        errors_count += 1
                        if self.verbose:
                            print(f"Ошибка при удалении {item_path}: {e}")

            self.found_items = updated_items_set
            self.display_found_items()
            deleted_size_mb = deleted_size_bytes / (1024 * 1024)
            msg = f"Удалено {deleted_count} объектов. Освобождено {deleted_size_mb:.2f} MB."
            if errors_count:
                msg += f" Ошибок: {errors_count}."
            self.status_label.configure(text=msg)
            if not self.found_items:
                self.delete_selected_button.configure(state=tk.DISABLED)
                self.delete_all_button.configure(state=tk.DISABLED)
                self.freed_space_label.configure(text="")


    def clear_recycle_bin(self):
        try:
            subprocess.run(["powershell", "-Command", "Clear-RecycleBin -Confirm:$false"], check=True)
            if self.verbose:
                print("Корзина очищена.")
        except Exception as e:
            if self.verbose:
                print(f"Ошибка при очистке корзины: {e}")

    def open_selected_item(self, event):
        selection = self.file_list.curselection()
        if selection:
            index = selection[0]
            item_path = self.file_list.get(index)
            if platform.system() == "Windows":
                try:
                    os.startfile(item_path)
                except OSError as e:
                    messagebox.showerror("Ошибка открытия", f"Не удалось открыть '{item_path}'. Ошибка: {e}")
            elif platform.system() == "Linux":
                try:
                    subprocess.Popen(['xdg-open', item_path])
                except OSError as e:
                    messagebox.showerror("Ошибка открытия", f"Не удалось открыть '{item_path}'. Ошибка: {e}")
            elif platform.system() == "Darwin": # macOS
                try:
                    subprocess.Popen(['open', item_path])
                except OSError as e:
                    messagebox.showerror("Ошибка открытия", f"Не удалось открыть '{item_path}'. Ошибка: {e}")
            else:
                messagebox.showerror("Неподдерживаемая система", "Открытие файлов через проводник не поддерживается в вашей операционной системе.")

def run():
    root = ctk.CTk()
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")
    root.geometry("800x820")
    root.resizable(False, False)  # Блокируем изменение размера
    FileCleaner(root, verbose=True)
    root.mainloop()

if __name__ == "__main__":
    run()