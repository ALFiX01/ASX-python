import os
import json
from datetime import datetime, timedelta
import psutil
import platform
import subprocess
from gui.utils import resource_path  # Импортируем resource_path из gui/utils.py

try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    import sys
    sys.exit(1)

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    print("Warning: GPUtil library not found. GPUtil information will not be available.")

from PIL import Image
from customtkinter import CTkImage

class HomeCenter:
    def __init__(self, parent):
        self.parent = parent
        self.info_frame = ctk.CTkScrollableFrame(self.parent, bg_color="transparent")
        self.info_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.system_info_cache = {}
        self.last_update = None
        self.update_interval = 5000
        self.recommendation_icons = self._load_recommendation_icons()
        self.setup_information_content()

    def _load_recommendation_icons(self):
        """Loads recommendation icons for better organization."""
        icons = {
            "Драйвера": "driver_icon.png",
            "Система": "system_icon.png",
            "Безопасность": "security_icon.png",
            "Оптимизация и настройки": "optimization_icon.png",
            "priority_high": "priority_high.png",
            "priority_medium": "priority_medium.png",
            "priority_low": "priority_low.png",
            "cpu": "cpu_icon.png",
            "disk": "disk_icon.png",
            "ram": "cpu_icon.png" # Reused cpu_icon for RAM
        }
        ctk_icons = {}
        for name, icon_file in icons.items():
            size = (24, 24) if name in ["cpu", "disk", "ram"] else (20, 20) if name in ["Драйвера", "Система", "Безопасность", "Оптимизация и настройки"] else (16, 16)
            ctk_icons[name] = CTkImage(Image.open(resource_path(os.path.join("icons", icon_file))), size=size)
        return ctk_icons

    def setup_information_content(self):
        self._clear_frame(self.info_frame) # Use internal clear_frame
        self._create_welcome_card() # Use internal card creation
        self.optimization_card = self._create_system_status_card() # Use internal card creation
        self.create_recommendations_section(self.optimization_card) # Keep recommendations as is
        self.schedule_updates()

    def _create_welcome_card(self):
        """Creates the welcome card."""
        self.create_card("ASX Hub", [
            (ctk.CTkLabel, {"text": "Добро пожаловать в центр управления системой", "font": ("Roboto", 18, "bold")}),
            (ctk.CTkLabel, {"text": "Оптимизируйте и настраивайте вашу систему", "font": ("Roboto", 14),
                            "text_color": ("gray70", "gray30")})
        ])

    def _create_system_status_card(self):
        """Creates the system status card and widgets."""
        card = self.create_card("Состояние системы", [])
        self.create_system_status_widgets(card)
        return card # Return for potential future use

    def create_card(self, title, widgets, card_pady=(0, 15)):
        """General card creation method."""
        card = ctk.CTkFrame(self.info_frame, fg_color=("gray86", "gray17"), corner_radius=10)
        card.pack(fill="x", padx=10, pady=card_pady)
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=20)
        title_label = ctk.CTkLabel(content, text=title, font=("Roboto", 20, "bold"))
        title_label.pack(anchor="w", pady=(0, 10))
        for widget_class, params in widgets:
            widget = widget_class(content, **params)
            widget.pack(anchor="w", pady=2)
        return content

    def create_system_status_widgets(self, parent):
        """Creates widgets for system status (Optimization, Disk, RAM)."""
        status_frame = ctk.CTkFrame(parent, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 15))
        status_frame.grid_columnconfigure((0, 1, 2), weight=1) # Configure columns at once

        status_types = [
            {"name": "Оптимизация", "icon": "Оптимизация и настройки", "percent_var": "optimization_percentage", "progress_var": "optimization_progress", "status_var": "optimization_status"},
            {"name": "Диск", "icon": "disk", "percent_var": "disk_usage_percentage", "progress_var": "disk_usage_progress", "status_var": "disk_usage_status"},
            {"name": "Память (RAM)", "icon": "ram", "percent_var": "ram_usage_percentage", "progress_var": "ram_usage_progress", "status_var": "ram_usage_status"}
        ]

        for i, status_type in enumerate(status_types):
            card = ctk.CTkFrame(status_frame, fg_color=("gray90", "gray20"), corner_radius=10)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            frame = ctk.CTkFrame(card, fg_color="transparent")
            frame.pack(fill="both", expand=True, padx=15, pady=15)

            title_frame = ctk.CTkFrame(frame, fg_color="transparent")
            title_frame.pack(fill="x", pady=(0, 5))
            ctk.CTkLabel(title_frame, text="", image=self.recommendation_icons[status_type["icon"]], compound="left", font=("Roboto", 16, "bold")).pack(side="left", padx=(0, 5))
            ctk.CTkLabel(title_frame, text=status_type["name"], font=("Roboto", 16, "bold")).pack(side="left")

            percent_label = ctk.CTkLabel(frame, text="0%", font=("Roboto", 48, "bold"))
            percent_label.pack(fill="x", pady=(10, 0))
            setattr(self, status_type["percent_var"], percent_label) # Dynamically set attribute

            progress_frame = ctk.CTkFrame(frame, fg_color="transparent")
            progress_frame.pack(fill="x", pady=(10, 0))
            progress_bar = ctk.CTkProgressBar(progress_frame, height=16, corner_radius=8, progress_color=("#2FA572", "#2FA572"))
            progress_bar.pack(fill="x")
            setattr(self, status_type["progress_var"], progress_bar) # Dynamically set attribute

            status_label = ctk.CTkLabel(frame, text="Состояние системы", font=("Roboto", 14), text_color=("gray70", "gray30"))
            status_label.pack(fill="x", pady=(5, 0))
            setattr(self, status_type["status_var"], status_label) # Dynamically set attribute

        self.update_system_status_widgets()

    def create_quick_actions(self, parent):
        """Creates quick action buttons with improved layout."""
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(0, 10))
        buttons_frame.grid_columnconfigure((0, 1), weight=1)

        actions = [
            ("Очистить кэш", self.clear_cache),
            ("Проверить обновления", self.check_updates),
            ("Анализ системы", self.analyze_system),
            ("Создать точку восстановления", self.create_restore_point)
        ]

        for i, (text, command) in enumerate(actions):
            btn = ctk.CTkButton(buttons_frame, text=text, command=command, height=32, corner_radius=8, font=("Roboto", 13))
            btn.grid(row=i // 2, column=i % 2, padx=5, pady=5, sticky="ew")

    def schedule_updates(self):
        self.update_system_info()
        self.update_system_status_widgets()
        self.parent.after(self.update_interval, self.schedule_updates)

    def update_system_info(self):
        """Updates system information efficiently."""
        try:
            psutil.cpu_percent() # Just call it to update internal stats, not used directly here
            psutil.virtual_memory() # Same here
            psutil.disk_usage('/') # And here
        except Exception as e:
            print(f"Error updating system info: {e}")

    def update_system_status_widgets(self):
        """Updates the system status widgets with current data."""
        percent = self.calculate_optimization_percentage()
        self._update_status_widget(self.optimization_progress, self.optimization_percentage, self.optimization_status, percent, "Система оптимизирована", "Требуется оптимизация", "Можно улучшить")

        disk = psutil.disk_usage('/')
        self._update_status_widget(self.disk_usage_progress, self.disk_usage_percentage, self.disk_usage_status, disk.percent, "Диск в норме", "Мало места на диске", "Диск заполнен наполовину", thresholds=[70, 90])

        memory = psutil.virtual_memory()
        self._update_status_widget(self.ram_usage_progress, self.ram_usage_percentage, self.ram_usage_status, memory.percent, "Память в норме", "Критически мало памяти", "Среднее использование памяти", thresholds=[70, 90])


    def _update_status_widget(self, progress_bar, percent_label, status_label, percent_value, status_good, status_bad, status_medium, thresholds=[70, 50]):
        """Helper function to update status widgets."""
        progress_bar.set(percent_value / 100)
        percent_label.configure(text=f"{int(percent_value)}%")
        if percent_value <= thresholds[0]:
            status_text = status_good
        elif percent_value > thresholds[0] and percent_value <= thresholds[1]:
            status_text = status_medium
        else:
            status_text = status_bad
        status_label.configure(text=status_text)


    def calculate_optimization_percentage(self):
        """Calculate the optimization percentage using tweak analysis data."""
        try:
            with open("tweak_analysis.json", "r", encoding='utf-8') as f:
                analysis = json.load(f)
                tweaks = analysis.get("tweaks", {})
                optimization_tweaks = [
                    data for data in tweaks.values()
                    if data.get("category") == "Оптимизация и настройки"
                ]
                total_tweaks = len(optimization_tweaks)
                optimized_tweaks = sum(1 for tweak in optimization_tweaks if tweak.get("optimized", False))
                return (optimized_tweaks / total_tweaks) * 100 if total_tweaks else 0
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error calculating optimization percentage: {e}")
            return 0

    def _clear_frame(self, frame): # Made internal
        """Clears all widgets from a frame."""
        for widget in frame.winfo_children():
            widget.destroy()

    def optimize_system(self):
        """Switch to Tweaks tab."""
        main_window = self.parent.winfo_toplevel()
        if hasattr(main_window, 'tabview'):
            main_window.tabview.set("Твики")

    def clear_cache(self): # Removed parent argument
        """Clears system cache."""
        # Implementation for cache clearing
        ctk.CTkMessageBox.showinfo("Информация", "Очистка кэша запущена (заглушка).")

    def check_updates(self): # Removed parent argument
        """Checks for system updates."""
        # Implementation for update checking
        ctk.CTkMessageBox.showinfo("Информация", "Проверка обновлений запущена (заглушка).")

    def analyze_system(self): # Removed parent argument
        """Analyzes system performance."""
        # Implementation for system analysis
        ctk.CTkMessageBox.showinfo("Информация", "Анализ системы запущен (заглушка).")

    def create_restore_point(self):
        """Creates a system restore point."""
        try:
            os.popen(
                "powershell.exe Checkpoint-Computer -Description 'ASX Hub Restore Point' -RestorePointType MODIFY_SETTINGS")
            self.show_success_message("Точка восстановления создана успешно")
        except Exception as e:
            self.show_error_message(f"Ошибка создания точки восстановления: {e}")

    def show_success_message(self, message):
        """Shows a success message."""
        ctk.CTkMessageBox.showinfo("Успех", message)

    def show_error_message(self, message):
        """Shows an error message."""
        ctk.CTkMessageBox.showerror("Ошибка", message)

    def get_cpu_name(self):
        """Get CPU name using different methods based on OS (original implementation)."""
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

    def get_gpu_info(self):
        """Get GPU information (original implementation)."""
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    return f"{', '.join([gpu.name for gpu in gpus])}"
                else:
                    return "Не найдено"
            except:
                return "Ошибка при получении информации"
        else:
            return "GPUtil не установлен"

    def format_uptime(self, seconds):
        """Formats uptime in seconds to a readable string (original implementation)."""
        days = seconds // (24 * 3600)
        seconds %= (24 * 3600)
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if days > 0:
            return f"{days} дн, {hours} ч, {minutes} мин"
        elif hours > 0:
            return f"{hours} ч, {minutes} мин, {seconds} сек"
        else:
            return f"{minutes} мин, {seconds} сек"

    def get_last_restore_point_date(self):
        """Get the creation date of the last system restore point using subprocess with error handling."""
        try:
            powershell_command = r'Get-WmiObject -Class SystemRestore -Namespace root\default | Sort-Object CreationTime -Descending | Select-Object -First 1 CreationTime | ForEach-Object {$_.CreationTime}'
            command = ['powershell.exe', '-Command', powershell_command]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       shell=False)  # shell=False for security
            stdout, stderr = process.communicate()

            if stderr:
                error_message = stderr.decode('cp866',
                                              errors='ignore').strip()  # Decode assuming CP866 or similar Windows encoding, adjust if needed
                print(f"PowerShell Error: {error_message}")
                return None

            stdout_str = stdout.decode('cp866', errors='ignore').strip()  # Decode assuming CP866, adjust if needed

            if not stdout_str:
                return None

            result = stdout_str.strip()
            dt = datetime.strptime(result[:14], "%Y%m%d%H%M%S")
            return dt.strftime("%d-%m-%Y %H:%M:%S")
        except Exception as e:
            print(f"Python Error getting restore point date: {e}")
            return None


    def load_outdated_drivers_data(self, filename="outdated_drivers_data.json"):
        """Loads outdated drivers data from JSON file."""
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"count": 0, "drivers": []}

    def is_restore_point_recommendation_needed(self, last_creation_date):
        """Check if a restore point recommendation is needed."""
        if last_creation_date is None:
            return True
        month_ago = datetime.now() - timedelta(days=30)
        last_creation_datetime = datetime.strptime(last_creation_date, "%d-%m-%Y %H:%M:%S") if last_creation_date else None
        return last_creation_datetime is None or last_creation_datetime < month_ago

    def go_to_tweak_page(self, category):
        """Navigates to the Tweaks tab and selects the specified category."""
        main_window = self.parent.winfo_toplevel()
        if hasattr(main_window, 'tabview'):
            main_window.tabview.set("Твики")
            if hasattr(main_window, 'select_category_in_tweaks'):
                main_window.select_category_in_tweaks(category)

    def create_recommendations_section(self, parent):
        """Create smart recommendations section with dynamic updates and priorities."""
        recommendations = []

        try:
            with open("tweak_analysis.json", "r", encoding='utf-8') as f:
                analysis = json.load(f)
                tweaks = analysis.get("tweaks", {})

            outdated_drivers_data = self.load_outdated_drivers_data()
            outdated_count = outdated_drivers_data.get("count", 0)
            last_restore_date_str = self.get_last_restore_point_date()
            restore_recommendation_needed = self.is_restore_point_recommendation_needed(last_restore_date_str)

            if outdated_count > 0:
                recommendations.append({
                    "type": "driver",
                    "title": f"Удалить устаревшие драйвера ({outdated_count})",
                    "category": "Драйвера",
                })

            if restore_recommendation_needed:
                recommendations.append({
                    "type": "restore_point",
                    "title": f"Создайте точку восстановления системы (Последняя: {last_restore_date_str or 'Не найдена'})",
                    "category": "Система",
                })

            from config import OPTIMIZATION_TWEAKS

            non_optimized = []
            for key, tweak in tweaks.items():
                if key in OPTIMIZATION_TWEAKS and not tweak.get("optimized", False):
                    priority = 2
                    category = tweak.get("category", "Неизвестно")
                    non_optimized.append({
                        "title": tweak.get("title", key),
                        "category": category,
                        "priority": priority,
                    })

            non_optimized.sort(key=lambda x: x["priority"], reverse=True)
            recommendations.extend(
                {"type": "tweak", **tweak} for tweak in non_optimized
            )


            if not recommendations:
                status_frame = ctk.CTkFrame(parent, fg_color=("gray86", "gray17"))
                status_frame.pack(fill="x", pady=10, padx=5)
                status_label = ctk.CTkLabel(
                    status_frame,
                    text="✓ Система полностью оптимизирована",
                    font=("Roboto", 14, "bold"),
                    text_color=("green", "light green"),
                )
                status_label.pack(pady=10)
            else:
                header_text = "Рекомендуемые оптимизации:"
                recommendation_count = len(recommendations)
                if recommendation_count > 3:
                    header_text = f"Топ важных оптимизаций ({recommendation_count} всего):"

                header = ctk.CTkLabel(parent, text=header_text, font=("Roboto", 14,))
                header.pack(anchor="w", pady=(0, 5))

                for rec in recommendations[:3]:
                    rec_frame = ctk.CTkFrame(parent, fg_color=("gray90", "gray20"), corner_radius=6)
                    rec_frame.pack(fill="x", pady=3, padx=5)

                    icon_image = None
                    if rec["type"] == "driver":
                        icon_image = self.recommendation_icons["Драйвера"]
                    elif rec["type"] == "restore_point":
                        icon_image = self.recommendation_icons["Система"]
                    elif rec["type"] == "firewall": # Assuming firewall is still relevant somewhere, if not, remove.
                        icon_image = self.recommendation_icons["Безопасность"]
                    elif rec["type"] == "tweak":
                        priority_icons = {3: "priority_high", 2: "priority_medium", 1: "priority_low"}
                        icon_key = priority_icons.get(rec["priority"])
                        icon_image = self.recommendation_icons.get(icon_key, self.recommendation_icons["Оптимизация и настройки"])

                    rec_icon_label = ctk.CTkLabel(rec_frame, image=icon_image, text="")
                    rec_icon_label.pack(side="left", padx=(5, 0))

                    rec_label = ctk.CTkLabel(
                        rec_frame,
                        text=rec['title'],
                        font=("Roboto", 13),
                        anchor="w",
                    )
                    rec_label.pack(side="left", padx=10, pady=5)

                    category_label = ctk.CTkLabel(
                        rec_frame,
                        text=rec["category"],
                        font=("Roboto", 11),
                        text_color=("gray50", "gray70"),
                        cursor="hand2",
                    )
                    category_label.pack(side="right", padx=10, pady=5)

                    if rec['type'] == 'tweak':
                        category_label.bind(
                            "<Button-1>",
                            lambda event, cat=rec["category"]: self.go_to_tweak_page(cat),
                        )


        except Exception as e:
            error_label = ctk.CTkLabel(
                parent,
                text="Ошибка загрузки рекомендаций",
                font=("Roboto", 13),
                text_color="red",
            )
            error_label.pack(pady=10)
            print(f"An error occurred: {e}")

    if __name__ == "__main__":
        app = ctk.CTk()
        app.title("ASX Hub")
        app.geometry("1050x800")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        class MockMainWindow:
            def __init__(self):
                self.tabview = self
                self._current_tab = None

            def set(self, tab_name):
                print(f"Switching to tab: {tab_name}")
                self._current_tab = tab_name

            def select_category_in_tweaks(self, category):
                print(f"Selecting category in Tweaks tab: {category}")

        mock_main_window = MockMainWindow()
        home_tab = app(mock_main_window)

        app.mainloop()