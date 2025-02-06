import os
import tkinter as tk
try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    import sys
    sys.exit(1)

from utils.github_handler import GitHubHandler

class ProgramsTab:
    def __init__(self, parent):
        self.parent = parent
        self.github_handler = GitHubHandler()

        # Create search frame
        self.search_frame = ctk.CTkFrame(self.parent)
        self.search_frame.pack(fill="x", padx=10, pady=5)

        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Поиск программ..."
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_programs)

        # Create programs list frame
        self.programs_frame = ctk.CTkScrollableFrame(self.parent)
        self.programs_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.setup_programs_list()

    def setup_programs_list(self):
        """Setup the list of available programs"""
        programs = [
            ("Chrome", "Веб-браузер от Google"),
            ("Firefox", "Веб-браузер от Mozilla"),
            ("7-Zip", "Архиватор файлов"),
            ("VLC", "Медиаплеер"),
            # Add more programs here
        ]

        for name, description in programs:
            program_frame = ctk.CTkFrame(self.programs_frame)
            program_frame.pack(fill="x", padx=5, pady=5)

            name_label = ctk.CTkLabel(
                program_frame,
                text=name,
                font=("Arial", 14, "bold")
            )
            name_label.pack(side="left", padx=5)

            desc_label = ctk.CTkLabel(
                program_frame,
                text=description
            )
            desc_label.pack(side="left", padx=5)

            download_button = ctk.CTkButton(
                program_frame,
                text="Загрузить",
                command=lambda n=name: self.download_program(n)
            )
            download_button.pack(side="right", padx=5)

    def search_programs(self, event):
        """Filter programs based on search text"""
        search_text = self.search_entry.get().lower()

        for program_frame in self.programs_frame.winfo_children():
            name_label = program_frame.winfo_children()[0]
            if search_text in name_label.cget("text").lower():
                program_frame.pack(fill="x", padx=5, pady=5)
            else:
                program_frame.pack_forget()

    def download_program(self, program_name):
        """Download program from GitHub"""
        # This would use the actual GitHub URL from config
        github_url = f"https://github.com/example/{program_name.lower()}"
        filename = f"{program_name.lower()}_setup.exe"

        downloaded_file = self.github_handler.download_release(github_url, filename)
        if downloaded_file:
            # Show success message
            self.show_message(f"{program_name} успешно загружен!")
        else:
            # Show error message
            self.show_message(f"Ошибка при загрузке {program_name}")

    def show_message(self, message):
        """Show a message dialog"""
        dialog = ctk.CTkDialog(
            self.parent,
            title="Сообщение",
            text=message
        )
        dialog.show()