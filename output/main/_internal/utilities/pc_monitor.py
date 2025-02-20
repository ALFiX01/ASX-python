import os
import platform
import psutil
import tkinter as tk
from datetime import datetime

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


class PCInfoViewer:
    def __init__(self, master):
        self.master = master
        self.master.title("Информация о ПК")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.master.geometry("1100x900")

        header = ctk.CTkLabel(master, text="Информация о ПК", font=("Roboto", 20, "bold"))
        header.pack(pady=10)

        # Создаем Tabview для разделения информации по категориям
        self.tabview = ctk.CTkTabview(master, width=1050, height=700)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)

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

        # --- Заполнение вкладок информацией ---
        # Система
        self.add_info_label("Система", "ОС", "...")
        self.add_info_label("Система", "Имя компьютера", "...")
        self.add_info_label("Система", "Архитектура", "...")
        self.add_info_label("Система", "Загрузка системы", "...")
        self.add_info_label("Система", "Время включения пк", "...")
        self.add_info_label("Система", "Процессор", "...")

        # CPU (добавлены данные из cpuinfo)
        self.add_info_label("CPU", "Физические ядра", "...")
        self.add_info_label("CPU", "Логические ядра", "...")
        self.add_info_label("CPU", "Макс. частота", "...")
        self.add_info_label("CPU", "Текущая частота", "...")
        self.add_info_label("CPU", "Загрузка ядер CPU", "...")
        self.add_info_label("CPU", "Общая загрузка CPU", "...")
        self.add_info_label("CPU", "Бренд процессора", "...")
        self.add_info_label("CPU", "Разрядность", "...")
        # Прогресс-бар для общей загрузки CPU
        self.cpu_progress_bar = ctk.CTkProgressBar(self.tabs["CPU"], width=200)
        self.cpu_progress_bar.grid(row=self.row_counter["CPU"], column=1, padx=10, pady=5, sticky="w")
        self.row_counter["CPU"] += 1

        # Память
        self.add_info_label("Память", "Общая память", "...")
        self.add_info_label("Память", "Доступно памяти", "...")
        self.add_info_label("Память", "Используется памяти", "...")
        self.add_info_label("Память", "Загрузка памяти", "...")
        # Прогресс-бар для загрузки памяти
        self.memory_progress_bar = ctk.CTkProgressBar(self.tabs["Память"], width=200)
        self.memory_progress_bar.grid(row=self.row_counter["Память"], column=1, padx=10, pady=5, sticky="w")
        self.row_counter["Память"] += 1

        # Swap
        self.add_info_label("Swap", "Общий размер Swap", "...")
        self.add_info_label("Swap", "Свободно Swap", "...")
        self.add_info_label("Swap", "Используется Swap", "...")
        self.add_info_label("Swap", "Загрузка Swap", "...")

        # Диски
        self.disk_labels = {}
        partitions = psutil.disk_partitions()
        for i, partition in enumerate(partitions):
            base_label = f"Диск {i+1} ({partition.device})"
            self.add_info_label("Диски", f"{base_label} - Точка монтирования", "...")
            self.add_info_label("Диски", f"{base_label} - Общий размер", "...")
            self.add_info_label("Диски", f"{base_label} - Используется", "...")
            self.add_info_label("Диски", f"{base_label} - Свободно", "...")
            self.add_info_label("Диски", f"{base_label} - Использование", "...")
            self.disk_labels[partition.device] = base_label
        # Статистика дисковой I/O
        self.add_info_label("Диски", "Диск I/O - Прочитано", "...")
        self.add_info_label("Диски", "Диск I/O - Записано", "...")

        # Сеть
        self.network_labels = {}
        if_addrs = psutil.net_if_addrs()
        for interface_name in if_addrs:
            base_label = f"Интерфейс {interface_name}"
            self.add_info_label("Сеть", f"{base_label} - IP-адрес", "...")
            self.add_info_label("Сеть", f"{base_label} - MAC-адрес", "...")
            self.add_info_label("Сеть", f"{base_label} - Передано", "...")
            self.add_info_label("Сеть", f"{base_label} - Получено", "...")
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
                        self.add_info_label("GPU", f"{base_label} - Загрузка", "...")
                        self.add_info_label("GPU", f"{base_label} - Используемая память", "...")
                        self.add_info_label("GPU", f"{base_label} - Общая память", "...")
                        self.add_info_label("GPU", f"{base_label} - Температура", "...")
                        self.gpu_labels[gpu.name] = base_label
            except Exception as e:
                self.add_info_label("GPU", "GPU", f"Ошибка получения информации о GPU: {e}")
        else:
            self.add_info_label("GPU", "GPU", "GPUtil не установлен.")

        # Батарея
        self.battery_labels = {}
        battery = psutil.sensors_battery()
        if battery:
            self.add_info_label("Батарея", "Наличие батареи", "...")
            self.add_info_label("Батарея", "Заряд батареи", "...")
            self.add_info_label("Батарея", "Время работы от батареи", "...")
            self.add_info_label("Батарея", "Состояние зарядки", "...")
        else:
            self.add_info_label("Батарея", "Батарея", "Батарея не найдена или информация недоступна.")

        # Пользователи – динамический список
        self.users_frame = ctk.CTkScrollableFrame(self.tabs["Пользователи"], width=1020, height=650, fg_color="transparent")
        self.users_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Кнопка обновления информации
        self.refresh_button = ctk.CTkButton(
            master,
            text="Обновить информацию",
            command=self.update_info,
            width=200,
            corner_radius=8,
            font=("Roboto", 13)
        )
        self.refresh_button.pack(pady=10)

        self.update_info()

    def add_info_label(self, section, label_text, value_placeholder):
        """
        Создает пару меток (название и значение) на вкладке section.
        """
        tab = self.tabs[section]
        row = self.row_counter[section]
        label = ctk.CTkLabel(tab, text=f"{label_text}:", font=("Roboto", 12, "bold"), anchor="w")
        value_label = ctk.CTkLabel(tab, text=value_placeholder, font=("Roboto", 12), wraplength=600, justify="left", anchor="w")
        label.grid(row=row, column=0, padx=(10, 5), pady=5, sticky="w")
        value_label.grid(row=row, column=1, padx=(5, 10), pady=5, sticky="w")
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
        self.update_system_info()
        self.update_cpu_info()
        self.update_memory_info()
        self.update_swap_info()
        self.update_disk_info()
        self.update_network_info()
        self.update_gpu_info()
        self.update_battery_info()
        self.update_users_info()

    def update_system_info(self):
        uname = platform.uname()
        system_info = uname.system
        computer_name = uname.node
        if system_info == "Windows":
            win_ver = platform.win32_ver()
            os_release = f"Windows {win_ver[0]}"
        else:
            os_release = uname.release
        architecture = uname.machine
        processor = platform.processor() if platform.processor() else "Неизвестно"
        system_load = psutil.cpu_percent()
        boot_time_timestamp = psutil.boot_time()
        boot_time = datetime.fromtimestamp(boot_time_timestamp).strftime("%Y-%m-%d %H:%M:%S")

        self.update_label("Система", "ОС", os_release)
        self.update_label("Система", "Имя компьютера", computer_name)
        self.update_label("Система", "Архитектура", architecture)
        self.update_label("Система", "Загрузка системы", f"{system_load}%")
        self.update_label("Система", "Время включения пк", boot_time)
        self.update_label("Система", "Процессор", processor)

    def update_cpu_info(self):
        try:
            cpu_freq = psutil.cpu_freq()
            max_freq = f"{cpu_freq.max:.2f} МГц" if cpu_freq else "N/A"
            current_freq = f"{cpu_freq.current:.2f} МГц" if cpu_freq else "N/A"
        except Exception:
            max_freq, current_freq = "Недоступно", "Недоступно"

        core_usage = psutil.cpu_percent(percpu=True, interval=0.5)
        cpu_percentages_str = ', '.join([f"{p}%" for p in core_usage])

        self.update_label("CPU", "Физические ядра", str(psutil.cpu_count(logical=False)))
        self.update_label("CPU", "Логические ядра", str(psutil.cpu_count(logical=True)))
        self.update_label("CPU", "Макс. частота", max_freq)
        self.update_label("CPU", "Текущая частота", current_freq)
        self.update_label("CPU", "Загрузка ядер CPU", cpu_percentages_str)
        overall_cpu = psutil.cpu_percent(interval=0.5)
        self.update_label("CPU", "Общая загрузка CPU", f"{overall_cpu}%")
        self.cpu_progress_bar.set(overall_cpu / 100)

        # Дополнительная информация из cpuinfo (если доступна)
        if cpuinfo:
            info = cpuinfo.get_cpu_info()
            brand = info.get('brand_raw', 'N/A')
            bits = info.get('bits', 'N/A')
        else:
            brand = "N/A"
            bits = "N/A"
        self.update_label("CPU", "Бренд процессора", brand)
        self.update_label("CPU", "Разрядность", str(bits))

    def update_memory_info(self):
        svmem = psutil.virtual_memory()
        total_memory = get_size(svmem.total)
        available_memory = get_size(svmem.available)
        used_memory = get_size(svmem.used)
        memory_percent = svmem.percent

        self.update_label("Память", "Общая память", total_memory)
        self.update_label("Память", "Доступно памяти", available_memory)
        self.update_label("Память", "Используется памяти", used_memory)
        self.update_label("Память", "Загрузка памяти", f"{memory_percent}%")
        self.memory_progress_bar.set(memory_percent / 100)

    def update_swap_info(self):
        swap = psutil.swap_memory()
        self.update_label("Swap", "Общий размер Swap", get_size(swap.total))
        self.update_label("Swap", "Свободно Swap", get_size(swap.free))
        self.update_label("Swap", "Используется Swap", get_size(swap.used))
        self.update_label("Swap", "Загрузка Swap", f"{swap.percent}%")

    def update_disk_info(self):
        partitions = psutil.disk_partitions()
        for i, partition in enumerate(partitions):
            base_label = self.disk_labels.get(partition.device, f"Диск {i+1}")
            self.update_label("Диски", f"{base_label} - Точка монтирования", partition.mountpoint)
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                self.update_label("Диски", f"{base_label} - Общий размер", get_size(partition_usage.total))
                self.update_label("Диски", f"{base_label} - Используется", get_size(partition_usage.used))
                self.update_label("Диски", f"{base_label} - Свободно", get_size(partition_usage.free))
                self.update_label("Диски", f"{base_label} - Использование", f"{partition_usage.percent}%")
            except PermissionError:
                self.update_label("Диски", f"{base_label} - Общий размер", "Нет доступа")
                self.update_label("Диски", f"{base_label} - Используется", "Нет доступа")
                self.update_label("Диски", f"{base_label} - Свободно", "Нет доступа")
                self.update_label("Диски", f"{base_label} - Использование", "Нет доступа")
        # Обновляем общую статистику дисковой I/O
        disk_io = psutil.disk_io_counters()
        self.update_label("Диски", "Диск I/O - Прочитано", get_size(disk_io.read_bytes))
        self.update_label("Диски", "Диск I/O - Записано", get_size(disk_io.write_bytes))

    def update_network_info(self):
        if_addrs = psutil.net_if_addrs()
        net_io = psutil.net_io_counters(pernic=True)
        for interface_name, addresses in if_addrs.items():
            base_label = self.network_labels.get(interface_name, f"Интерфейс {interface_name}")
            ip_address = "N/A"
            mac_address = "N/A"
            for address in addresses:
                if str(address.family) == 'AddressFamily.AF_INET':
                    ip_address = address.address
                elif str(address.family) == 'AddressFamily.AF_PACKET':
                    mac_address = address.address
            self.update_label("Сеть", f"{base_label} - IP-адрес", ip_address)
            self.update_label("Сеть", f"{base_label} - MAC-адрес", mac_address)
            # Обновляем данные по переданным/полученным байтам
            io_counters = net_io.get(interface_name)
            if io_counters:
                sent = get_size(io_counters.bytes_sent)
                recv = get_size(io_counters.bytes_recv)
            else:
                sent, recv = "N/A", "N/A"
            self.update_label("Сеть", f"{base_label} - Передано", sent)
            self.update_label("Сеть", f"{base_label} - Получено", recv)

    def update_gpu_info(self):
        if GPUtil:
            try:
                gpus = GPUtil.getGPUs()
                if not gpus:
                    self.update_label("GPU", "GPU", "GPU не обнаружены или информация недоступна.")
                    return
                for i, gpu in enumerate(gpus):
                    base_label = self.gpu_labels.get(gpu.name, f"GPU {i+1}")
                    self.update_label("GPU", f"{base_label} - Загрузка", f"{gpu.load * 100:.0f}%")
                    self.update_label("GPU", f"{base_label} - Используемая память", f"{gpu.memoryUsed} MB")
                    self.update_label("GPU", f"{base_label} - Общая память", f"{gpu.memoryTotal} MB")
                    self.update_label("GPU", f"{base_label} - Температура", f"{gpu.temperature} °C")
            except Exception as e:
                self.update_label("GPU", "GPU", f"Ошибка получения информации о GPU: {e}")

    def update_battery_info(self):
        battery = psutil.sensors_battery()
        if battery:
            self.update_label("Батарея", "Наличие батареи", "Да")
            self.update_label("Батарея", "Заряд батареи", f"{battery.percent}%")
            if battery.secsleft not in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN):
                minutes_left = battery.secsleft / 60
                time_left_str = f"{minutes_left:.0f} минут"
            else:
                time_left_str = "Неограничено" if battery.power_plugged else "Неизвестно"
            self.update_label("Батарея", "Время работы от батареи", time_left_str)
            self.update_label("Батарея", "Состояние зарядки", "Заряжается" if battery.power_plugged else "Разряжается")
        else:
            self.update_label("Батарея", "Батарея", "Батарея не найдена или информация недоступна.")

    def update_users_info(self):
        # Очищаем фрейм пользователей
        for widget in self.users_frame.winfo_children():
            widget.destroy()
        users = psutil.users()
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
    PCInfoViewer(root)
    root.mainloop()


if __name__ == "__main__":
    run_info_viewer()
