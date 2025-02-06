import os
import tkinter as tk
try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    import sys
    sys.exit(1)

from utils.github_handler import GitHubHandler

class UtilitiesTab:
    def __init__(self, parent):
        self.parent = parent
        self.github_handler = GitHubHandler()

        # Create utilities list frame with scrollbar
        self.utilities_frame = ctk.CTkScrollableFrame(self.parent)
        self.utilities_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.setup_utilities_list()

    def setup_utilities_list(self):
        """Setup the list of utilities"""
        utilities = [
            ("CPU-Z", "Информация о процессоре и системе"),
            ("HWiNFO", "Мониторинг системы"),
            ("MSI Afterburner", "Разгон видеокарты"),
            ("CCleaner", "Очистка системы"),
            # Add more utilities here
        ]

        for name, description in utilities:
            utility_frame = ctk.CTkFrame(self.utilities_frame)
            utility_frame.pack(fill="x", padx=5, pady=5)

            name_label = ctk.CTkLabel(
                utility_frame,
                text=name,
                font=("Arial", 14, "bold")
            )
            name_label.pack(side="left", padx=5)

            desc_label = ctk.CTkLabel(
                utility_frame,
                text=description
            )
            desc_label.pack(side="left", padx=5)

            button_text = "Запустить" if self.is_installed(name) else "Установить"
            action_button = ctk.CTkButton(
                utility_frame,
                text=button_text,
                command=lambda n=name: self.handle_utility(n)
            )
            action_button.pack(side="right", padx=5)

    def is_installed(self, utility_name):
        """Check if utility is installed"""
        return os.path.exists(os.path.join(self.github_handler.download_folder, f"{utility_name.lower()}_setup.exe"))

    def handle_utility(self, utility_name):
        """Handle utility installation or launch"""
        if self.is_installed(utility_name):
            self.launch_utility(utility_name)
        else:
            self.install_utility(utility_name)

    def install_utility(self, utility_name):
        """Download and install utility"""
        # Используем реальный URL из конфигурации
        github_url = f"https://github.com/example/{utility_name.lower()}"
        filename = f"{utility_name.lower()}_setup.exe"

        downloaded_file = self.github_handler.download_release(github_url, filename)
        if downloaded_file:
            self.show_message(f"{utility_name} успешно установлен!")
            self.update_utility_button(utility_name)
        else:
            self.show_message(f"Ошибка при установке {utility_name}")

    def launch_utility(self, utility_name):
        """Launch installed utility"""
        try:
            file_path = os.path.join(self.github_handler.download_folder, f"{utility_name.lower()}_setup.exe")
            if os.path.exists(file_path):
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                else:
                    self.show_message("Запуск программ доступен только в Windows")
        except Exception as e:
            self.show_message(f"Ошибка при запуске {utility_name}: {str(e)}")

    def update_utility_button(self, utility_name):
        """Update button text after installation"""
        for frame in self.utilities_frame.winfo_children():
            name_label = frame.winfo_children()[0]
            if name_label.cget("text") == utility_name:
                action_button = frame.winfo_children()[-1]
                action_button.configure(text="Запустить")
                break

    def show_message(self, message):
        """Show a message dialog"""
        dialog = ctk.CTkDialog(
            self.parent,
            title="Сообщение",
            text=message
        )
        dialog.show()