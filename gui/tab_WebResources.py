import os
import tkinter as tk
try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    import sys
    sys.exit(1)
from tkinter import messagebox
import webbrowser  # Import for opening web browser

class WebResourcesTab:
    def __init__(self, parent):
        self.parent = parent

        # === Web Resources List Frame (Улучшенный стиль) ===
        self.web_resources_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent" # Прозрачный фон для интеграции
        )
        self.web_resources_frame.pack(fill="both", expand=True, padx=10, pady=10) # Увеличены отступы

        self.setup_web_resources_list()

    def setup_web_resources_list(self):
        """Setup the list of web resources"""
        web_resources = [
            ("Google", "Поисковая система", "https://www.google.com"),
            ("YouTube", "Видеохостинг", "https://www.youtube.com"),
            ("GitHub", "Платформа для разработчиков", "https://github.com"),
            ("Stack Overflow", "Q&A для программистов", "https://stackoverflow.com"),
            ("Reddit", "Социальная сеть и форум", "https://www.reddit.com"),
            # Add more web resources here
        ]

        for name, description, url in web_resources:
            # === Web Resource Frame (Карточка веб-ресурса) ===
            web_resource_frame = ctk.CTkFrame(
                self.web_resources_frame,
                fg_color=("gray86", "gray17"), # Светлый фон в светлой теме, темный в темной
                corner_radius=10,
                border_width=0 # Убираем границу, фон карточки и так выделяет
            )
            web_resource_frame.pack(fill="x", padx=10, pady=5)
            web_resource_frame.bind("<Enter>", lambda event, frame=web_resource_frame: self.on_resource_hover(event, frame)) # Hover effect
            web_resource_frame.bind("<Leave>", lambda event, frame=web_resource_frame: self.on_resource_leave(event, frame)) # Hover effect

            # === Content Frame (Внутренний фрейм для контента) ===
            content_frame = ctk.CTkFrame(
                web_resource_frame,
                fg_color="transparent"
            )
            content_frame.pack(fill="x", padx=15, pady=15) # Увеличены внутренние отступы

            # === Icon Label (Иконка веб-ресурса - placeholder) ===
            icon_label = ctk.CTkLabel(
                content_frame,
                text="🌐", # Placeholder иконка - можно заменить на изображения
                font=("Arial", 30), # Увеличен размер иконки
                text_color=("gray50", "gray70") # Более блеклый цвет иконки
            )
            icon_label.pack(side="left", padx=(0, 15)) # Увеличен отступ справа от иконки

            # === Text Frame (Фрейм для текста - название и описание) ===
            text_frame = ctk.CTkFrame(
                content_frame,
                fg_color="transparent"
            )
            text_frame.pack(side="left", fill="x", expand=True)

            name_label = ctk.CTkLabel(
                text_frame,
                text=name,
                font=("Arial", 15, "bold") # Чуть больше размер названия
            )
            name_label.pack(anchor="w")

            desc_label = ctk.CTkLabel(
                text_frame,
                text=description,
                font=("Arial", 12),
                text_color=("gray50", "gray60") # Блеклый цвет описания для обеих тем
            )
            desc_label.pack(anchor="w")

            # === Open Button (Кнопка "Открыть") ===
            open_button = ctk.CTkButton(
                content_frame,
                text="Открыть",
                command=lambda u=url: self.open_web_resource(u),
                width=100,
                height=32,
                corner_radius=8 # Скругление углов кнопки
            )
            open_button.pack(side="right", padx=5)

    def open_web_resource(self, url):
        """Open web resource in default browser"""
        webbrowser.open_new_tab(url)

    def show_message(self, message):
        """Show a message dialog"""
        messagebox.showinfo(
            title="Сообщение",
            message=message
        )

    def on_resource_hover(self, event, frame):
        """Обработчик наведения мыши на карточку веб-ресурса"""
        frame.configure(border_width=2, border_color=("#56a6db", "#56a6db")) # Выделение рамкой при наведении

    def on_resource_leave(self, event, frame):
        """Обработчик ухода мыши с карточки веб-ресурса"""
        frame.configure(border_width=0, border_color=("gray70", "gray30")) # Возврат к обычному виду

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Web Resources Tab Example")
    app.geometry("800x700")

    web_resources_tab = WebResourcesTab(app)

    app.mainloop()