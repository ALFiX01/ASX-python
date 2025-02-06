import os
import tkinter as tk
try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    import sys
    sys.exit(1)
from tkinter import messagebox

from utils.github_handler import GitHubHandler

class UtilitiesTab:
    def __init__(self, parent):
        self.parent = parent
        self.github_handler = GitHubHandler()

        # === Utilities List Frame (Улучшенный стиль) ===
        self.utilities_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent" # Прозрачный фон для интеграции
        )
        self.utilities_frame.pack(fill="both", expand=True, padx=10, pady=10) # Увеличены отступы

        self.setup_utilities_list()

    def setup_utilities_list(self):
        """Настройка списка утилит"""
        utilities = [
            ("CPU-Z", "Информация о процессоре и системе"),
            ("HWiNFO", "Мониторинг системы"),
            ("MSI Afterburner", "Разгон видеокарты"),
            ("CCleaner", "Очистка системы"),
            ("CrystalDiskInfo", "Мониторинг состояния жестких дисков"),
            ("MemTest64", "Тестирование оперативной памяти"),
            ("FurMark", "Тестирование видеокарты"),
            ("Rivatuner Statistics Server", "Отображение FPS и системной информации в играх"),
            # Добавьте больше утилит здесь
        ]

        for name, description in utilities:
            # === Utility Frame (Карточка утилиты) ===
            utility_frame = ctk.CTkFrame(
                self.utilities_frame,
                fg_color=("gray86", "gray17"), # Светлый фон в светлой теме, темный в темной
                corner_radius=10,
                border_width=0 # Убираем границу, фон карточки и так выделяет
            )
            utility_frame.pack(fill="x", padx=10, pady=5)
            utility_frame.bind("<Enter>", lambda event, frame=utility_frame: self.on_utility_hover(event, frame)) # Hover effect
            utility_frame.bind("<Leave>", lambda event, frame=utility_frame: self.on_utility_leave(event, frame)) # Hover effect

            # === Content Frame (Внутренний фрейм для контента) ===
            content_frame = ctk.CTkFrame(
                utility_frame,
                fg_color="transparent"
            )
            content_frame.pack(fill="x", padx=15, pady=15) # Увеличены внутренние отступы

            # === Icon Label (Иконка утилиты - placeholder) ===
            icon_label = ctk.CTkLabel(
                content_frame,
                text="🔧", # Placeholder иконка - можно заменить на изображения
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

            # === Action Button (Кнопка "Запустить" / "Установить") ===
            button_text = "Запустить" if self.is_installed(name) else "Установить"
            action_button = ctk.CTkButton(
                content_frame,
                text=button_text,
                command=lambda n=name: self.handle_utility(n),
                width=100,
                height=32,
                corner_radius=8 # Скругление углов кнопки
            )
            action_button.pack(side="right", padx=5)

    def is_installed(self, utility_name):
        """Проверка, установлена ли утилита (пример)"""
        # !!! ВНИМАНИЕ: Это пример проверки установки.  Реальная проверка может быть сложнее !!!
        # В реальной ситуации нужно проверять наличие исполняемых файлов утилиты, записи в реестре, и т.д.
        # Простая проверка по наличию файла setup.exe в папке загрузок - ненадежна для определения установки.
        return os.path.exists(os.path.join(self.github_handler.download_folder, f"{utility_name.lower()}_setup.exe"))

    def handle_utility(self, utility_name):
        """Обработка установки или запуска утилиты"""
        if self.is_installed(utility_name):
            self.launch_utility(utility_name)
        else:
            self.install_utility(utility_name)

    def install_utility(self, utility_name):
        """Загрузка и установка утилиты (пример)"""
        github_url = f"https://github.com/example/{utility_name.lower()}" # Замените на реальные URL
        filename = f"{utility_name.lower()}_setup.exe"

        downloaded_file = self.github_handler.download_release(github_url, filename)
        if downloaded_file:
            self.show_message(f"{utility_name} успешно установлена!")
            self.update_utility_button(utility_name)
        else:
            self.show_message(f"Ошибка при установке {utility_name}")

    def launch_utility(self, utility_name):
        """Запуск установленной утилиты (пример)"""
        try:
            file_path = os.path.join(self.github_handler.download_folder, f"{utility_name.lower()}_setup.exe") # !!! Запуск setup.exe - это только пример !!!
            if os.path.exists(file_path):
                if os.name == 'nt':  # Windows
                    os.startfile(file_path) # !!! В РЕАЛЬНОМ ПРИЛОЖЕНИИ ЗАПУСКАТЬ setup.exe НЕПРАВИЛЬНО !!!
                    # Нужно запускать исполняемый файл самой утилиты, который устанавливается в Program Files или другое место.
                    # Процесс запуска утилиты зависит от конкретной утилиты и способа ее установки.
                else:
                    self.show_message("Запуск программ доступен только в Windows")
        except Exception as e:
            self.show_message(f"Ошибка при запуске {utility_name}: {str(e)}")

    def update_utility_button(self, utility_name):
        """Обновление текста кнопки после установки"""
        for frame in self.utilities_frame.winfo_children():
            content_frame = frame.winfo_children()[0]
            text_frame = content_frame.winfo_children()[2]
            name_label = text_frame.winfo_children()[0]

            if name_label.cget("text") == utility_name:
                action_button = content_frame.winfo_children()[-1]
                action_button.configure(text="Запустить")
                break

    def show_message(self, message):
        """Отображение диалогового окна сообщения"""
        messagebox.showinfo(
            title="Сообщение",
            message=message
        )

    def on_utility_hover(self, event, frame):
        """Обработчик наведения мыши на карточку утилиты"""
        frame.configure(border_width=2, border_color=("#56a6db", "#56a6db")) # Выделение рамкой при наведении

    def on_utility_leave(self, event, frame):
        """Обработчик ухода мыши с карточки утилиты"""
        frame.configure(border_width=0, border_color=("gray70", "gray30")) # Возврат к обычному виду

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Utilities Tab Example")
    app.geometry("800x700")

    utilities_tab = UtilitiesTab(app)

    app.mainloop()