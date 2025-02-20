import os
import platform
import psutil
import tkinter as tk
from datetime import datetime
import cpuinfo
import threading # Импорт модуля threading

try:
    import customtkinter as ctk
except ImportError:
    print("CustomTkinter не найден, используется стандартный tkinter.")
    ctk = tk

try:
    import cpuinfo
except ImportError:
    print("Библиотека cpuinfo не установлена. Информация о CPU будет ограничена.")
    cpuinfo = None

try:
    import GPUtil
except ImportError:
    print("Библиотека GPUtil не установлена. Информация о GPU недоступна.")
    GPUtil = None


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
    """Get CPU name using different methods based on OS."""
    os_name = platform.system()
    cpu_name = "Не удалось определить"

    if os_name == "Windows":
        try:
            # Execute WMIC command to get CPU name - moved to init for optimization if needed
            output = os.popen("wmic cpu get name").read().strip()
            # Split lines and extract the correct line
            lines = [line.strip() for line in output.split('\n') if line.strip()]
            if len(lines) > 1:
                cpu_name = lines[1]
        except Exception as e:
            print(f"Ошибка WMIC для CPU Name: {e}")

    # Fallback to platform.processor() if still not found
    if cpu_name == "Не удалось определить":
        cpu_name = platform.processor() or cpu_name

    return cpu_name


