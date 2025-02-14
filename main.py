import os
import sys
import ctypes
import platform
import json
import logging
import tkinter as tk

try:
    import customtkinter as ctk
except ImportError:
    logging.error("CustomTkinter not found. Please install it using: pip install customtkinter")
    sys.exit(1)

from gui.tab_tweaks import TweaksTab
from gui.tab_programs import ProgramsTab
from gui.tab_utilities import UtilitiesTab
from gui.tab_drivers import DriverTab
from gui.tab_WebResources import WebResourcesTab
from gui.tab_information import InformationTab
from gui.tab_settings import SettingsTab

from config import APP_VERSION

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def is_admin():
    """Проверяет, запущено ли приложение с правами администратора."""
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin()
        return True
    except Exception as e:
        logging.error(f"Error checking admin status: {e}")
        return False


class DynamicStatusBar(ctk.CTkFrame):
    """
    Динамический статус-бар с анимацией печати, плавым переходом цвета текста,
    очередью сообщений, обработкой дублирования и приоритетом для ошибок.
    """

    def __init__(self, master, default_text="", height=25,
                 typing_speed=14, deleting_speed=11,
                 fade_steps=20, icon_animation_steps=5, **kwargs):
        super().__init__(master, height=height, **kwargs)
        self.default_text = default_text
        self.typing_speed = typing_speed
        self.deleting_speed = deleting_speed
        self.fade_steps = fade_steps
        self.icon_animation_steps = icon_animation_steps

        # Определяем пары цветов для плавной анимации:
        # Первый элемент – начальный (светлый), второй – конечный (тёмный)
        self.colors = {
            "info": ("#a3d4fc", "#4691ce"),
            "success": ("#a8e6cf", "#27ae60"),
            "warning": ("#ffda77", "#f39c12"),
            "error": ("#ff9a9a", "#c0392b"),
            "default": ("#a3d4fc", "#4691ce")
        }

        self.icons = {
            "info": "💡",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "default": "📝"
        }

        self.message_queue = []
        self.is_animating = False

        self.animation_after_id = None
        self.color_after_id = None
        self.icon_after_id = None

        self.target_text = default_text
        self.current_text = ""
        self.current_message_type = "default"

        self._start_color = self.colors["default"][0]
        self._end_color = self.colors["default"][1]

        # Создаём контейнер для иконки и текста
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=2)

        self.icon_label = ctk.CTkLabel(
            self.content_frame,
            text=self.icons.get("default", "📝"),
            font=("Segoe UI Emoji", 14),
            width=20
        )
        self.icon_label.pack(side="left", padx=(2, 5))

        self.label = ctk.CTkLabel(
            self.content_frame,
            text=self.default_text,
            font=("Bahnschrift", 14),
            anchor="w"
        )
        self.label.pack(side="left", fill="x", expand=True)

        # Привязка клика для мгновенного сброса анимации
        self.label.bind("<Button-1>", self.reset_text_immediate)
        self.icon_label.bind("<Button-1>", self.reset_text_immediate)

        self.set_text_immediately(self.default_text, "default")

    def update_text(self, new_text, message_type="info", duration=3000,
                    animate=True, immediate=False, animate_icon=True):
        """
        Обновляет статус с заданным сообщением.
        Если сообщение совпадает с текущим или уже в очереди – ничего не меняется.
        Для типа "error" сразу отменяются текущие анимации.
        """
        if new_text == self.target_text and message_type == self.current_message_type:
            return

        if any(msg[0] == new_text and msg[1] == message_type for msg in self.message_queue):
            return

        if message_type == "error":
            self._cancel_animations()
            self._start_message(new_text, message_type, duration, animate, animate_icon)
            return

        if immediate or not animate:
            self._update_immediate(new_text, message_type, duration, animate_icon)
        else:
            if self.is_animating:
                self.message_queue.append((new_text, message_type, duration, animate, animate_icon))
            else:
                self._start_message(new_text, message_type, duration, animate, animate_icon)

    def _update_immediate(self, new_text, message_type, duration, animate_icon):
        self._cancel_animations()
        self.target_text = new_text
        self.current_message_type = message_type

        icon = self.icons.get(message_type, self.icons["default"])
        self.icon_label.configure(text=icon)
        if animate_icon:
            self._animate_icon(message_type)

        colors = self.colors.get(message_type, self.colors["default"])
        self.label.configure(text=new_text, text_color=colors[1])
        self.after(duration, self.reset_text_immediate)

    def _cancel_animations(self):
        """Отменяет все запланированные анимации и очищает очередь сообщений."""
        if self.animation_after_id:
            self.after_cancel(self.animation_after_id)
            self.animation_after_id = None
        if self.color_after_id:
            self.after_cancel(self.color_after_id)
            self.color_after_id = None
        if self.icon_after_id:
            self.after_cancel(self.icon_after_id)
            self.icon_after_id = None
        self.message_queue.clear()
        self.is_animating = False

    def _start_message(self, new_text, message_type, duration, animate, animate_icon):
        self.is_animating = True
        self.target_text = new_text
        self.current_text = ""
        self.duration = duration
        self.current_message_type = message_type

        colors = self.colors.get(message_type, self.colors["default"])
        self._start_color, self._end_color = colors

        icon = self.icons.get(message_type, self.icons["default"])
        self.icon_label.configure(text=icon)
        if animate_icon:
            self._animate_icon(message_type)
        self._animate_typing()

    def _animate_typing(self):
        try:
            if len(self.current_text) < len(self.target_text):
                self.current_text += self.target_text[len(self.current_text)]
                self.label.configure(text=self.current_text)
                self.animation_after_id = self.after(self.typing_speed, self._animate_typing)
            else:
                self._animate_color_transition(step=0)
                self.animation_after_id = self.after(self.duration, self._animate_deleting)
        except Exception as e:
            logging.error(f"Error in typing animation: {e}")
            self.set_text_immediately(self.target_text, self.current_message_type)

    def _animate_color_transition(self, step):
        if step <= self.fade_steps:
            progress = self._ease_in_out(step / self.fade_steps)
            try:
                new_color = self._interpolate_color(self._start_color, self._end_color, progress)
            except Exception as e:
                logging.error(f"Error in color interpolation: {e}")
                new_color = self._end_color
            self.label.configure(text_color=new_color)
            self.label.update_idletasks()
            self.color_after_id = self.after(20, lambda: self._animate_color_transition(step + 1))
        else:
            self.label.configure(text_color=self._end_color)

    def _animate_deleting(self):
        try:
            if len(self.current_text) > 0:
                self.current_text = self.current_text[:-1]
                self.label.configure(text=self.current_text)
                self.animation_after_id = self.after(self.deleting_speed, self._animate_deleting)
            else:
                self._finish_message()
        except Exception as e:
            logging.error(f"Error in deleting animation: {e}")
            self._finish_message()

    def _finish_message(self):
        if self.message_queue:
            next_message = self.message_queue.pop(0)
            new_text, message_type, duration, animate, animate_icon = next_message
            self._start_message(new_text, message_type, duration, animate, animate_icon)
        else:
            self._animate_typing_default()

    def _animate_typing_default(self):
        default_colors = self.colors.get("default", ("#a3d4fc", "#4691ce"))
        self._start_color, self._end_color = default_colors
        self.label.configure(text_color=self.colors["default"][1])
        self.target_text = self.default_text
        self.current_text = ""
        self.icon_label.configure(text=self.icons.get("default", "📝"))
        self._animate_typing_default_inner()

    def _animate_typing_default_inner(self):
        try:
            if len(self.current_text) < len(self.target_text):
                self.current_text += self.target_text[len(self.current_text)]
                self.label.configure(text=self.current_text)
                self.animation_after_id = self.after(self.typing_speed, self._animate_typing_default_inner)
            else:
                self.is_animating = False
        except Exception as e:
            logging.error(f"Error in default typing animation: {e}")
            self.set_text_immediately(self.default_text, "default")
            self.is_animating = False

    def _animate_icon(self, message_type):
        try:
            if message_type == "error":
                self._animate_icon_shake()
            else:
                self._animate_icon_bounce(initial_size=10, target_size=14, step=0)
        except Exception as e:
            logging.error(f"Error in icon animation: {e}")
            self.icon_label.configure(font=("Segoe UI Emoji", 14))

    def _animate_icon_bounce(self, initial_size, target_size, step, steps=None):
        steps = steps or self.icon_animation_steps
        try:
            if step <= steps:
                progress = self._ease_in_out(step / steps)
                new_size = int(initial_size + (target_size - initial_size) * progress)
                self.icon_label.configure(font=("Segoe UI Emoji", new_size))
                self.icon_after_id = self.after(20,
                                                lambda: self._animate_icon_bounce(initial_size, target_size, step + 1,
                                                                                  steps))
            else:
                self.icon_label.configure(font=("Segoe UI Emoji", target_size))
        except Exception as e:
            logging.error(f"Error in icon bounce animation: {e}")
            self.icon_label.configure(font=("Segoe UI Emoji", 14))

    def _animate_icon_shake(self, shake_count=0, max_shake=6):
        icon = self.icons.get("error", "❌")
        try:
            if shake_count < max_shake:
                prefix = "  " if shake_count % 2 == 0 else " "
                self.icon_label.configure(text=prefix + icon)
                self.icon_after_id = self.after(50, lambda: self._animate_icon_shake(shake_count + 1, max_shake))
            else:
                self.icon_label.configure(text=icon)
        except Exception as e:
            logging.error(f"Error in icon shake animation: {e}")
            self.icon_label.configure(text=icon)

    @staticmethod
    def _ease_in_out(t):
        """Функция сглаживания для анимаций."""
        return t * t * (3 - 2 * t)

    def _interpolate_color(self, start_hex, end_hex, progress):
        """Интерполирует между двумя HEX-цветами по заданному прогрессу."""
        try:
            r1, g1, b1 = self._hex_to_rgb(start_hex)
            r2, g2, b2 = self._hex_to_rgb(end_hex)
            r = int(r1 + (r2 - r1) * progress)
            g = int(g1 + (g2 - g1) * progress)
            b = int(b1 + (b2 - b1) * progress)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception as e:
            logging.error(f"Error in color interpolation: {e}")
            return end_hex

    @staticmethod
    def _hex_to_rgb(hex_color):
        """Преобразует HEX-цвет в кортеж (R, G, B)."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c * 2 for c in hex_color])
        try:
            return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        except (ValueError, IndexError):
            return (128, 128, 128)

    def reset_text_immediate(self, event=None):
        """Мгновенно сбрасывает все анимации и возвращает статус к стандартному виду."""
        self._cancel_animations()
        self.set_text_immediately(self.default_text, "default")

    def set_text_immediately(self, text, message_type):
        """
        Устанавливает текст и иконку без анимации и сохраняет текущие значения.
        """
        self.target_text = text
        self.current_message_type = message_type
        colors = self.colors.get(message_type, self.colors["default"])
        self.label.configure(text=text, text_color=colors[1])
        self.icon_label.configure(text=self.icons.get(message_type, self.icons["default"]))


# Глобальный экземпляр статус-бара
_status_bar_instance = None


def set_status_bar_instance(instance):
    """Устанавливает глобальный экземпляр статус-бара."""
    global _status_bar_instance
    _status_bar_instance = instance


def update_status(message, message_type="info", duration=3000,
                  animate=True, immediate=False, animate_icon=True):
    """Обновляет статус из других файлов."""
    if _status_bar_instance is not None:
        _status_bar_instance.update_text(message, message_type, duration, animate, immediate, animate_icon)


class ASXHub(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"ASX Hub v{APP_VERSION}")
        self.geometry("1050x800")
        self.minsize(1050, 800)

        self.load_and_apply_settings()  # Загружаем и применяем настройки

        # Основной контейнер
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Создаём TabView для категорий
        self.tabview = ctk.CTkTabview(self.main_container)
        self.tabview.pack(fill="both", expand=True)

        # Добавляем вкладки
        self.tab_tweaks = self.tabview.add("Твики")
        self.tab_programs = self.tabview.add("Программы")
        self.tab_utilities = self.tabview.add("Утилиты")
        self.tab_drivers = self.tabview.add("Драйверы")
        self.tab_web = self.tabview.add("Веб-ресурсы")
        self.tab_info = self.tabview.add("Информация")
        self.tab_settings = self.tabview.add("Настройка")

        # Настраиваем панель переключения вкладок:
        accent_color = self.settings.get("accent_color", "#1f6aa5")
        panel_bg_color = "#444444"      # фон панели
        button_bg_color = "#444444"     # фон невыбранной кнопки
        button_hover_color = "#666666"  # фон при наведении
        text_color = "white"
        border_color = "#222222"

        try:
            self.tabview._segmented_button.configure(
                fg_color=panel_bg_color,
                button_color=button_bg_color,
                button_hover_color=button_hover_color,
                text_color=text_color,
                selected_button_color=accent_color,
                selected_hover_color=accent_color,
                selected_text_color=text_color,
                corner_radius=8,
                border_width=1,
                border_color=border_color,
                text_font=("Helvetica", 12, "bold")
            )
            self.tabview._segmented_button.update_idletasks()
        except Exception as e:
            logging.error(f"Error applying accent color to tabview: {e}")

        # Инициализируем содержимое вкладок
        self.tweaks_tab = TweaksTab(self.tab_tweaks)
        self.programs_tab = ProgramsTab(self.tab_programs)
        self.utilities_tab = UtilitiesTab(self.tab_utilities)
        self.driver_tab = DriverTab(self.tab_drivers, self.dynamic_status)  # Pass the status bar here
        self.web_resources_tab = WebResourcesTab(self.tab_web)
        self.information_tab = InformationTab(self.tab_info)
        self.settings_tab = SettingsTab(self.tab_settings)

        default_status = f"ASX Hub v{APP_VERSION} | {'Администратор' if is_admin() else 'Обычный пользователь'}"
        self.dynamic_status = DynamicStatusBar(self.main_container, default_text=default_status, height=25)
        self.dynamic_status.pack(fill="x", pady=(6, 0))

        set_status_bar_instance(self.dynamic_status)
        self.dynamic_status.update_text("Добро пожаловать в ASX Hub!", duration=3000)

    def load_and_apply_settings(self):
        """Загружает настройки и применяет их, корректно обрабатывая режим 'System'."""
        settings = self.load_settings()
        self.settings = settings
        self.apply_settings(settings)

    def load_settings(self):
        """Загружает настройки из файла."""
        settings_file = "settings.json"
        try:
            with open(settings_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logging.warning("Settings file not found or invalid. Creating default settings.")
            return self.create_default_settings()

    def create_default_settings(self):
        """Создает файл настроек с значениями по умолчанию."""
        default_settings = {
            "theme": "blue",
            "appearance_mode": "Light",
            "accent_color": "#1f6aa5"
        }
        try:
            with open("settings.json", "w") as f:
                json.dump(default_settings, f, indent=4)
        except Exception as e:
            logging.error(f"Error creating default settings file: {e}")
        return default_settings

    def apply_settings(self, settings):
        """Применяет настройки к приложению."""
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

    def save_settings(self, settings):
        """Сохраняет настройки в файл."""
        try:
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=4)
            logging.info("Settings saved successfully.")
        except Exception as e:
            logging.error(f"Error saving settings: {e}")


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
