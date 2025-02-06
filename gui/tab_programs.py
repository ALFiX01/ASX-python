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
            placeholder_text="Поиск программ...",
            height=35
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
            # Create container frame with border
            program_frame = ctk.CTkFrame(
                self.programs_frame,
                fg_color="transparent",
                border_width=2,
                border_color=("gray70", "gray30"),
                corner_radius=10
            )
            program_frame.pack(fill="x", padx=10, pady=5)

            # Create inner frame for content
            content_frame = ctk.CTkFrame(
                program_frame,
                fg_color="transparent"
            )
            content_frame.pack(fill="x", padx=10, pady=10)

            # Program icon placeholder
            icon_label = ctk.CTkLabel(
                content_frame,
                text="📦",
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

            # Download button
            download_button = ctk.CTkButton(
                content_frame,
                text="Загрузить",
                command=lambda n=name: self.download_program(n),
                width=100,
                height=32
            )
            download_button.pack(side="right", padx=5)

    def search_programs(self, event):
        """Filter programs based on search text"""
        search_text = self.search_entry.get().lower()

        for program_frame in self.programs_frame.winfo_children():
            # Since we changed the structure, we need to navigate to the name label
            content_frame = program_frame.winfo_children()[0]  # Get the content frame
            text_frame = content_frame.winfo_children()[2]    # Get the text frame
            name_label = text_frame.winfo_children()[0]       # Get the name label

            if search_text in name_label.cget("text").lower():
                program_frame.pack(fill="x", padx=10, pady=5)
            else:
                program_frame.pack_forget()

    def download_program(self, program_name):
        """Download program from GitHub"""
        github_url = f"https://github.com/example/{program_name.lower()}"
        filename = f"{program_name.lower()}_setup.exe"

        downloaded_file = self.github_handler.download_release(github_url, filename)
        if downloaded_file:
            self.show_message(f"{program_name} успешно загружен!")
        else:
            self.show_message(f"Ошибка при загрузке {program_name}")

    def show_message(self, message):
        """Show a message dialog"""
        dialog = ctk.CTkDialog(
            self.parent,
            title="Сообщение",
            text=message
        )
        dialog.show()