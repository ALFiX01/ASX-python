import os
import sys
import ctypes
import platform
import tkinter as tk
import json

try:
    import customtkinter as ctk
except ImportError:
    print("Error: CustomTkinter not found. Please install it using: pip install customtkinter")
    sys.exit(1)

from gui.tab_tweaks import TweaksTab
from gui.tab_programs import ProgramsTab
from gui.tab_utilities import UtilitiesTab
from gui.tab_WebResources import WebResourcesTab
from gui.tab_information import InformationTab
from gui.tab_settings import SettingsTab

from config import APP_VERSION
from gui.tab_information import InformationTab


def is_admin():
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin()
        return True
    except Exception:
        return False


class DynamicStatusBar(ctk.CTkFrame):
    """
    Расширенный динамический статус-бар с анимацией «печати».
    Высота блока уменьшена до 25 пикселей.
    При вызове update_text() сообщение печатается по одному символу,
    затем через заданное время оно исчезает (анимация удаления символов) и
    заменяется дефолтным сообщением.
    При клике по статус-бару анимация останавливается и отображается стандартное сообщение.
    """
    def __init__(self, master, default_text="", height=25, **kwargs):
        super().__init__(master, height=height, **kwargs)
        self.default_text = default_text
        # Используем немного меньший шрифт для уменьшенного блока
        self.label = ctk.CTkLabel(self, text=self.default_text, font=("Bahnschrift", 12))
        self.label.pack(fill="both", expand=True, padx=5, pady=3)

        # Параметры анимации
        self.typing_speed = 17   # интервал при печати символов (мс)
        self.deleting_speed = 15 # интервал при удалении символов (мс)
        self.animation_after_id = None
        self.target_text = ""
        self.current_text = ""

        # По клику сбрасываем статус-бар до стандартного сообщения
        self.label.bind("<Button-1>", lambda e: self.reset_text_immediate())

    def reset_text_immediate(self):
        """Мгновенно сбрасывает анимацию и устанавливает стандартный текст."""
        if self.animation_after_id:
            self.after_cancel(self.animation_after_id)
            self.animation_after_id = None
        self.label.configure(text=self.default_text)

    def update_text(self, new_text, duration=3000):
        """
        Запускает анимацию печати нового сообщения.
        :param new_text: новое сообщение для отображения.
        :param duration: время (в мс) показа сообщения после полного отображения.
        """
        if self.animation_after_id:
            self.after_cancel(self.animation_after_id)
        self.target_text = new_text
        self.current_text = ""
        self.label.configure(text="")
        self._animate_typing(duration)

    def _animate_typing(self, duration):
        """Анимирует появление текста по одному символу."""
        if len(self.current_text) < len(self.target_text):
            self.current_text += self.target_text[len(self.current_text)]
            self.label.configure(text=self.current_text)
            self.animation_after_id = self.after(self.typing_speed, lambda: self._animate_typing(duration))
        else:
            # После полной печати ждем указанное время, затем запускаем анимацию удаления
            self.animation_after_id = self.after(duration, self._animate_deleting)

    def _animate_deleting(self):
        """Анимирует удаление символов из сообщения (эффект обратной печати)."""
        if len(self.current_text) > 0:
            self.current_text = self.current_text[:-1]
            self.label.configure(text=self.current_text)
            self.animation_after_id = self.after(self.deleting_speed, self._animate_deleting)
        else:
            self._animate_typing_default()

    def _animate_typing_default(self):
        """Анимирует появление стандартного сообщения."""
        self.target_text = self.default_text
        self.current_text = ""
        self.label.configure(text="")
        self.animation_after_id = self.after(self.typing_speed, self._animate_typing_default_inner)

    def _animate_typing_default_inner(self):
        if len(self.current_text) < len(self.target_text):
            self.current_text += self.target_text[len(self.current_text)]
            self.label.configure(text=self.current_text)
            self.animation_after_id = self.after(self.typing_speed, self._animate_typing_default_inner)
        else:
            self.animation_after_id = None


class ASXHub(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"ASX Hub v{APP_VERSION}")
        self.geometry("1050x800")
        self.minsize(1050, 750)

        self.load_and_apply_settings()  # Загрузить и применить настройки

        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabview = ctk.CTkTabview(self.main_container)
        self.tabview.pack(fill="both", expand=True)

        self.tab_tweaks = self.tabview.add("Твики")
        self.tab_programs = self.tabview.add("Программы")
        self.tab_utilities = self.tabview.add("Утилиты")
        self.tab_web = self.tabview.add("Веб-ресурсы")
        self.tab_info = self.tabview.add("Информация")
        self.tab_settings = self.tabview.add("Настройка")

        self.tweaks_tab = TweaksTab(self.tab_tweaks)
        self.programs_tab = ProgramsTab(self.tab_programs)
        self.utilities_tab = UtilitiesTab(self.tab_utilities)
        self.web_resources_tab = WebResourcesTab(self.tab_web)
        self.information_tab = InformationTab(self.tab_info)
        self.settings_tab = SettingsTab(self.tab_settings)

        # Создаем динамический статус-бар
        default_status = f"ASX Hub v{APP_VERSION} | {'Администратор' if is_admin() else 'Обычный пользователь'}"
        self.dynamic_status = DynamicStatusBar(self.main_container, default_text=default_status, height=25)
        self.dynamic_status.pack(fill="x", pady=(5, 0))

        # Пример: показываем приветственное сообщение при запуске
        self.dynamic_status.update_text("Добро пожаловать в ASX Hub!", duration=3000)

        # Пример использования: при применении твика можно вызвать:
        # self.dynamic_status.update_text("Применяется твик XYZ...", duration=2000)

    def load_and_apply_settings(self):
        """Загружает настройки и применяет их, обрабатывая режим 'System' корректно."""
        settings_file = "settings.json"
        try:
            with open(settings_file, "r") as f:
                settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            settings = {
                "theme": "blue",
                "appearance_mode": "Light"  # Значение по умолчанию
            }
            try:
                with open(settings_file, "w") as f:
                    json.dump(settings, f, indent=4)
            except Exception as e:
                print(f"Error creating default settings file: {e}")

        # Обработка режима 'System'
        if settings.get("appearance_mode", "Light") == "System":
            try:
                import darkdetect
                system_mode = "Dark" if darkdetect.isDark() else "Light"
            except ImportError:
                system_mode = "Light"
            ctk.set_appearance_mode(system_mode)
        else:
            ctk.set_appearance_mode(settings.get("appearance_mode", "Light"))

        ctk.set_default_color_theme(settings.get("theme", "blue"))


def main():
    if platform.system() == "Windows" and not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

    app = ASXHub()
    app.mainloop()


if __name__ == "__main__":
    main()
