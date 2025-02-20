import os
import platform
import tkinter as tk
from tkinter import messagebox
import winreg  # Для работы с реестром Windows

try:
    import customtkinter as ctk
except ImportError:
    print("CustomTkinter не найден, используется стандартный tkinter.")
    ctk = tk

# Для создания ярлыков в папке автозагрузки
try:
    import win32com.client
except ImportError:
    win32com = None


def get_size(bytes, suffix="B"):
    """
    Преобразует байты в удобочитаемый формат (КБ, МБ, ГБ и т.д.)
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def get_cpu_name():
    """Получить имя процессора в зависимости от ОС."""
    os_name = platform.system()
    cpu_name = "Не удалось определить"
    if os_name == "Windows":
        try:
            output = os.popen("wmic cpu get name").read().strip()
            lines = [line.strip() for line in output.split('\n') if line.strip()]
            if len(lines) > 1:
                cpu_name = lines[1]
        except Exception as e:
            print(f"Ошибка WMIC для CPU Name: {e}")
    if cpu_name == "Не удалось определить":
        cpu_name = platform.processor() or cpu_name
    return cpu_name


class StartupManager:
    def __init__(self, master):
        self.master = master
        self.master.title("Управление автозапуском Windows")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        # Шрифты
        self.title_font = ("Segoe UI", 24, "bold")
        self.section_font = ("Segoe UI", 16, "bold")
        self.label_font = ("Segoe UI", 13)

        self.startup_programs = []  # Список всех найденных элементов автозапуска

        self.setup_ui()
        self.load_startup_programs()
        self.display_startup_programs()

    def setup_ui(self):
        # Заголовок
        header = ctk.CTkLabel(
            self.master,
            text="Управление автозапуском Windows",
            font=self.title_font,
            text_color="#2A9DF4",
        )
        header.pack(pady=15)

        # Создаём Tabview с двумя вкладками: "Список автозапуска" и "Добавить элемент"
        self.tabview = ctk.CTkTabview(
            self.master,
            width=1100,
            height=700,
            segmented_button_selected_color="#2A9DF4",
            segmented_button_selected_hover_color="#1C6BA0",
            corner_radius=8,
            bg_color="transparent"
        )
        self.tabview.pack(padx=15, pady=10, fill="both", expand=True)

        # Вкладка "Список автозапуска"
        self.tabview.add("Список автозапуска")
        self.startup_tab = self.tabview.tab("Список автозапуска")

        # Фрейм с фильтрами и массовыми операциями
        self.filter_frame = ctk.CTkFrame(self.startup_tab, fg_color="transparent")
        self.filter_frame.pack(padx=10, pady=(10, 5), fill="x")

        # Поле поиска
        search_label = ctk.CTkLabel(self.filter_frame, text="Поиск:", font=self.label_font, corner_radius=8)
        search_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(self.filter_frame, width=250, textvariable=self.search_var, font=self.label_font)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", lambda event: self.display_startup_programs())

        # Сортировка
        sort_label = ctk.CTkLabel(self.filter_frame, text="Сортировка:", font=self.label_font)
        sort_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.sort_var = tk.StringVar(value="По названию")
        self.sort_option = ctk.CTkOptionMenu(
            self.filter_frame,
            values=["По названию", "По источнику"],
            variable=self.sort_var,
            font=self.label_font,
            width=150,
            command=lambda _: self.display_startup_programs()
        )
        self.sort_option.grid(row=0, column=3, padx=5, pady=5)

        # Кнопки массовых операций
        self.bulk_enable_button = ctk.CTkButton(
            self.filter_frame,
            text="Включить все",
            command=self.bulk_enable_all,
            width=120,
            font=self.label_font,
            fg_color="#5CB85C",
            hover_color="#4CAE4C"
        )
        self.bulk_enable_button.grid(row=0, column=4, padx=10, pady=5)

        self.bulk_disable_button = ctk.CTkButton(
            self.filter_frame,
            text="Отключить все",
            command=self.bulk_disable_all,
            width=120,
            font=self.label_font,
            fg_color="#D9534F",
            hover_color="#C9302C"
        )
        self.bulk_disable_button.grid(row=0, column=5, padx=10, pady=5)

        # Скроллируемый фрейм для списка автозапуска
        self.startup_programs_frame = ctk.CTkScrollableFrame(self.startup_tab, width=1050, height=580, fg_color="transparent")
        self.startup_programs_frame.pack(padx=10, pady=5, fill="both", expand=True)

        # Кнопка обновления списка
        self.refresh_button = ctk.CTkButton(
            self.master,
            text="Обновить список",
            command=self.reload_startup_programs,
            width=220,
            height=40,
            corner_radius=8,
            font=("Segoe UI", 14, "bold"),
            fg_color="#2A9DF4",
            hover_color="#1C6BA0",
            border_color="#FFFFFF",
            border_width=1
        )
        self.refresh_button.pack(pady=10)

        # Вкладка "Добавить элемент"
        self.tabview.add("Добавить элемент")
        self.add_tab = self.tabview.tab("Добавить элемент")
        self.setup_add_tab()

    def setup_add_tab(self):
        add_frame = ctk.CTkFrame(self.add_tab, fg_color="transparent")
        add_frame.pack(padx=20, pady=20, fill="both", expand=True)

        title_label = ctk.CTkLabel(add_frame, text="Добавить новый элемент автозапуска", font=self.section_font)
        title_label.pack(pady=(0, 10))

        # Поле ввода имени
        name_label = ctk.CTkLabel(add_frame, text="Имя:", font=self.label_font)
        name_label.pack(pady=(5, 0))
        self.new_name_entry = ctk.CTkEntry(add_frame, width=400, font=self.label_font)
        self.new_name_entry.pack(pady=(0, 10))

        # Поле ввода команды/пути
        command_label = ctk.CTkLabel(add_frame, text="Команда/Путь:", font=self.label_font)
        command_label.pack(pady=(5, 0))
        self.new_command_entry = ctk.CTkEntry(add_frame, width=400, font=self.label_font)
        self.new_command_entry.pack(pady=(0, 10))

        # Выбор места добавления: Реестр (HKCU) или Папка автозагрузки
        location_label = ctk.CTkLabel(add_frame, text="Место добавления:", font=self.label_font)
        location_label.pack(pady=(5, 0))
        self.location_var = tk.StringVar(value="registry")
        registry_radio = ctk.CTkRadioButton(add_frame, text="Реестр (HKCU)", variable=self.location_var, value="registry", font=self.label_font)
        registry_radio.pack(pady=5)
        folder_radio = ctk.CTkRadioButton(add_frame, text="Папка автозагрузки (Пользователь)", variable=self.location_var, value="folder", font=self.label_font)
        folder_radio.pack(pady=5)

        # Кнопка добавления нового элемента
        add_button = ctk.CTkButton(add_frame, text="Добавить элемент", command=self.add_new_startup, font=self.label_font, fg_color="#2A9DF4", hover_color="#1C6BA0")
        add_button.pack(pady=15)

    def load_startup_programs(self):
        """Загружает элементы автозапуска из реестра и папок."""
        self.startup_programs = []
        registry_keys = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run")
        ]

        for hkey_root, sub_key in registry_keys:
            self.load_from_registry(hkey_root, sub_key)

        # Загрузка из папок автозагрузки (общая и пользовательская)
        common_startup = os.path.join(os.getenv('ALLUSERSPROFILE', ''), r"Microsoft\Windows\Start Menu\Programs\Startup")
        user_startup = os.path.join(os.getenv('APPDATA', ''), r"Microsoft\Windows\Start Menu\Programs\Startup")
        self.load_from_startup_folder(common_startup, "folder_common")
        self.load_from_startup_folder(user_startup, "folder_user")

    def load_from_registry(self, hkey_root, sub_key):
        try:
            key = winreg.OpenKeyEx(hkey_root, sub_key)
            i = 0
            while True:
                try:
                    name, value, type_val = winreg.EnumValue(key, i)
                    if type_val in [winreg.REG_SZ, winreg.REG_EXPAND_SZ]:
                        self.startup_programs.append({
                            "name": name,
                            "command": value,
                            "enabled": True,
                            "hkey_root": hkey_root,
                            "sub_key": sub_key,
                            "source": "Реестр"
                        })
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except FileNotFoundError:
            pass

    def load_from_startup_folder(self, folder_path, folder_type):
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                full_path = os.path.join(folder_path, filename)
                if os.path.isfile(full_path):
                    lower_filename = filename.lower()
                    valid_extensions = ('.exe', '.bat', '.cmd', '.lnk')
                    enabled = True
                    original_filename = filename

                    # Если файл отключён, у него есть суффикс .disabled_startup
                    if lower_filename.endswith(".disabled_startup"):
                        enabled = False
                        # Убираем суффикс для проверки расширения
                        original_filename = filename[:-len(".disabled_startup")]
                        lower_original = original_filename.lower()
                        if not lower_original.endswith(valid_extensions):
                            continue  # Если исходное расширение не подходит, пропускаем файл
                    else:
                        if not lower_filename.endswith(valid_extensions):
                            continue  # Пропускаем, если расширение не подходит

                    display_name = os.path.splitext(original_filename)[0]
                    self.startup_programs.append({
                        "name": f"{display_name} (Папка — {folder_type.split('_')[1].capitalize()})",
                        "command": full_path,
                        "enabled": enabled,
                        "type": folder_type,
                        "filepath": full_path,
                        "source": "Папка"
                    })

    def display_startup_programs(self):
        """Отображает список элементов с учётом фильтра и сортировки."""
        for widget in self.startup_programs_frame.winfo_children():
            widget.destroy()

        query = self.search_var.get().lower()
        filtered_programs = [
            prog for prog in self.startup_programs
            if query in prog["name"].lower() or query in prog["command"].lower()
        ]

        if self.sort_var.get() == "По названию":
            filtered_programs.sort(key=lambda p: p["name"].lower())
        elif self.sort_var.get() == "По источнику":
            filtered_programs.sort(key=lambda p: p.get("source", "").lower())

        if not filtered_programs:
            no_programs_label = ctk.CTkLabel(self.startup_programs_frame, text="Список автозапуска пуст.", font=self.label_font)
            no_programs_label.pack(padx=20, pady=20)
            return

        for program in filtered_programs:
            self.create_program_entry(program)

    def create_program_entry(self, program):
        """Создаёт виджет для отдельного элемента автозапуска."""
        program_frame = ctk.CTkFrame(self.startup_programs_frame, fg_color="transparent", corner_radius=10, border_width=1, border_color="#444")
        program_frame.pack(fill='x', padx=10, pady=5)

        # Чекбокс для включения/отключения
        enabled_var = tk.BooleanVar(value=program["enabled"])
        checkbox = ctk.CTkCheckBox(
            program_frame,
            text="",
            variable=enabled_var,
            command=lambda p=program, var=enabled_var: self.toggle_startup(p, var)
        )
        checkbox.grid(row=0, column=0, padx=16, pady=10)

        # Метка с именем
        program_name_label = ctk.CTkLabel(program_frame, text=program["name"], font=self.label_font, anchor="w", wraplength=500)
        program_name_label.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        # Кнопка "Подробно"
        details_button = ctk.CTkButton(
            program_frame,
            text="Подробно",
            width=100,
            height=30,
            font=self.label_font,
            command=lambda p=program: self.open_details_dialog(p)
        )
        details_button.grid(row=0, column=2, padx=5, pady=10)

        # Кнопка "Редактировать" (разрешено только для записей HKCU и пользовательской папки)
        allow_edit = True
        if program.get("source") == "Реестр" and program.get("hkey_root") != winreg.HKEY_CURRENT_USER:
            allow_edit = False
        elif program.get("source") == "Папка" and program.get("type", "").lower() == "folder_common":
            allow_edit = False

        edit_button = ctk.CTkButton(
            program_frame,
            text="Редактировать",
            width=100,
            height=30,
            font=self.label_font,
            command=lambda p=program: self.edit_startup(p),
            state="normal" if allow_edit else "disabled"
        )
        edit_button.grid(row=0, column=3, padx=5, pady=10)

        # Кнопка "Удалить"
        delete_button = ctk.CTkButton(
            program_frame,
            text="Удалить",
            width=80,
            height=30,
            font=self.label_font,
            fg_color="#D9534F",
            hover_color="#C9302C",
            command=lambda p=program: self.delete_startup(p)
        )
        delete_button.grid(row=0, column=4, padx=5, pady=10)

    def update_startup_state(self, program, state):
        if "type" in program and program["type"] in ["folder_common", "folder_user"]:
            filepath = program["filepath"]
            valid_extensions = ('.exe', '.bat', '.cmd', '.lnk')
            try:
                if state:  # Включение службы
                    if filepath.lower().endswith(".disabled_startup"):
                        original_path = filepath[:-len(".disabled_startup")]
                        # Проверяем, что оригинальный файл имеет допустимое расширение
                        ext = os.path.splitext(original_path)[1].lower()
                        if ext not in valid_extensions:
                            print(f"Некорректное расширение для файла: {original_path}")
                            messagebox.showerror("Ошибка", f"Файл {program['name']} имеет некорректное расширение.")
                            return False
                        # Если оригинальный файл уже существует, удаляем его
                        if os.path.exists(original_path):
                            try:
                                os.remove(original_path)
                            except Exception as ex:
                                print(f"Не удалось удалить {original_path}: {ex}")
                                messagebox.showerror("Ошибка", f"Конфликт: невозможно удалить файл {original_path}.")
                                return False
                        os.rename(filepath, original_path)
                        program["filepath"] = original_path
                        program["command"] = original_path
                else:  # Отключение службы
                    if not filepath.lower().endswith(".disabled_startup"):
                        # Проверяем, что файл имеет допустимое расширение
                        ext = os.path.splitext(filepath)[1].lower()
                        if ext not in valid_extensions:
                            print(f"Некорректное расширение для файла: {filepath}")
                            messagebox.showerror("Ошибка", f"Файл {program['name']} имеет некорректное расширение.")
                            return False
                        new_path = filepath + ".disabled_startup"
                        os.rename(filepath, new_path)
                        program["filepath"] = new_path
                        program["command"] = new_path
            except Exception as e:
                print(f"Ошибка при изменении состояния для {program['name']}: {e}")
                messagebox.showerror("Ошибка", f"Не удалось изменить состояние для {program['name']}.")
                return False
        else:
            # Обработка автозапуска через реестр
            hkey_root = program["hkey_root"]
            sub_key = program["sub_key"]
            name = program["name"]
            command = program["command"]
            try:
                key = winreg.OpenKeyEx(hkey_root, sub_key, 0, winreg.KEY_WRITE)
                if state:
                    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, command)
                else:
                    winreg.DeleteValue(key, name)
                winreg.CloseKey(key)
            except OSError as e:
                print(f"Ошибка реестра при изменении {name}: {e}")
                messagebox.showerror("Ошибка",
                                     f"Не удалось изменить автозапуск для {program['name']}. Требуются права администратора.")
                return False
        program["enabled"] = state
        return True

    def toggle_startup(self, program, enabled_var):
        state = enabled_var.get()
        if not self.update_startup_state(program, state):
            enabled_var.set(not state)

    def bulk_enable_all(self):
        """Массово включает все отфильтрованные элементы."""
        query = self.search_var.get().lower()
        for program in self.startup_programs:
            if query in program["name"].lower() or query in program["command"].lower():
                if not program["enabled"]:
                    self.update_startup_state(program, True)
        self.display_startup_programs()

    def bulk_disable_all(self):
        """Массово отключает все отфильтрованные элементы."""
        query = self.search_var.get().lower()
        for program in self.startup_programs:
            if query in program["name"].lower() or query in program["command"].lower():
                if program["enabled"]:
                    self.update_startup_state(program, False)
        self.display_startup_programs()

    def open_details_dialog(self, program):
        """Открывает окно с подробной информацией об элементе автозапуска."""
        dialog = ctk.CTkToplevel(self.master)
        dialog.title("Подробности элемента автозапуска")
        dialog.geometry("600x300")
        ctk.CTkLabel(dialog, text="Подробная информация", font=self.section_font).pack(pady=10)

        info = f"Имя: {program.get('name')}\n"
        info += f"Команда: {program.get('command')}\n"
        info += f"Источник: {program.get('source')}\n"
        if program.get("source") == "Папка":
            info += f"Путь: {program.get('filepath')}\n"
        details_text = ctk.CTkTextbox(dialog, width=580, height=150, font=self.label_font)
        details_text.insert("0.0", info)
        details_text.configure(state="disabled")
        details_text.pack(padx=10, pady=10)

    def edit_startup(self, program):
        """Открывает окно редактирования для разрешённых элементов автозапуска."""
        # Проверка: редактирование разрешено только для HKCU или пользовательской папки
        if program.get("source") == "Реестр" and program.get("hkey_root") != winreg.HKEY_CURRENT_USER:
            messagebox.showwarning("Ограничение", "Редактирование системных записей не поддерживается.")
            return
        if program.get("source") == "Папка" and program.get("type", "").lower() == "folder_common":
            messagebox.showwarning("Ограничение", "Редактирование элементов из общей папки не поддерживается.")
            return

        edit_win = ctk.CTkToplevel(self.master)
        edit_win.title("Редактирование элемента")
        edit_win.geometry("600x250")

        ctk.CTkLabel(edit_win, text="Редактировать элемент автозапуска", font=self.section_font).pack(pady=10)

        # Поля для изменения имени и команды
        form_frame = ctk.CTkFrame(edit_win, fg_color="transparent")
        form_frame.pack(padx=10, pady=10, fill="both", expand=True)

        ctk.CTkLabel(form_frame, text="Имя:", font=self.label_font).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        name_entry = ctk.CTkEntry(form_frame, width=400, font=self.label_font)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        name_entry.insert(0, program.get("name"))

        ctk.CTkLabel(form_frame, text="Команда/Путь:", font=self.label_font).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        command_entry = ctk.CTkEntry(form_frame, width=400, font=self.label_font)
        command_entry.grid(row=1, column=1, padx=5, pady=5)
        command_entry.insert(0, program.get("command"))

        def save_edits():
            new_name = name_entry.get().strip()
            new_command = command_entry.get().strip()
            if not new_name or not new_command:
                messagebox.showwarning("Предупреждение", "Заполните все поля.")
                return

            # Редактирование для реестра
            if program.get("source") == "Реестр":
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
                    # Если имя изменилось, удаляем старую запись
                    if new_name != program["name"]:
                        try:
                            winreg.DeleteValue(key, program["name"])
                        except Exception:
                            pass
                    winreg.SetValueEx(key, new_name, 0, winreg.REG_SZ, new_command)
                    winreg.CloseKey(key)
                    messagebox.showinfo("Успех", f"{new_name} успешно обновлён в автозапуске (реестр).")
                except Exception as e:
                    print(f"Ошибка редактирования реестровой записи: {e}")
                    messagebox.showerror("Ошибка", f"Не удалось обновить {program['name']}.")
                    return
            # Редактирование для папки автозагрузки
            elif program.get("source") == "Папка":
                startup_folder = os.path.join(os.getenv('APPDATA', ''), r"Microsoft\Windows\Start Menu\Programs\Startup")
                if win32com:
                    try:
                        shell = win32com.client.Dispatch("WScript.Shell")
                        old_shortcut = os.path.join(startup_folder, f"{program['name'].split(' (')[0]}.lnk")
                        new_shortcut = os.path.join(startup_folder, f"{new_name}.lnk")
                        shortcut = shell.CreateShortCut(old_shortcut)
                        shortcut.Targetpath = new_command
                        shortcut.WorkingDirectory = os.path.dirname(new_command)
                        shortcut.IconLocation = new_command
                        shortcut.save()
                        if new_name != program["name"]:
                            os.rename(old_shortcut, new_shortcut)
                        messagebox.showinfo("Успех", f"{new_name} успешно обновлён (ярлык).")
                    except Exception as e:
                        print(f"Ошибка редактирования ярлыка: {e}")
                        messagebox.showerror("Ошибка", f"Не удалось обновить {program['name']}.")
                        return
                else:
                    # Для BAT файла – перезаписываем содержимое и переименовываем, если требуется
                    old_file = os.path.join(startup_folder, f"{program['name'].split(' (')[0]}.bat")
                    new_file = os.path.join(startup_folder, f"{new_name}.bat")
                    try:
                        with open(old_file, "w") as f:
                            f.write(f'start "" "{new_command}"')
                        if new_name != program["name"]:
                            os.rename(old_file, new_file)
                        messagebox.showinfo("Успех", f"{new_name} успешно обновлён (BAT файл).")
                    except Exception as e:
                        print(f"Ошибка редактирования BAT файла: {e}")
                        messagebox.showerror("Ошибка", f"Не удалось обновить {program['name']}.")
                        return

            edit_win.destroy()
            self.reload_startup_programs()

        save_button = ctk.CTkButton(edit_win, text="Сохранить", command=save_edits, font=self.label_font, fg_color="#5CB85C", hover_color="#4CAE4C")
        save_button.pack(pady=10)

    def delete_startup(self, program):
        confirm = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить {program['name']}?")
        if not confirm:
            return

        if program.get("source") == "Реестр":
            try:
                key = winreg.OpenKeyEx(program["hkey_root"], program["sub_key"], 0, winreg.KEY_WRITE)
                winreg.DeleteValue(key, program["name"])
                winreg.CloseKey(key)
            except Exception as e:
                print(f"Ошибка удаления реестровой записи {program['name']}: {e}")
                messagebox.showerror("Ошибка", f"Не удалось удалить {program['name']}.")
                return
        elif program.get("source") == "Папка":
            filepath = program.get("filepath")
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Ошибка удаления файла {filepath}: {e}")
                messagebox.showerror("Ошибка", f"Не удалось удалить {program['name']}.")
                return

        messagebox.showinfo("Удалено", f"{program['name']} удалён.")
        self.reload_startup_programs()

    def reload_startup_programs(self):
        self.load_startup_programs()
        self.display_startup_programs()
        messagebox.showinfo("Обновлено", "Список автозапуска обновлён.")

    def add_new_startup(self):
        name = self.new_name_entry.get().strip()
        command = self.new_command_entry.get().strip()
        location = self.location_var.get()

        if not name or not command:
            messagebox.showwarning("Предупреждение", "Заполните все поля.")
            return

        if location == "registry":
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, command)
                winreg.CloseKey(key)
                messagebox.showinfo("Успех", f"{name} добавлен в автозагрузку (реестр).")
            except Exception as e:
                print(f"Ошибка добавления в реестр: {e}")
                messagebox.showerror("Ошибка", f"Не удалось добавить {name} в автозагрузку (реестр).")
                return

        elif location == "folder":
            startup_folder = os.path.join(os.getenv('APPDATA', ''), r"Microsoft\Windows\Start Menu\Programs\Startup")
            if not os.path.exists(startup_folder):
                messagebox.showerror("Ошибка", "Папка автозагрузки не найдена.")
                return

            if win32com:
                try:
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut_path = os.path.join(startup_folder, f"{name}.lnk")
                    shortcut = shell.CreateShortCut(shortcut_path)
                    shortcut.Targetpath = command
                    shortcut.WorkingDirectory = os.path.dirname(command)
                    shortcut.IconLocation = command
                    shortcut.save()
                    messagebox.showinfo("Успех", f"{name} добавлен в автозагрузку (ярлык).")
                except Exception as e:
                    print(f"Ошибка создания ярлыка: {e}")
                    messagebox.showerror("Ошибка", f"Не удалось создать ярлык для {name}.")
                    return
            else:
                bat_path = os.path.join(startup_folder, f"{name}.bat")
                try:
                    with open(bat_path, "w") as f:
                        f.write(f'start "" "{command}"')
                    messagebox.showinfo("Успех", f"{name} добавлен в автозагрузку (BAT файл).")
                except Exception as e:
                    print(f"Ошибка создания BAT файла: {e}")
                    messagebox.showerror("Ошибка", f"Не удалось создать BAT файл для {name}.")
                    return

        # Очищаем поля ввода и обновляем список
        self.new_name_entry.delete(0, tk.END)
        self.new_command_entry.delete(0, tk.END)
        self.reload_startup_programs()


def run_startup_manager():
    root = ctk.CTk()
    root.geometry("1100x800")
    root.configure(fg_color="#121212")
    root.resizable(False, False)  # Блокируем изменение размера
    StartupManager(root)
    root.mainloop()


if __name__ == "__main__":
    run_startup_manager()
