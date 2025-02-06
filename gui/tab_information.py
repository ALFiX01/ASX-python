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
import psutil  # Import psutil for system info

try:
    import GPUtil # Import GPUtil for GPU info
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    print("Warning: GPUtil library not found. GPU information will not be available.")

APP_VERSION = "1.0.0" # Make sure this is defined in your main app or config

class InformationTab:
    def __init__(self, parent):
        self.parent = parent

        # === Information Content Frame (Scrollable) ===
        self.info_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent" # Transparent background for integration
        )
        self.info_frame.pack(fill="both", expand=True, padx=20, pady=20) # Increased padding around the tab content

        self.setup_information_content()

    def setup_information_content(self):
        """Setup the content of the Information tab"""

        # === Application Information Card ===
        app_info_card = ctk.CTkFrame(
            self.info_frame,
            fg_color=("gray86", "gray17"), # Adaptive background color
            corner_radius=10,
            border_width=0
        )
        app_info_card.pack(fill="x", padx=10, pady=(0, 15)) # Increased bottom pady for card spacing

        app_info_content = ctk.CTkFrame(app_info_card, fg_color="transparent")
        app_info_content.pack(fill="x", padx=20, pady=20) # Increased padding inside card

        app_title_label = ctk.CTkLabel(
            app_info_content,
            text="ASX Hub",
            font=("Arial", 26, "bold") # Larger and bolder title
        )
        app_title_label.pack(anchor="w", pady=(0, 8)) # Increased pady below title

        app_version_label = ctk.CTkLabel(
            app_info_content,
            text=f"Версия: {APP_VERSION}", # Use your APP_VERSION variable
            font=("Arial", 13) # Slightly smaller version font
        )
        app_version_label.pack(anchor="w", pady=(0, 12)) # Increased pady below version

        app_desc_label = ctk.CTkLabel(
            app_info_content,
            text="ASX Hub - это приложение для оптимизации вашей системы и упрощения доступа к необходимым программам и ресурсам.\n"
                 "Оно предоставляет инструменты для настройки системы, загрузки полезных программ и быстрый доступ к веб-ресурсам.\n"
                 "Разработано для удобства и повышения продуктивности.",
            font=("Arial", 12),
            justify="left",
            text_color=("gray60", "gray70") # Even bleaker description color
        )
        app_desc_label.pack(anchor="w")

        # === Developer Information Card ===
        dev_info_card = ctk.CTkFrame(
            self.info_frame,
            fg_color=("gray86", "gray17"),
            corner_radius=10,
            border_width=0
        )
        dev_info_card.pack(fill="x", padx=10, pady=(15, 15)) # Increased top and bottom pady for card spacing

        dev_info_content = ctk.CTkFrame(dev_info_card, fg_color="transparent")
        dev_info_content.pack(fill="x", padx=20, pady=20)

        dev_title_label = ctk.CTkLabel(
            dev_info_content,
            text="Разработчик",
            font=("Arial", 20, "bold") # Slightly larger title
        )
        dev_title_label.pack(anchor="w", pady=(0, 10))

        dev_name_label = ctk.CTkLabel(
            dev_info_content,
            text="ALFiX.inc", # Replace with your name
            font=("Arial", 12)
        )
        dev_name_label.pack(anchor="w", pady=(0, 3)) # Reduced pady

        dev_contact_label = ctk.CTkLabel(
            dev_info_content,
            text="Discord.GG/ALFiX-Zone", # Replaced email with Discord invite link text
            font=("Arial", 12),
            text_color=("skyblue3", "lightblue") # Slightly brighter link color
        )
        dev_contact_label.pack(anchor="w")
        dev_contact_label.bind("<Button-1>", lambda event: webbrowser.open("https://discord.gg/ALFiX-Zone")) # Open Discord invite link in browser
        dev_contact_label.configure(cursor="hand2") # Change cursor to hand on hover

        # === Links Card ===
        links_card = ctk.CTkFrame(
            self.info_frame,
            fg_color=("gray86", "gray17"),
            corner_radius=10,
            border_width=0
        )
        links_card.pack(fill="x", padx=10, pady=(15, 15)) # Increased top and bottom pady for card spacing

        links_content = ctk.CTkFrame(links_card, fg_color="transparent")
        links_content.pack(fill="x", padx=20, pady=20)

        links_title_label = ctk.CTkLabel(
            links_content,
            text="Ссылки",
            font=("Arial", 20, "bold") # Slightly larger title
        )
        links_title_label.pack(anchor="w", pady=(0, 10))

        github_button = ctk.CTkButton(
            links_content,
            text="GitHub Репозиторий",
            command=lambda: webbrowser.open("https://github.com/ALFiX01/ASX-python"), # Replace with your repo URL
            width=160, # Slightly wider button
            height=36, # Slightly taller button
            corner_radius=8
        )
        github_button.pack(anchor="w", pady=(0, 8)) # Increased pady below button

        website_button = ctk.CTkButton(
            links_content,
            text="Поддержка",
            command=lambda: webbrowser.open("https://your-website.com"), # Replace with your website URL or remove if not applicable
            width=220, # Slightly wider button
            height=36, # Slightly taller button
            corner_radius=8
        )
        website_button.pack(anchor="w")

        # === System Information Card ===
        system_info_card = ctk.CTkFrame(
            self.info_frame,
            fg_color=("gray86", "gray17"),
            corner_radius=10,
            border_width=0
        )
        system_info_card.pack(fill="x", padx=10, pady=(15, 20)) # Increased top and bottom pady for card spacing

        system_info_content = ctk.CTkFrame(system_info_card, fg_color="transparent")
        system_info_content.pack(fill="x", padx=20, pady=20)

        system_title_label = ctk.CTkLabel(
            system_info_content,
            text="Системная информация",
            font=("Arial", 20, "bold") # Slightly larger title
        )
        system_title_label.pack(anchor="w", pady=(0, 10))

        os_label = ctk.CTkLabel(
            system_info_content,
            text=f"Операционная система: {platform.system()} {platform.platform()}",
            font=("Arial", 12)
        )
        os_label.pack(anchor="w", pady=(0, 2))

        python_label = ctk.CTkLabel(
            system_info_content,
            text=f"Версия Python: {sys.version.split()[0]}", # Show only major.minor.micro version
            font=("Arial", 12)
        )
        python_label.pack(anchor="w", pady=(0, 2))

        ctk_label = ctk.CTkLabel(
            system_info_content,
            text=f"Версия CustomTkinter: {ctk.__version__}",
            font=("Arial", 12)
        )
        ctk_label.pack(anchor="w", pady=(0, 8)) # Increased pady

        # === CPU Information ===
        cpu_name = self.get_cpu_name() # Use the new get_cpu_name function

        cpu_label = ctk.CTkLabel(
            system_info_content,
            text=f"Процессор (CPU): {cpu_name}",
            font=("Arial", 12)
        )
        cpu_label.pack(anchor="w", pady=(0, 2))

        # === GPU Information ===
        gpu_info_text = "Информация о GPU недоступна" # Default text if no GPU info
        if GPU_AVAILABLE:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_names = ", ".join([gpu.name for gpu in gpus]) # List GPU names
                gpu_info_text = f"Видеокарта (GPU): {gpu_names}"
            else:
                gpu_info_text = "Видеокарта (GPU): Не найдено" # If GPUtil finds no GPUs
        else:
            gpu_info_text = "Видеокарта (GPU): GPUtil не установлен" # If GPUtil module is not available

        gpu_label = ctk.CTkLabel(
            system_info_content,
            text=gpu_info_text,
            font=("Arial", 12)
        )
        gpu_label.pack(anchor="w", pady=(0, 2))

        # === RAM Information ===
        ram_gb = psutil.virtual_memory().total / (1024**3) # Convert bytes to GB
        ram_label = ctk.CTkLabel(
            system_info_content,
            text=f"Оперативная память (RAM): {ram_gb:.2f} ГБ", # Format to 2 decimal places
            font=("Arial", 12)
        )
        ram_label.pack(anchor="w")

    def get_cpu_name(self):
        """Get CPU name using different methods based on OS"""
        os_name = platform.system()
        cpu_name = "Не удалось определить"

        if os_name == "Windows":
            try:
                # Execute WMIC command to get CPU name
                output = os.popen("wmic cpu get name").read().strip()
                # Split lines and extract the correct line
                lines = [line.strip() for line in output.split('\n') if line.strip()]
                if len(lines) > 1:
                    cpu_name = lines[1]
            except Exception as e:
                print(f"Ошибка WMIC для CPU Name: {e}")

        elif os_name == "Linux":
            try:
                # Read from /proc/cpuinfo
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if "model name" in line.lower():
                            cpu_name = line.split(":")[1].strip()
                            break
            except Exception as e:
                print(f"Ошибка чтения /proc/cpuinfo: {e}")

        elif os_name == "Darwin":  # macOS
            try:
                # Use sysctl for macOS
                cpu_name = os.popen("sysctl -n machdep.cpu.brand_string").read().strip()
            except Exception as e:
                print(f"Ошибка sysctl для CPU Name (macOS): {e}")

        # Fallback to platform.processor() if still not found
        if cpu_name == "Не удалось определить":
            cpu_name = platform.processor() or cpu_name

        return cpu_name


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Information Tab Example")
    app.geometry("800x700")

    information_tab = InformationTab(app) # You would usually create this tab within your main app

    app.mainloop()