class PCInfoViewer:
    def __init__(self, master):
        # ... (остальная часть __init__ остается без изменений до self.update_info())
        self.master = master
        self.master.title("Информация о ПК")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        # Настройка шрифтов
        self.title_font = ("Segoe UI", 24, "bold")
        self.section_font = ("Segoe UI", 12, "bold")
        self.label_font = ("Segoe UI", 12)

        header = ctk.CTkLabel(master,
                            text="PC Monitoring Dashboard",
                            font=self.title_font,
                            text_color="#2A9DF4")  # Новый цвет заголовка
        header.pack(pady=15)

        # Создаем Tabview для разделения информации по категориям
        self.tabview = ctk.CTkTabview(master,
                                    width=1150,
                                    height=750,
                                    segmented_button_selected_color="#2A9DF4",
                                    segmented_button_selected_hover_color="#1C6BA0",
                                    corner_radius=8)
        self.tabview.pack(padx=15, pady=10, fill="both", expand=True)

        # Стили для прогресс-баров
        self.progress_style = {
            "height": 18,
            "width": 300,
            "progress_color": "#2A9DF4",
            "border_color": "#1A1A1A",
            "corner_radius": 4
        }

        # Список вкладок (секции) без вкладки "Температуры"
        sections = [
            "Система", "CPU", "Память", "Swap", "Диски", "Сеть", "GPU",
            "Батарея", "Пользователи"
        ]
        self.tabs = {}
        self.row_counter = {}
        for sec in sections:
            self.tabview.add(sec)
            self.tabs[sec] = self.tabview.tab(sec)
            self.row_counter[sec] = 0

        # Словарь для хранения виджетов-меток: ключ – кортеж (секция, название)
        self.info_labels = {}

        # --- Static System Info (Fetched once in init) ---
        uname = platform.uname()
        self.static_system_info = {
            "os_name": uname.system,
            "computer_name": uname.node,
            "architecture": uname.machine,
            "os_release": uname.release
        }
        if self.static_system_info["os_name"] == "Windows":
            win_ver = platform.win32_ver()
            self.static_system_info["os_release"] = f"Windows {win_ver[0]}"
        self.static_system_info["processor_name"] = get_cpu_name()

        # --- Static CPU Info (Fetched once in init if cpuinfo is available) ---
        self.static_cpu_info = {
            "brand": "N/A",
            "bits": "N/A"
        }
        if cpuinfo:
            info = cpuinfo.get_cpu_info()
            self.static_cpu_info["brand"] = info.get('brand_raw', 'N/A')
            self.static_cpu_info["bits"] = str(info.get('bits', 'N/A'))


        # --- Заполнение вкладок информацией ---
        # Система
        self.add_info_label("Система", "ОС", self.static_system_info["os_release"])
        self.add_info_label("Система", "Имя компьютера", self.static_system_info["computer_name"])
        self.add_info_label("Система", "Архитектура", self.static_system_info["architecture"])
        self.add_info_label("Система", "Загрузка системы", "...") # Dynamic
        self.add_info_label("Система", "Время включения пк", "...") # Dynamic
        self.add_info_label("Система", "Процессор", self.static_system_info["processor_name"])

        # CPU (добавлены данные из cpuinfo)
        self.add_info_label("CPU", "Физические ядра", "...") # Dynamic, but mostly static
        self.add_info_label("CPU", "Логические ядра", "...") # Dynamic, but mostly static
        self.add_info_label("CPU", "Макс. частота", "...") # Dynamic
        self.add_info_label("CPU", "Текущая частота", "...") # Dynamic
        self.add_info_label("CPU", "Загрузка ядер CPU", "...") # Dynamic
        self.add_info_label("CPU", "Общая загрузка CPU", "...") # Dynamic
        self.add_info_label("CPU", "Бренд процессора", self.static_cpu_info["brand"])
        self.add_info_label("CPU", "Разрядность", self.static_cpu_info["bits"])
        # Прогресс-бар для общей загрузки CPU
        self.cpu_progress_bar = ctk.CTkProgressBar(self.tabs["CPU"], **self.progress_style)
        self.cpu_progress_bar.grid(row=self.row_counter["CPU"], column=1, padx=10, pady=5, sticky="w")
        self.row_counter["CPU"] += 1

        # Память
        self.add_info_label("Память", "Общая память", "...") # Dynamic
        self.add_info_label("Память", "Доступно памяти", "...") # Dynamic
        self.add_info_label("Память", "Используется памяти", "...") # Dynamic
        self.add_info_label("Память", "Загрузка памяти", "...") # Dynamic
        # Прогресс-бар для загрузки памяти
        self.memory_progress_bar = ctk.CTkProgressBar(self.tabs["Память"], **self.progress_style)
        self.memory_progress_bar.grid(row=self.row_counter["Память"], column=1, padx=10, pady=5, sticky="w")
        self.row_counter["Память"] += 1

        # Swap
        self.add_info_label("Swap", "Общий размер Swap", "...") # Dynamic
        self.add_info_label("Swap", "Свободно Swap", "...") # Dynamic
        self.add_info_label("Swap", "Используется Swap", "...") # Dynamic
        self.add_info_label("Swap", "Загрузка Swap", "...") # Dynamic

        # Диски
        self.disk_labels = {}
        partitions = psutil.disk_partitions()
        for i, partition in enumerate(partitions):
            base_label = f"Диск {i+1} ({partition.device})"
            self.add_info_label("Диски", f"{base_label} - Точка монтирования", "...") # Dynamic, but mostly static
            self.add_info_label("Диски", f"{base_label} - Общий размер", "...") # Dynamic
            self.add_info_label("Диски", f"{base_label} - Используется", "...") # Dynamic
            self.add_info_label("Диски", f"{base_label} - Свободно", "...") # Dynamic
            self.add_info_label("Диски", f"{base_label} - Использование", "...") # Dynamic
            self.disk_labels[partition.device] = base_label
        # Статистика дисковой I/O
        self.add_info_label("Диски", "Диск I/O - Прочитано", "...") # Dynamic
        self.add_info_label("Диски", "Диск I/O - Записано", "...") # Dynamic

        # Сеть
        self.network_labels = {}
        if_addrs = psutil.net_if_addrs()
        for interface_name in if_addrs:
            base_label = f"Интерфейс {interface_name}"
            self.add_info_label("Сеть", f"{base_label} - IP-адрес", "...") # Dynamic
            self.add_info_label("Сеть", f"{base_label} - MAC-адрес", "...") # Dynamic, but mostly static
            self.add_info_label("Сеть", f"{base_label} - Передано", "...") # Dynamic
            self.add_info_label("Сеть", f"{base_label} - Получено", "...") # Dynamic
            self.network_labels[interface_name] = base_label

        # GPU
        if GPUtil:
            self.gpu_labels = {}
            try:
                gpus = GPUtil.getGPUs()
                if not gpus:
                    self.add_info_label("GPU", "GPU", "GPU не обнаружены или информация недоступна.")
                else:
                    for i, gpu in enumerate(gpus):
                        base_label = f"GPU {i+1} ({gpu.name})"
                        self.add_info_label("GPU", f"{base_label} - Загрузка", "...") # Dynamic
                        self.add_info_label("GPU", f"{base_label} - Используемая память", "...") # Dynamic
                        self.add_info_label("GPU", f"{base_label} - Общая память", "...") # Dynamic
                        self.add_info_label("GPU", f"{base_label} - Температура", "...") # Dynamic
                        self.gpu_labels[gpu.name] = base_label
            except Exception as e:
                self.add_info_label("GPU", "GPU", f"Ошибка получения информации о GPU: {e}")
        else:
            self.add_info_label("GPU", "GPU", "GPUtil не установлен.")

        # Батарея
        self.battery_labels = {}
        battery = psutil.sensors_battery()
        if battery:
            self.add_info_label("Батарея", "Наличие батареи", "...") # Dynamic, but mostly static
            self.add_info_label("Батарея", "Заряд батареи", "...") # Dynamic
            self.add_info_label("Батарея", "Время работы от батареи", "...") # Dynamic
            self.add_info_label("Батарея", "Состояние зарядки", "...") # Dynamic
        else:
            self.add_info_label("Батарея", "Батарея", "Батарея не найдена или информация недоступна.")

        # Пользователи – динамический список
        self.users_frame = ctk.CTkScrollableFrame(self.tabs["Пользователи"], width=1020, height=650, fg_color="transparent")
        self.users_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Кнопка обновления информации
        self.refresh_button = ctk.CTkButton(
            master,
            text="ОБНОВИТЬ ДАННЫЕ",
            command=self.update_info,
            width=220,
            height=40,
            corner_radius=8,
            font=("Segoe UI", 14, "bold"),
            fg_color="#2A9DF4",
            hover_color="#1C6BA0",
            border_color="#FFFFFF",
            border_width=1
        )
        self.refresh_button.pack(pady=15)

        self.update_info() # Первоначальное обновление данных


    def add_info_label(self, section, label_text, value_placeholder):
        tab = self.tabs[section]
        row = self.row_counter[section]
        label = ctk.CTkLabel(tab,
                           text=f"{label_text}:",
                           font=self.section_font,
                           text_color="#CCCCCC",  # Цвет текста метки
                           anchor="w")
        value_label = ctk.CTkLabel(tab,
                                 text=value_placeholder,
                                 font=self.label_font,
                                 text_color="#FFFFFF",  # Цвет значения
                                 wraplength=650,
                                 justify="left",
                                 anchor="w")
        label.grid(row=row, column=0, padx=(15, 5), pady=7, sticky="w")
        value_label.grid(row=row, column=1, padx=(5, 15), pady=7, sticky="w")
        self.info_labels[(section, label_text)] = value_label
        self.row_counter[section] += 1


    def update_label(self, section, label_text, value):
        """
        Обновляет текст метки, если такая существует.
        """
        key = (section, label_text)
        if key in self.info_labels:
            self.info_labels[key].configure(text=value if value else "N/A")

    def update_info(self):
        # Запускаем обновление каждой секции в отдельном потоке
        threads = [
            threading.Thread(target=self.update_system_info_thread),
            threading.Thread(target=self.update_cpu_info_thread),
            threading.Thread(target=self.update_memory_info_thread),
            threading.Thread(target=self.update_swap_info_thread),
            threading.Thread(target=self.update_disk_info_thread),
            threading.Thread(target=self.update_network_info_thread),
            threading.Thread(target=self.update_gpu_info_thread),
            threading.Thread(target=self.update_battery_info_thread),
            threading.Thread(target=self.update_users_info_thread)
        ]
        for thread in threads:
            thread.start()


    def update_system_info_thread(self):
        system_load = psutil.cpu_percent()
        boot_time_timestamp = psutil.boot_time()
        boot_time = datetime.fromtimestamp(boot_time_timestamp).strftime("%Y-%m-%d %H:%M:%S")
        self.master.after(0, self.update_system_info_ui, system_load, boot_time)

    def update_system_info_ui(self, system_load, boot_time):
        self.update_label("Система", "Загрузка системы", f"{system_load}%")
        self.update_label("Система", "Время включения пк", boot_time)


    def update_cpu_info_thread(self):
        try:
            cpu_freq = psutil.cpu_freq()
            max_freq = f"{cpu_freq.max:.2f} МГц" if cpu_freq else "N/A"
            current_freq = f"{cpu_freq.current:.2f} МГц" if cpu_freq else "N/A"
        except Exception:
            max_freq, current_freq = "Недоступно", "Недоступно"

        core_usage = psutil.cpu_percent(percpu=True, interval=0.5)
        cpu_percentages_str = ', '.join([f"{p}%" for p in core_usage])
        overall_cpu = psutil.cpu_percent(interval=0.5)

        self.master.after(0, self.update_cpu_info_ui, psutil.cpu_count(logical=False), psutil.cpu_count(logical=True), max_freq, current_freq, cpu_percentages_str, overall_cpu)

    def update_cpu_info_ui(self, physical_cores, logical_cores, max_freq, current_freq, cpu_percentages_str, overall_cpu):
        self.update_label("CPU", "Физические ядра", str(physical_cores))
        self.update_label("CPU", "Логические ядра", str(logical_cores))
        self.update_label("CPU", "Макс. частота", max_freq)
        self.update_label("CPU", "Текущая частота", current_freq)
        self.update_label("CPU", "Загрузка ядер CPU", cpu_percentages_str)
        self.update_label("CPU", "Общая загрузка CPU", f"{overall_cpu}%")
        self.cpu_progress_bar.set(overall_cpu / 100)


    def update_memory_info_thread(self):
        svmem = psutil.virtual_memory()
        total_memory = get_size(svmem.total)
        available_memory = get_size(svmem.available)
        used_memory = get_size(svmem.used)
        memory_percent = svmem.percent
        self.master.after(0, self.update_memory_info_ui, total_memory, available_memory, used_memory, memory_percent)

    def update_memory_info_ui(self, total_memory, available_memory, used_memory, memory_percent):
        self.update_label("Память", "Общая память", total_memory)
        self.update_label("Память", "Доступно памяти", available_memory)
        self.update_label("Память", "Используется памяти", used_memory)
        self.update_label("Память", "Загрузка памяти", f"{memory_percent}%")
        self.memory_progress_bar.set(memory_percent / 100)

    def update_swap_info_thread(self):
        swap = psutil.swap_memory()
        total_swap = get_size(swap.total)
        free_swap = get_size(swap.free)
        used_swap = get_size(swap.used)
        swap_percent = swap.percent
        self.master.after(0, self.update_swap_info_ui, total_swap, free_swap, used_swap, swap_percent)

    def update_swap_info_ui(self, total_swap, free_swap, used_swap, swap_percent):
        self.update_label("Swap", "Общий размер Swap", total_swap)
        self.update_label("Swap", "Свободно Swap", free_swap)
        self.update_label("Swap", "Используется Swap", used_swap)
        self.update_label("Swap", "Загрузка Swap", f"{swap_percent}%")

    def update_disk_info_thread(self):
        partitions = psutil.disk_partitions()
        disk_info_data = {}
        for i, partition in enumerate(partitions):
            base_label = self.disk_labels.get(partition.device, f"Диск {i+1}")
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                disk_info_data[partition.device] = {
                    "mountpoint": partition.mountpoint,
                    "total": get_size(partition_usage.total),
                    "used": get_size(partition_usage.used),
                    "free": get_size(partition_usage.free),
                    "percent": f"{partition_usage.percent}%"
                }
            except PermissionError:
                disk_info_data[partition.device] = {
                    "mountpoint": partition.mountpoint,
                    "total": "Нет доступа",
                    "used": "Нет доступа",
                    "free": "Нет доступа",
                    "percent": "Нет доступа"
                }
        disk_io = psutil.disk_io_counters()
        disk_io_read = get_size(disk_io.read_bytes)
        disk_io_write = get_size(disk_io.write_bytes)

        self.master.after(0, self.update_disk_info_ui, partitions, disk_info_data, disk_io_read, disk_io_write)


    def update_disk_info_ui(self, partitions, disk_info_data, disk_io_read, disk_io_write):
        for i, partition in enumerate(partitions):
            base_label = self.disk_labels.get(partition.device, f"Диск {i+1}")
            disk_data = disk_info_data.get(partition.device, {})
            self.update_label("Диски", f"{base_label} - Точка монтирования", disk_data.get("mountpoint", "N/A"))
            self.update_label("Диски", f"{base_label} - Общий размер", disk_data.get("total", "N/A"))
            self.update_label("Диски", f"{base_label} - Используется", disk_data.get("used", "N/A"))
            self.update_label("Диски", f"{base_label} - Свободно", disk_data.get("free", "N/A"))
            self.update_label("Диски", f"{base_label} - Использование", disk_data.get("percent", "N/A"))
        self.update_label("Диски", "Диск I/O - Прочитано", disk_io_read)
        self.update_label("Диски", "Диск I/O - Записано", disk_io_write)


    def update_network_info_thread(self):
        if_addrs = psutil.net_if_addrs()
        net_io = psutil.net_io_counters(pernic=True)
        network_data = {}
        for interface_name, addresses in if_addrs.items():
            ip_address = "N/A"
            mac_address = "N/A"
            for address in addresses:
                if str(address.family) == 'AddressFamily.AF_INET':
                    ip_address = address.address
                elif str(address.family) == 'AddressFamily.AF_PACKET':
                    mac_address = address.address
            io_counters = net_io.get(interface_name)
            sent = get_size(io_counters.bytes_sent) if io_counters else "N/A"
            recv = get_size(io_counters.bytes_recv) if io_counters else "N/A"
            network_data[interface_name] = {
                "ip": ip_address,
                "mac": mac_address,
                "sent": sent,
                "recv": recv
            }
        self.master.after(0, self.update_network_info_ui, if_addrs, network_data)


    def update_network_info_ui(self, if_addrs, network_data):
        for interface_name, addresses in if_addrs.items():
            base_label = self.network_labels.get(interface_name, f"Интерфейс {interface_name}")
            net_data = network_data.get(interface_name, {})
            self.update_label("Сеть", f"{base_label} - IP-адрес", net_data.get("ip", "N/A"))
            self.update_label("Сеть", f"{base_label} - MAC-адрес", net_data.get("mac", "N/A"))
            self.update_label("Сеть", f"{base_label} - Передано", net_data.get("sent", "N/A"))
            self.update_label("Сеть", f"{base_label} - Получено", net_data.get("recv", "N/A"))


    def update_gpu_info_thread(self):
        gpu_info_list = []
        if GPUtil:
            try:
                gpus = GPUtil.getGPUs()
                if not gpus:
                    gpu_info_list = [{"name": "GPU", "error": "GPU не обнаружены или информация недоступна."}]
                else:
                    for gpu in gpus:
                        gpu_info_list.append({
                            "name": gpu.name,
                            "load": f"{gpu.load * 100:.0f}%",
                            "memoryUsed": f"{gpu.memoryUsed} MB",
                            "memoryTotal": f"{gpu.memoryTotal} MB",
                            "temperature": f"{gpu.temperature} °C"
                        })
            except Exception as e:
                gpu_info_list = [{"name": "GPU", "error": f"Ошибка получения информации о GPU: {e}"}]
        else:
            gpu_info_list = [{"name": "GPU", "error": "GPUtil не установлен."}]

        self.master.after(0, self.update_gpu_info_ui, gpu_info_list)

    def update_gpu_info_ui(self, gpu_info_list):
        if not gpu_info_list:
            return

        if "error" in gpu_info_list[0]: # Handle error case
            self.update_label("GPU", "GPU", gpu_info_list[0]["error"])
        else:
            for i, gpu_info in enumerate(gpu_info_list):
                base_label = self.gpu_labels.get(gpu_info["name"], f"GPU {i+1}")
                self.update_label("GPU", f"{base_label} - Загрузка", gpu_info["load"])
                self.update_label("GPU", f"{base_label} - Используемая память", gpu_info["memoryUsed"])
                self.update_label("GPU", f"{base_label} - Общая память", gpu_info["memoryTotal"])
                self.update_label("GPU", f"{base_label} - Температура", gpu_info["temperature"])


    def update_battery_info_thread(self):
        battery_data = {}
        battery = psutil.sensors_battery()
        if battery:
            battery_data = {
                "present": "Да",
                "percent": f"{battery.percent}%",
                "time_left": "Неограничено" if battery.secsleft == psutil.POWER_TIME_UNLIMITED else "Неизвестно" if battery.secsleft == psutil.POWER_TIME_UNKNOWN else f"{battery.secsleft / 60:.0f} минут",
                "charging_status": "Заряжается" if battery.power_plugged else "Разряжается"
            }
        else:
            battery_data = {"error": "Батарея не найдена или информация недоступна."}

        self.master.after(0, self.update_battery_info_ui, battery_data)

    def update_battery_info_ui(self, battery_data):
        if "error" in battery_data:
            self.update_label("Батарея", "Батарея", battery_data["error"])
        else:
            self.update_label("Батарея", "Наличие батареи", battery_data["present"])
            self.update_label("Батарея", "Заряд батареи", battery_data["percent"])
            self.update_label("Батарея", "Время работы от батареи", battery_data["time_left"])
            self.update_label("Батарея", "Состояние зарядки", battery_data["charging_status"])


    def update_users_info_thread(self):
        users = psutil.users()
        self.master.after(0, self.update_users_info_ui, users)

    def update_users_info_ui(self, users):
        # Очищаем фрейм пользователей
        for widget in self.users_frame.winfo_children():
            widget.destroy()
        if not users:
            label = ctk.CTkLabel(self.users_frame, text="Нет данных о текущих пользователях.", font=("Roboto", 12))
            label.pack(pady=5)
        else:
            for user in users:
                start_time = datetime.fromtimestamp(user.started).strftime("%Y-%m-%d %H:%M:%S")
                user_info = f"Пользователь: {user.name} | Терминал: {user.terminal} | Хост: {user.host} | Время входа: {start_time}"
                label = ctk.CTkLabel(self.users_frame, text=user_info, font=("Roboto", 12), anchor="w")
                label.pack(padx=10, pady=5, anchor="w")



def run_info_viewer():
    root = ctk.CTk()
    root.geometry("1100x900")
    root.configure(fg_color="#121212")  # Темный фон главного окна
    root.resizable(False, False)  # Блокируем изменение размера
    PCInfoViewer(root)
    root.mainloop()

if __name__ == "__main__":
    run_info_viewer()