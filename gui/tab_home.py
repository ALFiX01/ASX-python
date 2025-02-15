import os
import tkinter as tk
try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    import sys
    sys.exit(1)
import platform
import sys
import webbrowser
import psutil
import datetime
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    print("Warning: GPUtil library not found. GPU information will not be available.")

from config import APP_VERSION  # You might want to use this, I've kept it.

class HomeCenter:
    def __init__(self, parent):
        self.parent = parent
        self.tweaks = {  # Define tweaks here for easier management
            "Отключить анимации": (3, False),  # (percentage, is_enabled)
            "Оптимизировать загрузку": (5, False),
            "Отключить ненужные службы": (7, False),
            "Очистить кэш браузера": (2, False),
            "Включить защиту от вредоносных программ": (8, False),
        }
        # Load initial state from a config file (if it exists), otherwise default to False
        self.load_tweak_states()
        self.info_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.info_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.setup_information_content()
        self.update_optimization_display() # Initial display update

    def setup_information_content(self):
        """Setup the content of the Home tab"""
        self.clear_frame(self.info_frame) # Clear previous widgets

        # --- Welcome Card ---
        self.create_card(self.info_frame, "Добро пожаловать в ASX Hub!", [
            (ctk.CTkLabel, {"text": "Ваш центр управления системой.", "font": ("Roboto", 16)})
        ], card_pady=(0, 15))

        # --- Optimization Status Card ---
        optimization_card = self.create_card(self.info_frame, "Состояние оптимизации", [], card_pady=(15, 15))
        self.optimization_percentage_label = ctk.CTkLabel(optimization_card, text="", font=("Roboto", 36, "bold"))
        self.optimization_percentage_label.pack(anchor="w", pady=(0, 10))

        self.optimization_progress_bar = ctk.CTkProgressBar(optimization_card, width=300)
        self.optimization_progress_bar.pack(anchor="w", pady=(0, 10))

        self.optimization_description_label = ctk.CTkLabel(optimization_card, text="", font=("Roboto", 12))
        self.optimization_description_label.pack(anchor="w", pady=(0, 10))

        optimize_button = ctk.CTkButton(optimization_card, text="Оптимизировать", command=self.optimize_system, width=150, height=30, corner_radius=8, font=("Roboto", 13))
        optimize_button.pack(anchor="w", pady=(0, 10))

        # --- Recommendations Card ---
        recommendations_content = self.create_card(self.info_frame, "Рекомендации", [], card_pady=(15, 15))

        for tweak_name, (percentage, is_enabled) in self.tweaks.items():
            frame = ctk.CTkFrame(recommendations_content, fg_color="transparent")  # Use a frame for layout
            frame.pack(fill="x", pady=2)  # Pack the frame

            label = ctk.CTkLabel(frame, text=tweak_name, font=("Roboto", 12), anchor="w")  # Anchor label to the west
            label.pack(side="left", fill="x", expand=True)  # Allow the label to expand

            button = ctk.CTkButton(frame, text="Вкл" if not is_enabled else "Выкл",
                                   command=lambda t=tweak_name: self.toggle_tweak(t), # Use lambda for the command
                                   width=80, height=24, corner_radius=6, font=("Roboto", 12))
            button.pack(side="right")

        # --- Personal Recommendations Card ---
        personal_recommendations_content = self.create_card(self.info_frame, "Персональные рекомендации", [], card_pady=(15, 15))

        # Example recommendation: Create a system restore point
        last_restore_point = self.get_last_restore_point_date()
        if last_restore_point:
            days_since_last_restore = (datetime.datetime.now() - last_restore_point).days
            if days_since_last_restore > 30:
                self.create_personal_recommendation(personal_recommendations_content, "Создать точку восстановления", "Вы давно не создавали точку восстановления системы. Рекомендуется создать новую точку восстановления.", self.create_restore_point)

        # --- Quick Access Card ---
        self.create_card(self.info_frame, "Быстрый доступ", [
            (ctk.CTkButton, {"text": "GitHub", "command": lambda: webbrowser.open("https://github.com/ALFiX01/ASX-python"), "width": 100, "height": 28, "corner_radius": 8, "font": ("Roboto", 13)}),
            (ctk.CTkButton, {"text": "Поддержка", "command": lambda: webbrowser.open("https://your-website.com"), "width": 100, "height": 28, "corner_radius": 8, "font": ("Roboto", 13)})
        ], card_pady=(15,15))

        # --- System Information Card ---
        self.create_card(self.info_frame, "Системная информация", [
            (ctk.CTkLabel, {"text": f"Операционная система: {platform.system()} {platform.platform()}", "font": ("Roboto", 12)}),
            (ctk.CTkLabel, {"text": f"Версия Python: {sys.version.split()[0]}", "font": ("Roboto", 12)}),
            (ctk.CTkLabel, {"text": f"Версия CustomTkinter: {ctk.__version__}", "font": ("Roboto", 12)}),
            (ctk.CTkLabel, {"text": f"Процессор (CPU): {self.get_cpu_name()}", "font": ("Roboto", 12)}),
            (ctk.CTkLabel, {"text": self.get_gpu_info(), "font": ("Roboto", 12)}),
            (ctk.CTkLabel, {"text": f"Оперативная память (RAM): {psutil.virtual_memory().total / (1024**3):.2f} ГБ", "font": ("Roboto", 12)})
        ], card_pady=(15, 20))

    def create_card(self, parent, title_text, widgets, card_padx=10, card_pady=15):
        """Creates a reusable card layout."""
        card = ctk.CTkFrame(parent, fg_color=("gray86", "gray17"), corner_radius=10, border_width=0)
        card.pack(fill="x", padx=card_padx, pady=card_pady)

        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=20, pady=20)

        title = ctk.CTkLabel(content_frame, text=title_text, font=("Roboto", 20, "bold"))
        title.pack(anchor="w", pady=(0, 10))

        for widget_class, widget_params in widgets:
            widget = widget_class(content_frame, **widget_params)
            widget.pack(anchor="w", pady=2)  # Consistent vertical padding

        return content_frame  # Return the content frame for adding custom widgets

    def clear_frame(self, frame):
        """Clears all widgets from a frame."""
        for widget in frame.winfo_children():
            widget.destroy()

    def calculate_optimization_percentage(self):
        """Calculate the optimization percentage."""
        total_possible = sum(percentage for percentage, _ in self.tweaks.values())
        current_score = sum(percentage for percentage, is_enabled in self.tweaks.values() if is_enabled)
        return (current_score / total_possible) * 100 if total_possible else 0

    def update_optimization_display(self):
        """Updates the optimization percentage, progress bar, and description."""
        percentage = self.calculate_optimization_percentage()
        self.optimization_percentage_label.configure(text=f"{percentage:.1f}%")  # Format to one decimal place
        self.optimization_progress_bar.set(percentage / 100)

        if percentage >= 75:
            description = "Отлично"
        elif percentage >= 50:
            description = "Хорошо"
        elif percentage >= 25:
            description = "Удовлетворительно"
        else:
            description = "Требуется оптимизация"
        self.optimization_description_label.configure(text=description)

    def toggle_tweak(self, tweak_name):
        """Toggles a tweak on or off."""
        percentage, is_enabled = self.tweaks[tweak_name]
        self.tweaks[tweak_name] = (percentage, not is_enabled)
        self.update_optimization_display()
        self.setup_information_content()  # Rebuild the recommendations card
        self.save_tweak_states() # Save state after toggling

    def optimize_system(self):
        """'Optimize' the system (currently just enables all tweaks)."""
        for tweak_name in self.tweaks:
            self.tweaks[tweak_name] = (self.tweaks[tweak_name][0], True)  # Enable all
        self.update_optimization_display()
        self.setup_information_content() # Refresh UI
        self.save_tweak_states() # Save changes

    def get_cpu_name(self):
        """Get CPU name."""
        try:
            return os.popen("wmic cpu get name").read().strip().split('\n')[1]
        except:
            pass

        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line.lower():
                        return line.split(":")[1].strip()
        except:
            pass

        try:
            return os.popen("sysctl -n machdep.cpu.brand_string").read().strip()
        except:
            pass

        return platform.processor() or "Неизвестно"

    def get_gpu_info(self):
        """Get GPU information."""
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    return f"Видеокарта (GPU): {', '.join([gpu.name for gpu in gpus])}"
                else:
                    return "Видеокарта (GPU): Не найдено"
            except:
                return "Видеокарта (GPU): Ошибка при получении информации"
        else:
            return "Видеокарта (GPU): GPUtil не установлен"

    def load_tweak_states(self):
        """Loads tweak states from a configuration file (if it exists)."""
        try:
            with open("config.txt", "r") as f:
                for line in f:
                    name, state = line.strip().split("=")
                    if name in self.tweaks:  # Check if tweak still exists
                        self.tweaks[name] = (self.tweaks[name][0], state.lower() == "true")
        except FileNotFoundError:
            pass  # It's okay if the file doesn't exist yet

    def save_tweak_states(self):
        """Saves the current tweak states to a configuration file."""
        with open("config.txt", "w") as f:
            for name, (_, is_enabled) in self.tweaks.items():
                f.write(f"{name}={is_enabled}\n")

    def get_last_restore_point_date(self):
        """Get the date of the last system restore point."""
        try:
            restore_points = os.popen("powershell.exe Get-ComputerRestorePoint").read()
            if "Creation Time" in restore_points:
                last_restore_point_line = restore_points.splitlines()[-2]  # Second last line contains the last restore point
                last_restore_point_date_str = last_restore_point_line.split(":")[1].strip()
                return datetime.datetime.strptime(last_restore_point_date_str, "%m/%d/%Y %I:%M:%S %p")
        except:
            pass
        return None

    def create_restore_point(self):
        """Create a new system restore point."""
        try:
            os.popen("powershell.exe Checkpoint-Computer -Description 'ASX Hub Restore Point' -RestorePointType MODIFY_SETTINGS")
            ctk.CTkMessageBox.show_info("Создание точки восстановления", "Точка восстановления успешно создана.")
        except Exception as e:
            ctk.CTkMessageBox.show_error("Ошибка", f"Не удалось создать точку восстановления: {e}")

    def create_personal_recommendation(self, parent, title, description, command):
        """Create a personal recommendation card."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")  # Use a frame for layout
        frame.pack(fill="x", pady=2)  # Pack the frame

        title_label = ctk.CTkLabel(frame, text=title, font=("Roboto", 14, "bold"), anchor="w")  # Anchor label to the west
        title_label.pack(side="top", fill="x", expand=True)  # Allow the label to expand

        description_label = ctk.CTkLabel(frame, text=description, font=("Roboto", 12), anchor="w")  # Anchor label to the west
        description_label.pack(side="top", fill="x", expand=True)  # Allow the label to expand

        button = ctk.CTkButton(frame, text="Выполнить", command=command, width=80, height=24, corner_radius=6, font=("Roboto", 12))
        button.pack(side="right")

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("ASX Hub")
    app.geometry("800x600")  # Adjusted for better initial size
    ctk.set_appearance_mode("System")  # Follow system appearance
    ctk.set_default_color_theme("blue")

    home_tab = HomeCenter(app)
    app.mainloop()
