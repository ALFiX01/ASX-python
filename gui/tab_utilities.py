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
            # Create container frame with border
            utility_frame = ctk.CTkFrame(
                self.utilities_frame,
                fg_color="transparent",
                border_width=2,
                border_color=("gray70", "gray30"),
                corner_radius=10
            )
            utility_frame.pack(fill="x", padx=10, pady=5)

            # Create inner frame for content
            content_frame = ctk.CTkFrame(
                utility_frame,
                fg_color="transparent"
            )
            content_frame.pack(fill="x", padx=10, pady=10)

            # Utility icon placeholder
            icon_label = ctk.CTkLabel(
                content_frame,
                text="🔧",
                font=("Arial", 24)
            )
            icon_label.pack(side="left", padx=(5, 10))

            # Text information frame
            text_frame = ctk.CTkFrame(
                content_frame,
                fg_color="transparent"
            )
            text_frame.pack(side="left", fill="x", expand=True)

            name_label = ctk.CTkLabel(
                text_frame,
                text=name,
                font=("Arial", 14, "bold")
            )
            name_label.pack(anchor="w")

            desc_label = ctk.CTkLabel(
                text_frame,
                text=description,
                font=("Arial", 12)
            )
            desc_label.pack(anchor="w")

            # Action button
            button_text = "Запустить" if self.is_installed(name) else "Установить"
            action_button = ctk.CTkButton(
                content_frame,
                text=button_text,
                command=lambda n=name: self.handle_utility(n),
                width=100,
                height=32
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
            content_frame = frame.winfo_children()[0]  # Get the content frame
            text_frame = content_frame.winfo_children()[2]  # Get the text frame
            name_label = text_frame.winfo_children()[0]  # Get the name label

            if name_label.cget("text") == utility_name:
                action_button = content_frame.winfo_children()[-1]  # Get the action button
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